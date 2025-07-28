import os
from typing import List
from app.utils.logger_config import get_logger

logger = get_logger(__name__)


class PromptGenerator:
    """Generates AI prompts from templates and ingredients."""
    
    TEMPLATE_FILE = "templates/prompt-template.txt"
    INGREDIENT_PLACEHOLDER = "{ingredients}"
    
    def __init__(self):
        self.template_content = self._load_template()
    
    def generate_prompt(self, ingredients: List[str]) -> str:
        """Generate AI prompt from ingredients list.
        
        Args:
            ingredients: List of validated ingredients
            
        Returns:
            Complete prompt string for AI
            
        Raises:
            ValueError: If template loading fails
        """
        if not ingredients:
            raise ValueError("Cannot generate prompt from empty ingredients list")
        
        ingredients_text = self._format_ingredients_list(ingredients)
        prompt = self.template_content.replace(
            self.INGREDIENT_PLACEHOLDER, 
            ingredients_text
        )
        
        logger.info(f"Generated prompt for {len(ingredients)} ingredients")
        return prompt
    
    def _load_template(self) -> str:
        """Load prompt template from file.
        
        Returns:
            Template content as string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            ValueError: If template is empty or invalid
        """
        try:
            with open(self.TEMPLATE_FILE, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            
            if not content:
                raise ValueError("Template file is empty")
            
            if self.INGREDIENT_PLACEHOLDER not in content:
                raise ValueError("Template missing ingredients placeholder")
            
            logger.info("Successfully loaded prompt template")
            return content
            
        except FileNotFoundError:
            logger.error(f"Template file not found: {self.TEMPLATE_FILE}")
            raise
        except Exception as e:
            logger.error(f"Failed to load template: {str(e)}")
            raise ValueError(f"Template loading failed: {str(e)}")
    
    def _format_ingredients_list(self, ingredients: List[str]) -> str:
        """Format ingredients list for prompt insertion."""
        return ", ".join(ingredients)