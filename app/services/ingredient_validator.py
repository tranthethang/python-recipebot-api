import re
from typing import List
from app.utils.logger_config import get_logger

logger = get_logger(__name__)


class IngredientValidator:
    """Validates ingredient format and content."""
    
    QUANTITY_PATTERN = re.compile(r'^\d+(?:\.\d+)?\s*kg\s+\w+', re.IGNORECASE)
    MAX_INGREDIENTS = 20
    MIN_INGREDIENTS = 1
    
    def validate_ingredients_list(self, ingredients: List[str]) -> bool:
        """Validate the complete ingredients list.
        
        Args:
            ingredients: List of ingredient strings with quantities
            
        Returns:
            True if all ingredients are valid, False otherwise
        """
        if not self._check_list_size(ingredients):
            return False
        
        if not self._check_ingredients_content(ingredients):
            return False
        
        logger.info(f"Successfully validated {len(ingredients)} ingredients")
        return True
    
    def _check_list_size(self, ingredients: List[str]) -> bool:
        """Check if ingredients list size is within limits."""
        if not ingredients:
            logger.warning("Empty ingredients list provided")
            return False
        
        if len(ingredients) < self.MIN_INGREDIENTS:
            logger.warning(f"Too few ingredients: {len(ingredients)}")
            return False
        
        if len(ingredients) > self.MAX_INGREDIENTS:
            logger.warning(f"Too many ingredients: {len(ingredients)}")
            return False
        
        return True
    
    def _check_ingredients_content(self, ingredients: List[str]) -> bool:
        """Check if all ingredients have valid format."""
        for ingredient in ingredients:
            if not self._validate_single_ingredient(ingredient):
                return False
        return True
    
    def _validate_single_ingredient(self, ingredient: str) -> bool:
        """Validate a single ingredient format.
        
        Args:
            ingredient: Single ingredient string
            
        Returns:
            True if ingredient is valid, False otherwise
        """
        if not ingredient or not ingredient.strip():
            logger.warning("Empty ingredient found")
            return False
        
        if not self.QUANTITY_PATTERN.match(ingredient.strip()):
            logger.warning(f"Invalid ingredient format: {ingredient}")
            return False
        
        return True