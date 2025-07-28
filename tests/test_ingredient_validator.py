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