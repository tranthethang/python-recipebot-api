import pytest
from app.services.ingredient_validator import IngredientValidator


class TestIngredientValidator:
    """Test cases for IngredientValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = IngredientValidator()
    
    def test_validate_valid_ingredients_list(self):
        """Test validation of valid ingredients list."""
        valid_ingredients = ["2kg pork", "1kg potatoes", "0.5kg onions"]
        result = self.validator.validate_ingredients_list(valid_ingredients)
        assert result is True
    
    def test_validate_empty_ingredients_list(self):
        """Test validation of empty ingredients list."""
        empty_ingredients = []
        result = self.validator.validate_ingredients_list(empty_ingredients)
        assert result is False
    
    def test_validate_none_ingredients_list(self):
        """Test validation of None ingredients list."""
        none_ingredients = None
        result = self.validator.validate_ingredients_list(none_ingredients)
        assert result is False
    
    def test_validate_too_many_ingredients(self):
        """Test validation with too many ingredients."""
        too_many_ingredients = [f"{i}kg ingredient{i}" for i in range(25)]
        result = self.validator.validate_ingredients_list(too_many_ingredients)
        assert result is False
    
    def test_validate_ingredients_without_quantity(self):
        """Test validation of ingredients without quantity."""
        invalid_ingredients = ["pork", "potatoes", "onions"]
        result = self.validator.validate_ingredients_list(invalid_ingredients)
        assert result is False
    
    def test_validate_ingredients_with_invalid_format(self):
        """Test validation of ingredients with invalid format."""
        invalid_ingredients = ["2 pork", "1 potatoes", "0.5 onions"]
        result = self.validator.validate_ingredients_list(invalid_ingredients)
        assert result is False
    
    def test_validate_mixed_valid_invalid_ingredients(self):
        """Test validation with mix of valid and invalid ingredients."""
        mixed_ingredients = ["2kg pork", "potatoes", "0.5kg onions"]
        result = self.validator.validate_ingredients_list(mixed_ingredients)
        assert result is False
    
    def test_validate_single_ingredient(self):
        """Test validation of single valid ingredient."""
        single_ingredient_valid = "2kg pork"
        result = self.validator._validate_single_ingredient(single_ingredient_valid)
        assert result is True
    
    def test_validate_single_ingredient_empty_string(self):
        """Test validation of empty string ingredient."""
        empty_ingredient = ""
        result = self.validator._validate_single_ingredient(empty_ingredient)
        assert result is False
    
    def test_validate_single_ingredient_whitespace_only(self):
        """Test validation of whitespace-only ingredient."""
        whitespace_ingredient = "   "
        result = self.validator._validate_single_ingredient(whitespace_ingredient)
        assert result is False
    
    def test_check_list_size_valid(self):
        """Test list size check with valid size."""
        valid_size_list = ["2kg pork", "1kg potatoes"]
        result = self.validator._check_list_size(valid_size_list)
        assert result is True
    
    def test_check_list_size_empty(self):
        """Test list size check with empty list."""
        empty_list = []
        result = self.validator._check_list_size(empty_list)
        assert result is False
    
    def test_check_list_size_too_large(self):
        """Test list size check with oversized list."""
        oversized_list = ["ingredient"] * 25
        result = self.validator._check_list_size(oversized_list)
        assert result is False
    
    def test_validate_mass_units(self):
        """Test validation with various mass units."""
        mass_ingredients = [
            "2kg pork",
            "500g flour", 
            "1lb beef",
            "8oz cheese",
            "2.5 kilograms potatoes",
            "100 grams sugar"
        ]
        for ingredient in mass_ingredients:
            result = self.validator._validate_single_ingredient(ingredient)
            assert result is True, f"Failed to validate mass ingredient: {ingredient}"
    
    def test_validate_capacity_units(self):
        """Test validation with various capacity units."""
        capacity_ingredients = [
            "2l milk",
            "500ml water",
            "1 cup flour",
            "2 tbsp oil",
            "1 tsp salt",
            "16 fl oz broth",
            "3 liters stock",
            "250 milliliters cream"
        ]
        for ingredient in capacity_ingredients:
            result = self.validator._validate_single_ingredient(ingredient)
            assert result is True, f"Failed to validate capacity ingredient: {ingredient}"
    
    def test_get_ingredient_unit(self):
        """Test unit extraction from ingredients."""
        test_cases = [
            ("2kg pork", "kg"),
            ("500g flour", "g"),
            ("1 cup milk", "cup"),
            ("2 tbsp oil", "tbsp"),
            ("1 tsp salt", "tsp"),
            ("16 fl oz broth", "fl oz"),
            ("invalid ingredient", "")
        ]
        
        for ingredient, expected_unit in test_cases:
            result = self.validator.get_ingredient_unit(ingredient)
            assert result == expected_unit, f"Expected {expected_unit}, got {result} for {ingredient}"
    
    def test_is_mass_unit(self):
        """Test mass unit identification."""
        mass_units = ["kg", "g", "lb", "oz", "kilogram", "gram", "pound", "ounce"]
        for unit in mass_units:
            assert self.validator.is_mass_unit(unit) is True, f"{unit} should be identified as mass unit"
        
        non_mass_units = ["l", "ml", "cup", "tbsp", "tsp"]
        for unit in non_mass_units:
            assert self.validator.is_mass_unit(unit) is False, f"{unit} should not be identified as mass unit"
    
    def test_is_capacity_unit(self):
        """Test capacity unit identification."""
        capacity_units = ["l", "ml", "cup", "tbsp", "tsp", "fl oz", "liter", "milliliter"]
        for unit in capacity_units:
            assert self.validator.is_capacity_unit(unit) is True, f"{unit} should be identified as capacity unit"
        
        non_capacity_units = ["kg", "g", "lb", "oz"]
        for unit in non_capacity_units:
            assert self.validator.is_capacity_unit(unit) is False, f"{unit} should not be identified as capacity unit"
    
    def test_get_supported_units(self):
        """Test getting all supported units."""
        units = self.validator.get_supported_units()
        
        assert "mass_units" in units
        assert "capacity_units" in units
        assert isinstance(units["mass_units"], list)
        assert isinstance(units["capacity_units"], list)
        assert len(units["mass_units"]) > 0
        assert len(units["capacity_units"]) > 0
        
        # Check that some expected units are present
        assert "kg" in units["mass_units"]
        assert "g" in units["mass_units"]
        assert "l" in units["capacity_units"]
        assert "ml" in units["capacity_units"]