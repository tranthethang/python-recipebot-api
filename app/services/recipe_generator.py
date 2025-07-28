import json
import re
from typing import List, Dict, Any, Optional
from app.services.ingredient_validator import IngredientValidator
from app.services.prompt_generator import PromptGenerator
from app.services.openrouter_client import OpenRouterClient
from app.models.recipe_models import Recipe
from app.utils.logger_config import get_logger

logger = get_logger(__name__)


class RecipeGenerator:
    """Main service for generating recipes from ingredients."""
    
    def __init__(self):
        self.validator = IngredientValidator()
        self.prompt_generator = PromptGenerator()
        self.ai_client = OpenRouterClient()
    
    async def generate_recipe_from_ingredients(self, ingredients: List[str]) -> Dict[str, Any]:
        """Generate recipe from ingredients list.
        
        Args:
            ingredients: List of ingredient strings with quantities
            
        Returns:
            Dictionary containing recipe or error message
        """
        logger.info(f"Processing recipe request with {len(ingredients)} ingredients")
        
        if not self.validator.validate_ingredients_list(ingredients):
            return self._create_insufficient_data_response()
        
        try:
            prompt = self.prompt_generator.generate_prompt(ingredients)
            ai_response = await self.ai_client.generate_recipe(prompt)
            recipe_data = self._parse_ai_response(ai_response["content"])
            
            if recipe_data:
                recipe = Recipe(**recipe_data)
                logger.info("Successfully generated recipe")
                return {"status": "success", "recipe": recipe.model_dump()}
            else:
                logger.warning("Failed to parse AI response into recipe")
                return self._create_insufficient_data_response()
                
        except Exception as e:
            logger.error(f"Recipe generation failed: {str(e)}")
            return self._create_error_response(f"Recipe generation failed: {str(e)}")
    
    def _parse_ai_response(self, ai_content: str) -> Optional[Dict[str, Any]]:
        """Parse AI response content into recipe dictionary."""
        try:
            if ai_content.strip().lower().startswith("need to provide more ingredients"):
                return None
            
            recipe_data = self._extract_recipe_data(ai_content)
            return recipe_data
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            return None
    
    def _extract_recipe_data(self, content: str) -> Dict[str, Any]:
        """Extract structured recipe data from AI response."""
        recipe_data = {
            "title": self._extract_title(content),
            "ingredients": self._extract_ingredients(content),
            "instructions": self._extract_instructions(content),
            "cooking_time": self._extract_cooking_time(content)
        }
        
        if not all(recipe_data.values()):
            raise ValueError("Incomplete recipe data from AI response")
        
        return recipe_data
    
    def _extract_title(self, content: str) -> str:
        """Extract recipe title from AI response."""
        title_patterns = [
            r"(?:Title|Recipe|Name):\s*(.+)",
            r"# (.+)",
            r"## (.+)"
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Generated Recipe"
    
    def _extract_ingredients(self, content: str) -> List[str]:
        """Extract ingredients list from AI response."""
        ingredients_section = re.search(
            r"(?:Ingredients|Materials):\s*(.*?)(?:\n\n|\nInstructions|\nSteps|$)", 
            content, 
            re.IGNORECASE | re.DOTALL
        )
        
        if ingredients_section:
            ingredients_text = ingredients_section.group(1)
            ingredients = [
                line.strip().lstrip('•-*').strip() 
                for line in ingredients_text.split('\n')
                if line.strip() and not line.strip().startswith(('Instructions', 'Steps'))
            ]
            return [ing for ing in ingredients if ing]
        
        return ["Ingredients not specified"]
    
    def _extract_instructions(self, content: str) -> List[str]:
        """Extract cooking instructions from AI response."""
        instructions_section = re.search(
            r"(?:Instructions|Steps|Method):\s*(.*?)(?:\n\n|$)", 
            content, 
            re.IGNORECASE | re.DOTALL
        )
        
        if instructions_section:
            instructions_text = instructions_section.group(1)
            instructions = [
                line.strip().lstrip('1234567890.').strip() 
                for line in instructions_text.split('\n')
                if line.strip()
            ]
            return [inst for inst in instructions if inst]
        
        return ["Instructions not provided"]
    
    def _extract_cooking_time(self, content: str) -> str:
        """Extract cooking time from AI response."""
        time_patterns = [
            r"(?:Cooking time|Prep time|Total time):\s*(.+)",
            r"(\d+\s*(?:minutes?|hours?|mins?))"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "30 minutes"
    
    def _create_insufficient_data_response(self) -> Dict[str, str]:
        """Create response for insufficient ingredients."""
        return {
            "status": "error",
            "message": "need to provide more ingredients"
        }
    
    def _create_error_response(self, message: str) -> Dict[str, str]:
        """Create error response."""
        return {
            "status": "error",
            "message": message
        }