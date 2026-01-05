"""
AI Service for recipe generation, meal planning, and intelligent suggestions
Integrates with Ollama for local AI processing
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.schemas.recipe import RecipeCreate
from app.schemas.meal_plan import MealPlanCreate, MealPlanEntryCreate
from app.services.inventory_service import InventoryService

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered features"""
    
    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.chat_model = settings.OLLAMA_CHAT_MODEL
        self.recipe_model = settings.OLLAMA_RECIPE_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self.session = None
        
    async def initialize_models(self):
        """Initialize and verify AI models"""
        if not settings.ENABLE_AI_FEATURES:
            logger.info("AI features are disabled")
            return
            
        try:
            # Check if models are available
            models = await self._list_models()
            logger.info(f"Available Ollama models: {models}")
            
            # Pull required models if not available
            available_models = [m["name"] for m in models.get("models", [])]
            
            if self.chat_model not in available_models:
                logger.info(f"Pulling chat model: {self.chat_model}")
                await self._pull_model(self.chat_model)
                
            if self.recipe_model not in available_models:
                logger.info(f"Pulling recipe model: {self.recipe_model}")
                await self._pull_model(self.recipe_model)
                
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
            if settings.ENVIRONMENT == "development":
                raise
            
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                base_url=self.ollama_base_url,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session
        
    async def _list_models(self) -> Dict[str, Any]:
        """List available Ollama models"""
        session = await self._get_session()
        async with session.get("/api/tags") as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to list models: {response.status}")
                
    async def _pull_model(self, model_name: str):
        """Pull a model from Ollama"""
        session = await self._get_session()
        async with session.post("/api/pull", json={"name": model_name}) as response:
            if response.status != 200:
                raise Exception(f"Failed to pull model {model_name}: {response.status}")
                
    async def _generate_completion(self, model: str, prompt: str, **kwargs) -> str:
        """Generate text completion using Ollama"""
        if not settings.ENABLE_AI_FEATURES:
            return "AI features are disabled"
            
        session = await self._get_session()
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        
        async with session.post("/api/generate", json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama API error: {response.status}")
                return "Sorry, I couldn't process that request."
                
    async def _chat_completion(self, model: str, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion using Ollama"""
        if not settings.ENABLE_AI_FEATURES:
            return "AI features are disabled"
            
        session = await self._get_session()
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            **kwargs
        }
        
        async with session.post("/api/chat", json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("message", {}).get("content", "")
            else:
                logger.error(f"Ollama chat API error: {response.status}")
                return "Sorry, I couldn't process that request."
    
    # Recipe Generation Methods
    
    async def generate_recipe_from_ingredients(
        self,
        ingredients: List[str],
        dietary_restrictions: List[str] = None,
        cuisine_type: str = None,
        difficulty: str = None,
        user: User = None
    ) -> Optional[RecipeCreate]:
        """Generate a recipe from available ingredients"""
        
        dietary_str = f"Dietary restrictions: {', '.join(dietary_restrictions)}. " if dietary_restrictions else ""
        cuisine_str = f"Cuisine type: {cuisine_type}. " if cuisine_type else ""
        difficulty_str = f"Difficulty: {difficulty}. " if difficulty else ""
        
        prompt = f"""
        Create a detailed recipe using these ingredients: {', '.join(ingredients)}.
        {dietary_str}{cuisine_str}{difficulty_str}
        
        Format the response as a JSON object with the following structure:
        {{
            "title": "Recipe title",
            "description": "Brief description",
            "prep_time": 30,
            "cook_time": 45,
            "servings": 4,
            "difficulty": "easy|medium|hard",
            "cuisine_type": "Italian|Mexican|Asian|etc",
            "ingredients": [
                {{"name": "ingredient name", "quantity": "1 cup", "notes": "optional notes"}}
            ],
            "instructions": [
                {{"step_number": 1, "instruction": "First instruction", "duration": 5}},
                {{"step_number": 2, "instruction": "Second instruction", "duration": 10}}
            ],
            "nutrition_info": {{
                "calories": 350,
                "protein": 25,
                "carbs": 45,
                "fat": 12
            }},
            "tags": ["quick", "healthy", "vegetarian"],
            "tips": ["Optional cooking tips"]
        }}
        
        Make sure the recipe is practical, delicious, and uses the ingredients efficiently.
        """
        
        response = await self._generate_completion(self.recipe_model, prompt)
        
        try:
            recipe_data = json.loads(response)
            return RecipeCreate(**recipe_data)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to parse generated recipe: {e}")
            return None
            
    async def suggest_recipes_from_inventory(
        self,
        db: AsyncSession,
        user: User,
        max_recipes: int = 5
    ) -> List[Dict[str, Any]]:
        """Suggest recipes based on user's current inventory"""
        
        inventory_service = InventoryService(db)
        inventory_items = await inventory_service.get_user_inventory_items(user)
        
        if not inventory_items:
            return []
            
        ingredient_names = [item.name for item in inventory_items[:10]]  # Limit to prevent token overflow
        
        prompt = f"""
        Based on these available ingredients: {', '.join(ingredient_names)},
        suggest {max_recipes} different recipes that can be made.
        
        Format as a JSON array of objects:
        [
            {{
                "title": "Recipe 1",
                "description": "Brief description",
                "missing_ingredients": ["salt", "pepper"],
                "match_percentage": 85,
                "difficulty": "easy",
                "prep_time": 30
            }}
        ]
        
        Focus on recipes that use the available ingredients efficiently and minimize missing items.
        """
        
        response = await self._generate_completion(self.chat_model, prompt)
        
        try:
            suggestions = json.loads(response)
            return suggestions
        except json.JSONDecodeError:
            logger.error("Failed to parse recipe suggestions")
            return []
    
    # Meal Planning Methods
    
    async def generate_meal_plan(
        self,
        db: AsyncSession,
        user: User,
        days: int = 7,
        dietary_preferences: List[str] = None,
        budget_range: str = None
    ) -> Optional[MealPlanCreate]:
        """Generate a weekly meal plan"""
        
        dietary_str = f"Dietary preferences: {', '.join(dietary_preferences)}. " if dietary_preferences else ""
        budget_str = f"Budget range: {budget_range}. " if budget_range else ""
        
        # Get user's inventory for context
        inventory_service = InventoryService(db)
        inventory_items = await inventory_service.get_user_inventory_items(user)
        inventory_str = ", ".join([item.name for item in inventory_items[:5]]) if inventory_items else "No current inventory"
        
        prompt = f"""
        Create a {days}-day meal plan for a household.
        Current inventory: {inventory_str}
        {dietary_str}{budget_str}
        
        Format as JSON:
        {{
            "name": "Weekly Meal Plan",
            "description": "AI-generated meal plan",
            "entries": [
                {{
                    "date": "2024-01-15",
                    "meal_type": "breakfast",
                    "recipe_name": "Overnight Oats",
                    "estimated_prep_time": 5
                }},
                {{
                    "date": "2024-01-15", 
                    "meal_type": "lunch",
                    "recipe_name": "Chicken Salad",
                    "estimated_prep_time": 15
                }}
            ]
        }}
        
        Include breakfast, lunch, and dinner for each day. Use available ingredients when possible.
        Vary meals to avoid repetition. Consider prep time for busy days.
        """
        
        response = await self._generate_completion(self.chat_model, prompt)
        
        try:
            plan_data = json.loads(response)
            return MealPlanCreate(**plan_data)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to parse meal plan: {e}")
            return None
    
    # Smart Suggestions
    
    async def get_waste_reduction_tips(
        self,
        db: AsyncSession,
        user: User
    ) -> List[str]:
        """Get personalized waste reduction tips"""
        
        # This would analyze user's consumption patterns
        # For now, return general tips
        
        tips = [
            "Store herbs in water like flowers to keep them fresh longer",
            "Freeze overripe bananas for smoothies instead of throwing them away",
            "Use a first-in-first-out system when organizing your pantry",
            "Plan your meals around ingredients that are about to expire",
            "Store apples away from other fruits to prevent premature ripening"
        ]
        
        return tips
        
    async def suggest_shopping_list_optimizations(
        self,
        current_list: List[Dict[str, Any]],
        store_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Optimize shopping list for cost and efficiency"""
        
        # Group by store sections
        sections = {
            "produce": [],
            "dairy": [],
            "meat": [],
            "pantry": [],
            "frozen": [],
            "other": []
        }
        
        section_mapping = {
            "fruits": "produce", "vegetables": "produce",
            "milk": "dairy", "cheese": "dairy", "yogurt": "dairy",
            "chicken": "meat", "beef": "meat", "fish": "meat",
            "rice": "pantry", "pasta": "pantry", "canned": "pantry",
            "ice cream": "frozen", "frozen vegetables": "frozen"
        }
        
        for item in current_list:
            category = item.get("category", "other").lower()
            section = section_mapping.get(category, "other")
            sections[section].append(item)
            
        return {
            "optimized_list": sections,
            "estimated_total": sum(item.get("estimated_price", 0) for item in current_list),
            "savings_tips": [
                "Buy seasonal produce for better prices",
                "Check store brands for pantry items",
                "Use loyalty programs and coupons"
            ]
        }
    
    # Chat and Q&A
    
    async def chat_about_cooking(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """General cooking and kitchen Q&A"""
        
        if not conversation_history:
            conversation_history = []
            
        system_message = {
            "role": "system",
            "content": "You are a helpful kitchen assistant. Answer questions about cooking, recipes, meal planning, and kitchen management. Be concise and practical."
        }
        
        user_message = {"role": "user", "content": message}
        
        messages = [system_message] + conversation_history + [user_message]
        
        response = await self._chat_completion(self.chat_model, messages)
        return response