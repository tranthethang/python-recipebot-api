from typing import Dict, Any
from fastapi import APIRouter, Depends
from app.models.recipe_models import RecipeRequest, RecipeResponse
from app.services.recipe_generator import RecipeGenerator
from app.utils.response_formatter import ResponseFormatter
from app.utils.logger_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


def get_recipe_generator() -> RecipeGenerator:
    """Dependency to get RecipeGenerator instance."""
    return RecipeGenerator()


@router.post("/api/recipe", response_model=RecipeResponse)
async def generate_recipe(
    request: RecipeRequest,
    recipe_generator: RecipeGenerator = Depends(get_recipe_generator)
) -> RecipeResponse:
    """Generate recipe from ingredients.
    
    Args:
        request: Recipe request containing ingredients list
        recipe_generator: Injected RecipeGenerator service
        
    Returns:
        Recipe response or error
        
    Raises:
        HTTPException: For various error conditions
    """
    logger.info(f"Received recipe request with {len(request.ingredients)} ingredients")
    
    try:
        result = await recipe_generator.generate_recipe_from_ingredients(
            request.ingredients
        )
        
        if result["status"] == "success":
            return ResponseFormatter.format_success_response(result)
        else:
            raise ResponseFormatter.format_error_response(result["message"], 400)
            
    except Exception as e:
        logger.error(f"Recipe generation endpoint error: {str(e)}")
        raise ResponseFormatter.format_server_error(
            "Internal server error occurred"
        )