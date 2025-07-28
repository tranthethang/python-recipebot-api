from typing import Dict, Any
from fastapi import HTTPException
from app.models.recipe_models import RecipeResponse, ErrorResponse


class ResponseFormatter:
    """Formats API responses according to specification."""
    
    @staticmethod
    def format_success_response(recipe_data: Dict[str, Any]) -> RecipeResponse:
        """Format successful recipe response.
        
        Args:
            recipe_data: Dictionary containing recipe information
            
        Returns:
            Formatted RecipeResponse object
        """
        return RecipeResponse(recipe=recipe_data["recipe"])
    
    @staticmethod
    def format_error_response(message: str, status_code: int = 400) -> HTTPException:
        """Format error response as HTTPException.
        
        Args:
            message: Error message
            status_code: HTTP status code
            
        Returns:
            HTTPException with formatted error
        """
        error_response = ErrorResponse(message=message)
        return HTTPException(
            status_code=status_code,
            detail=error_response.model_dump()
        )
    
    @staticmethod
    def format_validation_error(message: str) -> HTTPException:
        """Format validation error response."""
        return ResponseFormatter.format_error_response(message, 422)
    
    @staticmethod
    def format_server_error(message: str) -> HTTPException:
        """Format server error response."""
        return ResponseFormatter.format_error_response(message, 500)