import re
from typing import List, Set
from app.utils.logger_config import get_logger

logger = get_logger(__name__)


class IngredientValidator:
    """Validates ingredient format and content."""
    
    # Supported units for different measurement types
    MASS_UNITS: Set[str] = {
        'kg', 'kilogram', 'kilograms',
        'g', 'gram', 'grams',
        'lb', 'pound', 'pounds',
        'oz', 'ounce', 'ounces'
    }
    
    CAPACITY_UNITS: Set[str] = {
        'l', 'liter', 'liters', 'litre', 'litres',
        'ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres',
        'cup', 'cups',
        'tbsp', 'tablespoon', 'tablespoons',
        'tsp', 'teaspoon', 'teaspoons',
        'fl oz', 'fluid ounce', 'fluid ounces'
    }
    
    # Combined set of all supported units
    ALL_UNITS: Set[str] = MASS_UNITS | CAPACITY_UNITS
    
    # Create regex pattern that matches any supported unit
    QUANTITY_PATTERN = re.compile(
        r'^\d+(?:\.\d+)?\s*(?:' + '|'.join(re.escape(unit) for unit in ALL_UNITS) + r')\s+\w+',
        re.IGNORECASE
    )
    
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
    
    def get_ingredient_unit(self, ingredient: str) -> str:
        """Extract the unit from an ingredient string.
        
        Args:
            ingredient: Single ingredient string
            
        Returns:
            The unit found in the ingredient, or empty string if none found
        """
        ingredient = ingredient.strip().lower()
        
        # Sort units by length (descending) to match longer units first
        # This prevents "oz" from matching before "fl oz"
        sorted_units = sorted(self.ALL_UNITS, key=len, reverse=True)
        
        # Look for units in the ingredient string
        for unit in sorted_units:
            # Create pattern to match the unit - either after digits/space or with word boundaries
            pattern = r'(?:\d\s*|^|\s)' + re.escape(unit.lower()) + r'(?:\s|$)'
            if re.search(pattern, ingredient):
                return unit
        
        return ""
    
    def is_mass_unit(self, unit: str) -> bool:
        """Check if a unit is a mass measurement unit.
        
        Args:
            unit: Unit string to check
            
        Returns:
            True if unit is a mass unit, False otherwise
        """
        return unit.lower() in self.MASS_UNITS
    
    def is_capacity_unit(self, unit: str) -> bool:
        """Check if a unit is a capacity measurement unit.
        
        Args:
            unit: Unit string to check
            
        Returns:
            True if unit is a capacity unit, False otherwise
        """
        return unit.lower() in self.CAPACITY_UNITS
    
    def get_supported_units(self) -> dict:
        """Get all supported units categorized by type.
        
        Returns:
            Dictionary with mass and capacity units
        """
        return {
            "mass_units": sorted(list(self.MASS_UNITS)),
            "capacity_units": sorted(list(self.CAPACITY_UNITS))
        }