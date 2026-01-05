"""
Inventory management service
"""

from typing import List, Optional, Dict, Any
from datetime import date, timedelta
from decimal import Decimal
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.inventory import InventoryItem, ConsumptionLog
from app.models.user import User
from app.services.ai_service import AIService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for inventory management operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        ai_service: Optional[AIService] = None,
        notification_service: Optional[NotificationService] = None
    ):
        self.db = db
        self.ai_service = ai_service
        self.notification_service = notification_service
    
    async def get_expiring_items(
        self,
        household_id: str,
        days_ahead: int = 7
    ) -> List[InventoryItem]:
        """Get items expiring within specified days"""
        cutoff_date = date.today() + timedelta(days=days_ahead)
        
        result = await self.db.execute(
            select(InventoryItem).where(
                InventoryItem.household_id == household_id,
                InventoryItem.expiration_date.isnot(None),
                InventoryItem.expiration_date <= cutoff_date,
                InventoryItem.quantity > 0
            ).order_by(InventoryItem.expiration_date.asc())
        )
        
        return result.scalars().all()
    
    async def get_low_stock_items(
        self,
        household_id: str,
        threshold: float = 0.2
    ) -> List[Dict[str, Any]]:
        """Get items with low stock based on consumption patterns"""
        # This would analyze consumption patterns and identify items running low
        # For now, return items with quantity below a threshold
        
        result = await self.db.execute(
            select(InventoryItem).where(
                InventoryItem.household_id == household_id,
                InventoryItem.quantity < threshold
            )
        )
        
        items = result.scalars().all()
        return [
            {
                "item": item,
                "stock_level": float(item.quantity),
                "recommendation": "Restock recommended"
            }
            for item in items
        ]
    
    async def get_shopping_recommendations(
        self,
        household_id: str,
        meal_plan_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate shopping recommendations based on inventory and meal plans"""
        recommendations = []
        
        # Get expiring items that should be used
        expiring_items = await self.get_expiring_items(household_id, days_ahead=3)
        if expiring_items:
            recommendations.append({
                "type": "use_soon",
                "title": "Use These Items Soon",
                "items": [
                    {
                        "name": item.name,
                        "quantity": float(item.quantity),
                        "unit": item.unit,
                        "expires_in": (item.expiration_date - date.today()).days if item.expiration_date else None
                    }
                    for item in expiring_items[:5]  # Top 5
                ]
            })
        
        # Get low stock items
        low_stock = await self.get_low_stock_items(household_id)
        if low_stock:
            recommendations.append({
                "type": "restock",
                "title": "Running Low",
                "items": [
                    {
                        "name": item["item"].name,
                        "current_quantity": item["stock_level"],
                        "unit": item["item"].unit,
                        "suggested_quantity": max(1.0, item["stock_level"] * 3)
                    }
                    for item in low_stock[:5]
                ]
            })
        
        return recommendations
    
    async def forecast_waste(
        self,
        household_id: str,
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """Forecast potential food waste using AI"""
        if not self.ai_service:
            # Simple heuristic-based forecasting
            return await self._simple_waste_forecast(household_id, days_ahead)
        
        # AI-powered forecasting
        expiring_items = await self.get_expiring_items(household_id, days_ahead)
        consumption_history = await self._get_consumption_history(household_id, days=30)
        
        return await self.ai_service.forecast_waste(
            expiring_items,
            consumption_history,
            days_ahead
        )
    
    async def _simple_waste_forecast(
        self,
        household_id: str,
        days_ahead: int
    ) -> Dict[str, Any]:
        """Simple waste forecasting based on expiration dates"""
        expiring_items = await self.get_expiring_items(household_id, days_ahead)
        
        total_value = Decimal('0')
        items_at_risk = []
        
        for item in expiring_items:
            if item.purchase_price:
                item_value = item.purchase_price * (item.quantity / max(item.quantity, 1))
                total_value += item_value
                
                items_at_risk.append({
                    "id": str(item.id),
                    "name": item.name,
                    "quantity": float(item.quantity),
                    "unit": item.unit,
                    "value": float(item_value),
                    "expires_in": (item.expiration_date - date.today()).days if item.expiration_date else None,
                    "location": item.location
                })
        
        recommendations = []
        if items_at_risk:
            recommendations.append("Use items expiring within 3 days")
            recommendations.append("Plan meals around expiring ingredients")
            recommendations.append("Consider freezing items if not used soon")
        
        return {
            "household_id": household_id,
            "forecast_period_days": days_ahead,
            "total_items_at_risk": len(items_at_risk),
            "estimated_waste_value": total_value,
            "items_at_risk": items_at_risk,
            "recommendations": recommendations,
            "confidence_score": 0.7  # Heuristic-based
        }
    
    async def _get_consumption_history(
        self,
        household_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get consumption history for waste analysis"""
        from_date = date.today() - timedelta(days=days)
        
        result = await self.db.execute(
            select(ConsumptionLog, InventoryItem)
            .join(InventoryItem, ConsumptionLog.item_id == InventoryItem.id)
            .where(
                InventoryItem.household_id == household_id,
                ConsumptionLog.used_at >= from_date
            )
        )
        
        logs = result.all()
        
        return [
            {
                "item_name": item.name,
                "quantity_used": float(log.quantity_used),
                "waste_reason": log.waste_reason,
                "used_at": log.used_at.isoformat()
            }
            for log, item in logs
        ]
    
    async def add_item_from_barcode(
        self,
        barcode: str,
        household_id: str,
        user_id: str,
        location: str = "pantry"
    ) -> Optional[InventoryItem]:
        """Add item by scanning barcode"""
        from app.services.barcode_service import BarcodeService
        
        barcode_service = BarcodeService()
        product_info = await barcode_service.lookup_barcode(barcode)
        
        if not product_info:
            return None
        
        # Create inventory item from product info
        item = InventoryItem(
            household_id=household_id,
            added_by=user_id,
            barcode=barcode,
            name=product_info.get("product_name", f"Product {barcode}"),
            category=product_info.get("category", "general"),
            quantity=1,
            unit="piece",
            location=location,
            nutrition_data=product_info.get("nutrition_data")
        )
        
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        
        return item
    
    async def send_expiration_alerts(self, household_id: str):
        """Send alerts for items expiring soon"""
        if not self.notification_service:
            return
        
        expiring_items = await self.get_expiring_items(household_id, days_ahead=2)
        
        if expiring_items:
            message = f"You have {len(expiring_items)} items expiring soon!"
            await self.notification_service.send_household_notification(
                household_id,
                "Expiration Alert",
                message,
                "expiration_alert"
            )