import pytest
from fastapi import HTTPException
from app.utils.response_formatter import ResponseFormatter
from app.models.recipe_models import RecipeResponse, Recipe


class TestResponseFormatter:
    """Test cases for ResponseFormatter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_recipe_data = {
            "recipe": {
                "title": "Test Recipe",
                "ingredients": ["2kg pork", "1kg potatoes"],
                "instructions": ["Step 1", "Step 2"],
                "cooking_time": "30 minutes"
            }
        }
    
    def test_format_success_response(self):
        """Test successful response formatting."""
        result = ResponseFormatter.format_success_response(self.sample_recipe_data)
        
        assert isinstance(result, RecipeResponse)
        assert result.status == "success"
        assert result.recipe.title == "Test Recipe"
        assert len(result.recipe.ingredients) == 2
        assert len(result.recipe.instructions) == 2
        assert result.recipe.cooking_time == "30 minutes"
    
    def test_format_error_response_default_status(self):
        """Test error response formatting with default status code."""
        message = "Test error message"
        
        result = ResponseFormatter.format_error_response(message)
        
        assert isinstance(result, HTTPException)
        assert result.status_code == 400
        assert result.detail["status"] == "error"
        assert result.detail["message"] == message
    
    def test_format_error_response_custom_status(self):
        """Test error response formatting with custom status code."""
        message = "Custom error"
        status_code = 500
        
        result = ResponseFormatter.format_error_response(message, status_code)
        
        assert isinstance(result, HTTPException)
        assert result.status_code == 500
        assert result.detail["message"] == message
    
    def test_format_validation_error(self):
        """Test validation error formatting."""
        message = "Validation failed"
        
        result = ResponseFormatter.format_validation_error(message)
        
        assert isinstance(result, HTTPException)
        assert result.status_code == 422
        assert result.detail["message"] == message
    
    def test_format_server_error(self):
        """Test server error formatting."""
        message = "Internal server error"
        
        result = ResponseFormatter.format_server_error(message)
        
        assert isinstance(result, HTTPException)
        assert result.status_code == 500
        assert result.detail["message"] == message