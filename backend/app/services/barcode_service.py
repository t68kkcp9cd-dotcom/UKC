"""
Barcode lookup service for product information
Integrates with OpenFoodFacts and other barcode databases
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class BarcodeService:
    """Service for barcode lookups and product information"""
    
    def __init__(self):
        self.openfoodfacts_base_url = settings.OPENFOODFACTS_API_URL
        self.session = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                base_url=self.openfoodfacts_base_url,
                timeout=aiohttp.ClientTimeout(total=10)
            )
        return self.session
        
    async def lookup_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Lookup product information by barcode
        
        Args:
            barcode: Product barcode (EAN, UPC, etc.)
            
        Returns:
            Product information dictionary or None if not found
        """
        try:
            session = await self._get_session()
            
            # Try OpenFoodFacts API
            async with session.get(f"/product/{barcode}.json") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == 1:  # Product found
                        product = data.get("product", {})
                        
                        # Extract nutrition data
                        nutrition_data = {}
                        nutriments = product.get("nutriments", {})
                        
                        if nutriments:
                            nutrition_data = {
                                "calories": nutriments.get("energy-kcal_100g"),
                                "protein": nutriments.get("proteins_100g"),
                                "carbs": nutriments.get("carbohydrates_100g"),
                                "fat": nutriments.get("fat_100g"),
                                "fiber": nutriments.get("fiber_100g"),
                                "sodium": nutriments.get("sodium_100g")
                            }
                        
                        return {
                            "product_name": product.get("product_name", product.get("product_name_en", "")),
                            "brand": product.get("brands", ""),
                            "category": self._extract_category(product),
                            "image_url": product.get("image_front_url"),
                            "ingredients": product.get("ingredients_text", ""),
                            "nutrition_data": nutrition_data,
                            "allergens": product.get("allergens_tags", []),
                            "labels": product.get("labels_tags", []),
                            "source": "openfoodfacts"
                        }
                        
                logger.info(f"Product not found in OpenFoodFacts: {barcode}")
                
                # Try alternative sources or return basic info
                return await self._get_basic_product_info(barcode)
                
        except Exception as e:
            logger.error(f"Error looking up barcode {barcode}: {e}")
            return await self._get_basic_product_info(barcode)
            
    async def _get_basic_product_info(self, barcode: str) -> Dict[str, Any]:
        """Return basic product info when lookup fails"""
        return {
            "product_name": f"Product {barcode}",
            "brand": "Unknown",
            "category": "general",
            "image_url": None,
            "ingredients": "",
            "nutrition_data": {},
            "allergens": [],
            "labels": [],
            "source": "basic",
            "note": "Product information not available in database"
        }
        
    def _extract_category(self, product_data: Dict[str, Any]) -> str:
        """Extract category from product data"""
        # Try different category fields
        categories = product_data.get("categories", "")
        if categories:
            # Take the first category
            category_list = categories.split(",")
            if category_list:
                return category_list[0].strip().lower()
                
        # Try other fields
        category_tags = product_data.get("categories_tags", [])
        if category_tags:
            return category_tags[0].replace("en:", "")
            
        # Default categories based on product name
        product_name = product_data.get("product_name", "").lower()
        
        if any(word in product_name for word in ["milk", "cheese", "yogurt", "butter"]):
            return "dairy"
        elif any(word in product_name for word in ["chicken", "beef", "pork", "fish", "meat"]):
            return "meat"
        elif any(word in product_name for word in ["bread", "pasta", "rice", "cereal"]):
            return "grains"
        elif any(word in product_name for word in ["apple", "banana", "fruit", "vegetable", "salad"]):
            return "produce"
        elif any(word in product_name for word in ["frozen", "ice cream"]):
            return "frozen"
        else:
            return "general"
            
    async def batch_lookup_barcodes(self, barcodes: list[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Lookup multiple barcodes efficiently
        
        Args:
            barcodes: List of barcodes to lookup
            
        Returns:
            Dictionary mapping barcodes to product information
        """
        results = {}
        
        # Process in batches to avoid overwhelming the API
        batch_size = 5
        for i in range(0, len(barcodes), batch_size):
            batch = barcodes[i:i + batch_size]
            
            tasks = [self.lookup_barcode(barcode) for barcode in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for barcode, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error looking up {barcode}: {result}")
                    results[barcode] = None
                else:
                    results[barcode] = result
                    
            # Add small delay between batches to be respectful to the API
            if i + batch_size < len(barcodes):
                await asyncio.sleep(0.1)
                
        return results
        
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            
    async def __aenter__(self):
        """Async context manager entry"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()