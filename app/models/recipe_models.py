from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class RecipeRequest(BaseModel):
    """Request model for recipe generation."""
    ingredients: List[str] = Field(..., min_length=1, max_length=20)
    
    @field_validator('ingredients')
    @classmethod
    def validate_ingredients_format(cls, ingredients: List[str]) -> List[str]:
        """Validate ingredient format and content."""
        if not ingredients:
            raise ValueError("Ingredients list cannot be empty")
        
        for ingredient in ingredients:
            if not isinstance(ingredient, str) or not ingredient.strip():
                raise ValueError("Each ingredient must be a non-empty string")
            
            if not any(char.isdigit() for char in ingredient):
                raise ValueError(f"Ingredient '{ingredient}' must include quantity")
        
        return ingredients


class Recipe(BaseModel):
    """Recipe response model."""
    title: str = Field(..., min_length=1, max_length=100)
    ingredients: List[str] = Field(..., min_length=1)
    instructions: List[str] = Field(..., min_length=1)
    cooking_time: str = Field(..., min_length=1)


class RecipeResponse(BaseModel):
    """Success response model."""
    status: str = Field(default="success")
    recipe: Recipe


class ErrorResponse(BaseModel):
    """Error response model."""
    status: str = Field(default="error")
    message: str = Field(..., min_length=1)