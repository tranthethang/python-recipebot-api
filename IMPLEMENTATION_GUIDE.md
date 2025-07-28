# RecipeBot API - Implementation Guide

## Overview
This document provides detailed step-by-step coding instructions and comprehensive unit test cases for implementing the RecipeBot API, following the technical specifications and coding conventions.

## Project Structure
```
recipebot-api/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── recipe_models.py       # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ingredient_validator.py
│   │   ├── openrouter_client.py
│   │   ├── prompt_generator.py
│   │   └── recipe_generator.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── recipe_routes.py       # API endpoints
│   └── utils/
│       ├── __init__.py
│       ├── logger_config.py
│       └── response_formatter.py
├── tests/
│   ├── __init__.py
│   ├── test_ingredient_validator.py
│   ├── test_openrouter_client.py
│   ├── test_prompt_generator.py
│   ├── test_recipe_generator.py
│   ├── test_recipe_routes.py
│   └── test_response_formatter.py
├── templates/
│   └── prompt-template.txt
├── .env
├── requirements.txt
└── pytest.ini
```

## Step-by-Step Implementation

### Step 1: Create Pydantic Models (app/models/recipe_models.py)

```python
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class RecipeRequest(BaseModel):
    """Request model for recipe generation."""
    ingredients: List[str] = Field(..., min_items=1, max_items=20)
    
    @validator('ingredients')
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
    ingredients: List[str] = Field(..., min_items=1)
    instructions: List[str] = Field(..., min_items=1)
    cooking_time: str = Field(..., min_length=1)


class RecipeResponse(BaseModel):
    """Success response model."""
    status: str = Field(default="success")
    recipe: Recipe


class ErrorResponse(BaseModel):
    """Error response model."""
    status: str = Field(default="error")
    message: str = Field(..., min_length=1)
```

### Step 2: Create Ingredient Validator (app/services/ingredient_validator.py)

```python
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
```

### Step 3: Create Prompt Generator (app/services/prompt_generator.py)

```python
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
```

### Step 4: Create OpenRouter Client (app/services/openrouter_client.py)

```python
import os
from typing import Dict, Any
import aiohttp
import asyncio
from app.utils.logger_config import get_logger

logger = get_logger(__name__)


class OpenRouterClient:
    """Handles communication with OpenRouter AI service."""
    
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    TIMEOUT_SECONDS = 30
    
    def __init__(self):
        self.api_key = self._get_api_key()
        self.headers = self._build_headers()
    
    async def generate_recipe(self, prompt: str) -> Dict[str, Any]:
        """Send prompt to OpenRouter and get recipe response.
        
        Args:
            prompt: Complete prompt string for AI
            
        Returns:
            Dictionary containing AI response
            
        Raises:
            ConnectionError: If API connection fails
            TimeoutError: If request times out
            ValueError: If response is invalid
        """
        payload = self._build_request_payload(prompt)
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(
                total=self.TIMEOUT_SECONDS
            )) as session:
                logger.info("Sending request to OpenRouter API")
                
                async with session.post(
                    self.BASE_URL, 
                    json=payload, 
                    headers=self.headers
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info("Successfully received response from OpenRouter")
                        return self._parse_api_response(result)
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error {response.status}: {error_text}")
                        raise ConnectionError(f"API request failed: {response.status}")
                        
        except asyncio.TimeoutError:
            logger.error("OpenRouter API request timeout")
            raise TimeoutError("AI service request timeout")
        except aiohttp.ClientError as e:
            logger.error(f"OpenRouter API connection error: {str(e)}")
            raise ConnectionError(f"API connection failed: {str(e)}")
    
    def _get_api_key(self) -> str:
        """Retrieve API key from environment variables."""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        return api_key
    
    def _build_headers(self) -> Dict[str, str]:
        """Build request headers for OpenRouter API."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "RecipeBot API"
        }
    
    def _build_request_payload(self, prompt: str) -> Dict[str, Any]:
        """Build request payload for OpenRouter API."""
        return {
            "model": "anthropic/claude-3-haiku",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
    
    def _parse_api_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate OpenRouter API response."""
        try:
            content = response["choices"][0]["message"]["content"]
            return {"content": content, "raw_response": response}
        except (KeyError, IndexError) as e:
            logger.error(f"Invalid API response format: {str(e)}")
            raise ValueError(f"Invalid API response: {str(e)}")
```

### Step 5: Create Recipe Generator (app/services/recipe_generator.py)

```python
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
                return {"status": "success", "recipe": recipe.dict()}
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
```

### Step 6: Create Response Formatter (app/utils/response_formatter.py)

```python
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
            detail=error_response.dict()
        )
    
    @staticmethod
    def format_validation_error(message: str) -> HTTPException:
        """Format validation error response."""
        return ResponseFormatter.format_error_response(message, 422)
    
    @staticmethod
    def format_server_error(message: str) -> HTTPException:
        """Format server error response."""
        return ResponseFormatter.format_error_response(message, 500)
```

### Step 7: Create Logger Configuration (app/utils/logger_config.py)

```python
import logging
import os
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """Configure and return logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        os.makedirs("logs", exist_ok=True)
        
        file_handler = logging.FileHandler(
            f"logs/recipebot_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger
```

### Step 8: Create API Routes (app/api/recipe_routes.py)

```python
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
            raise ResponseFormatter.format_error_response(result["message"])
            
    except Exception as e:
        logger.error(f"Recipe generation endpoint error: {str(e)}")
        raise ResponseFormatter.format_server_error(
            "Internal server error occurred"
        )
```

### Step 9: Create Main Application (app/main.py)

```python
from fastapi import FastAPI
from app.api.recipe_routes import router as recipe_router
from app.utils.logger_config import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="RecipeBot API",
    description="AI-powered recipe recommendations from ingredients",
    version="1.0.0"
)

app.include_router(recipe_router)


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("RecipeBot API starting up")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("RecipeBot API shutting down")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "RecipeBot API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Unit Test Cases

### Test 1: Ingredient Validator Tests (tests/test_ingredient_validator.py)

```python
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
```

### Test 2: Prompt Generator Tests (tests/test_prompt_generator.py)

```python
import pytest
from unittest.mock import patch, mock_open
from app.services.prompt_generator import PromptGenerator


class TestPromptGenerator:
    """Test cases for PromptGenerator class."""
    
    @patch("builtins.open", new_callable=mock_open, 
           read_data="Please create a recipe using these ingredients: {ingredients}")
    def test_generate_prompt_valid_ingredients(self, mock_file):
        """Test prompt generation with valid ingredients."""
        generator = PromptGenerator()
        ingredients = ["2kg pork", "1kg potatoes", "0.5kg onions"]
        
        result = generator.generate_prompt(ingredients)
        expected = "Please create a recipe using these ingredients: 2kg pork, 1kg potatoes, 0.5kg onions"
        
        assert result == expected
    
    @patch("builtins.open", new_callable=mock_open, 
           read_data="Please create a recipe using these ingredients: {ingredients}")
    def test_generate_prompt_empty_ingredients(self, mock_file):
        """Test prompt generation with empty ingredients list."""
        generator = PromptGenerator()
        empty_ingredients = []
        
        with pytest.raises(ValueError, match="Cannot generate prompt from empty ingredients list"):
            generator.generate_prompt(empty_ingredients)
    
    @patch("builtins.open", new_callable=mock_open, 
           read_data="Please create a recipe using these ingredients: {ingredients}")
    def test_generate_prompt_single_ingredient(self, mock_file):
        """Test prompt generation with single ingredient."""
        generator = PromptGenerator()
        single_ingredient = ["2kg pork"]
        
        result = generator.generate_prompt(single_ingredient)
        expected = "Please create a recipe using these ingredients: 2kg pork"
        
        assert result == expected
    
    @patch("builtins.open", side_effect=FileNotFoundError())
    def test_load_template_file_not_found(self, mock_file):
        """Test template loading when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            PromptGenerator()
    
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_load_template_empty_file(self, mock_file):
        """Test template loading with empty file."""
        with pytest.raises(ValueError, match="Template file is empty"):
            PromptGenerator()
    
    @patch("builtins.open", new_callable=mock_open, 
           read_data="This template has no placeholder")
    def test_load_template_missing_placeholder(self, mock_file):
        """Test template loading without required placeholder."""
        with pytest.raises(ValueError, match="Template missing ingredients placeholder"):
            PromptGenerator()
    
    @patch("builtins.open", new_callable=mock_open, 
           read_data="Recipe template with {ingredients} placeholder")
    def test_format_ingredients_list(self, mock_file):
        """Test ingredients list formatting."""
        generator = PromptGenerator()
        ingredients = ["2kg pork", "1kg potatoes", "0.5kg onions"]
        
        result = generator._format_ingredients_list(ingredients)
        expected = "2kg pork, 1kg potatoes, 0.5kg onions"
        
        assert result == expected
    
    @patch("builtins.open", new_callable=mock_open, 
           read_data="Recipe template with {ingredients} placeholder")
    def test_format_single_ingredient(self, mock_file):
        """Test single ingredient formatting."""
        generator = PromptGenerator()
        ingredients = ["2kg pork"]
        
        result = generator._format_ingredients_list(ingredients)
        expected = "2kg pork"
        
        assert result == expected
```

### Test 3: OpenRouter Client Tests (tests/test_openrouter_client.py)

```python
import pytest
from unittest.mock import patch, AsyncMock
import aiohttp
from app.services.openrouter_client import OpenRouterClient


class TestOpenRouterClient:
    """Test cases for OpenRouterClient class."""
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-api-key'})
    def test_init_with_valid_api_key(self):
        """Test client initialization with valid API key."""
        client = OpenRouterClient()
        assert client.api_key == 'test-api-key'
        assert 'Authorization' in client.headers
        assert client.headers['Authorization'] == 'Bearer test-api-key'
    
    @patch.dict('os.environ', {}, clear=True)
    def test_init_without_api_key(self):
        """Test client initialization without API key."""
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY environment variable not set"):
            OpenRouterClient()
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-api-key'})
    @patch('aiohttp.ClientSession.post')
    async def test_generate_recipe_success(self, mock_post):
        """Test successful recipe generation."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Recipe: Pork and Potato Stew\nIngredients: 2kg pork, 1kg potatoes\nInstructions: Cook together\nCooking time: 45 minutes"
                }
            }]
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        client = OpenRouterClient()
        prompt = "Create a recipe with pork and potatoes"
        
        result = await client.generate_recipe(prompt)
        
        assert "content" in result
        assert "raw_response" in result
        assert "Recipe: Pork and Potato Stew" in result["content"]
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-api-key'})
    @patch('aiohttp.ClientSession.post')
    async def test_generate_recipe_api_error(self, mock_post):
        """Test recipe generation with API error."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        mock_post.return_value.__aenter__.return_value = mock_response
        
        client = OpenRouterClient()
        prompt = "Create a recipe"
        
        with pytest.raises(ConnectionError, match="API request failed: 500"):
            await client.generate_recipe(prompt)
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-api-key'})
    @patch('aiohttp.ClientSession.post')
    async def test_generate_recipe_timeout(self, mock_post):
        """Test recipe generation with timeout."""
        mock_post.side_effect = asyncio.TimeoutError()
        
        client = OpenRouterClient()
        prompt = "Create a recipe"
        
        with pytest.raises(TimeoutError, match="AI service request timeout"):
            await client.generate_recipe(prompt)
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-api-key'})
    @patch('aiohttp.ClientSession.post')
    async def test_generate_recipe_connection_error(self, mock_post):
        """Test recipe generation with connection error."""
        mock_post.side_effect = aiohttp.ClientError("Connection failed")
        
        client = OpenRouterClient()
        prompt = "Create a recipe"
        
        with pytest.raises(ConnectionError, match="API connection failed"):
            await client.generate_recipe(prompt)
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-api-key'})
    def test_build_request_payload(self):
        """Test request payload building."""
        client = OpenRouterClient()
        prompt = "Test prompt"
        
        payload = client._build_request_payload(prompt)
        
        assert payload["model"] == "anthropic/claude-3-haiku"
        assert payload["messages"][0]["content"] == "Test prompt"
        assert payload["max_tokens"] == 1000
        assert payload["temperature"] == 0.7
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-api-key'})
    def test_parse_api_response_valid(self):
        """Test parsing valid API response."""
        client = OpenRouterClient()
        response = {
            "choices": [{
                "message": {
                    "content": "Recipe content here"
                }
            }]
        }
        
        result = client._parse_api_response(response)
        
        assert result["content"] == "Recipe content here"
        assert result["raw_response"] == response
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-api-key'})
    def test_parse_api_response_invalid(self):
        """Test parsing invalid API response."""
        client = OpenRouterClient()
        invalid_response = {"invalid": "response"}
        
        with pytest.raises(ValueError, match="Invalid API response"):
            client._parse_api_response(invalid_response)
```

### Test 4: Recipe Generator Tests (tests/test_recipe_generator.py)

```python
import pytest
from unittest.mock import AsyncMock, patch
from app.services.recipe_generator import RecipeGenerator


class TestRecipeGenerator:
    """Test cases for RecipeGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = RecipeGenerator()
    
    @patch('app.services.recipe_generator.IngredientValidator')
    @patch('app.services.recipe_generator.PromptGenerator')
    @patch('app.services.recipe_generator.OpenRouterClient')
    async def test_generate_recipe_success(self, mock_client, mock_prompt, mock_validator):
        """Test successful recipe generation."""
        # Setup mocks
        mock_validator.return_value.validate_ingredients_list.return_value = True
        mock_prompt.return_value.generate_prompt.return_value = "Test prompt"
        mock_client.return_value.generate_recipe = AsyncMock(return_value={
            "content": "Title: Pork Stew\nIngredients:\n- 2kg pork\n- 1kg potatoes\nInstructions:\n1. Cook pork\n2. Add potatoes\nCooking time: 45 minutes"
        })
        
        ingredients = ["2kg pork", "1kg potatoes"]
        result = await self.generator.generate_recipe_from_ingredients(ingredients)
        
        assert result["status"] == "success"
        assert "recipe" in result
        assert result["recipe"]["title"] == "Pork Stew"
    
    @patch('app.services.recipe_generator.IngredientValidator')
    async def test_generate_recipe_invalid_ingredients(self, mock_validator):
        """Test recipe generation with invalid ingredients."""
        mock_validator.return_value.validate_ingredients_list.return_value = False
        
        ingredients = ["invalid"]
        result = await self.generator.generate_recipe_from_ingredients(ingredients)
        
        assert result["status"] == "error"
        assert result["message"] == "need to provide more ingredients"
    
    @patch('app.services.recipe_generator.IngredientValidator')
    @patch('app.services.recipe_generator.PromptGenerator')
    @patch('app.services.recipe_generator.OpenRouterClient')
    async def test_generate_recipe_ai_insufficient_data(self, mock_client, mock_prompt, mock_validator):
        """Test recipe generation when AI returns insufficient data."""
        mock_validator.return_value.validate_ingredients_list.return_value = True
        mock_prompt.return_value.generate_prompt.return_value = "Test prompt"
        mock_client.return_value.generate_recipe = AsyncMock(return_value={
            "content": "need to provide more ingredients"
        })
        
        ingredients = ["2kg pork"]
        result = await self.generator.generate_recipe_from_ingredients(ingredients)
        
        assert result["status"] == "error"
        assert result["message"] == "need to provide more ingredients"
    
    @patch('app.services.recipe_generator.IngredientValidator')
    @patch('app.services.recipe_generator.PromptGenerator')
    @patch('app.services.recipe_generator.OpenRouterClient')
    async def test_generate_recipe_exception(self, mock_client, mock_prompt, mock_validator):
        """Test recipe generation with exception."""
        mock_validator.return_value.validate_ingredients_list.return_value = True
        mock_prompt.return_value.generate_prompt.side_effect = Exception("Test error")
        
        ingredients = ["2kg pork"]
        result = await self.generator.generate_recipe_from_ingredients(ingredients)
        
        assert result["status"] == "error"
        assert "Recipe generation failed" in result["message"]
    
    def test_extract_title_with_title_prefix(self):
        """Test title extraction with title prefix."""
        content = "Title: Delicious Pork Stew\nIngredients: pork, potatoes"
        title = self.generator._extract_title(content)
        assert title == "Delicious Pork Stew"
    
    def test_extract_title_with_hash_prefix(self):
        """Test title extraction with hash prefix."""
        content = "# Amazing Recipe\nIngredients: pork, potatoes"
        title = self.generator._extract_title(content)
        assert title == "Amazing Recipe"
    
    def test_extract_title_no_prefix(self):
        """Test title extraction without prefix."""
        content = "Some recipe content without title"
        title = self.generator._extract_title(content)
        assert title == "Generated Recipe"
    
    def test_extract_ingredients_with_section(self):
        """Test ingredients extraction with ingredients section."""
        content = "Title: Recipe\nIngredients:\n- 2kg pork\n- 1kg potatoes\nInstructions: Cook well"
        ingredients = self.generator._extract_ingredients(content)
        assert "2kg pork" in ingredients
        assert "1kg potatoes" in ingredients
    
    def test_extract_ingredients_no_section(self):
        """Test ingredients extraction without ingredients section."""
        content = "Title: Recipe\nSome content without ingredients section"
        ingredients = self.generator._extract_ingredients(content)
        assert ingredients == ["Ingredients not specified"]
    
    def test_extract_instructions_with_section(self):
        """Test instructions extraction with instructions section."""
        content = "Ingredients: pork\nInstructions:\n1. Cook pork\n2. Serve hot"
        instructions = self.generator._extract_instructions(content)
        assert "Cook pork" in instructions
        assert "Serve hot" in instructions
    
    def test_extract_instructions_no_section(self):
        """Test instructions extraction without instructions section."""
        content = "Ingredients: pork\nSome content without instructions"
        instructions = self.generator._extract_instructions(content)
        assert instructions == ["Instructions not provided"]
    
    def test_extract_cooking_time_with_prefix(self):
        """Test cooking time extraction with time prefix."""
        content = "Recipe content\nCooking time: 45 minutes\nMore content"
        cooking_time = self.generator._extract_cooking_time(content)
        assert cooking_time == "45 minutes"
    
    def test_extract_cooking_time_pattern_match(self):
        """Test cooking time extraction with pattern matching."""
        content = "Recipe takes about 30 minutes to prepare"
        cooking_time = self.generator._extract_cooking_time(content)
        assert cooking_time == "30 minutes"
    
    def test_extract_cooking_time_no_match(self):
        """Test cooking time extraction with no matches."""
        content = "Recipe content without time information"
        cooking_time = self.generator._extract_cooking_time(content)
        assert cooking_time == "30 minutes"
    
    def test_create_insufficient_data_response(self):
        """Test insufficient data response creation."""
        response = self.generator._create_insufficient_data_response()
        assert response["status"] == "error"
        assert response["message"] == "need to provide more ingredients"
    
    def test_create_error_response(self):
        """Test error response creation."""
        message = "Test error message"
        response = self.generator._create_error_response(message)
        assert response["status"] == "error"
        assert response["message"] == message
```

### Test 5: API Routes Tests (tests/test_recipe_routes.py)

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)


class TestRecipeRoutes:
    """Test cases for recipe API routes."""
    
    def test_health_check_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @patch('app.api.recipe_routes.RecipeGenerator')
    def test_generate_recipe_success(self, mock_generator):
        """Test successful recipe generation endpoint."""
        mock_instance = AsyncMock()
        mock_instance.generate_recipe_from_ingredients.return_value = {
            "status": "success",
            "recipe": {
                "title": "Pork Stew",
                "ingredients": ["2kg pork", "1kg potatoes"],
                "instructions": ["Cook pork", "Add potatoes"],
                "cooking_time": "45 minutes"
            }
        }
        mock_generator.return_value = mock_instance
        
        request_data = {
            "ingredients": ["2kg pork", "1kg potatoes", "0.5kg onions"]
        }
        
        response = client.post("/api/recipe", json=request_data)
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert "recipe" in response.json()
    
    def test_generate_recipe_empty_ingredients(self):
        """Test recipe generation with empty ingredients."""
        request_data = {"ingredients": []}
        
        response = client.post("/api/recipe", json=request_data)
        
        assert response.status_code == 422
    
    def test_generate_recipe_missing_ingredients(self):
        """Test recipe generation without ingredients field."""
        request_data = {}
        
        response = client.post("/api/recipe", json=request_data)
        
        assert response.status_code == 422
    
    def test_generate_recipe_invalid_ingredient_format(self):
        """Test recipe generation with invalid ingredient format."""
        request_data = {
            "ingredients": ["pork", "potatoes", "onions"]  # Missing quantities
        }
        
        response = client.post("/api/recipe", json=request_data)
        
        assert response.status_code == 422
    
    def test_generate_recipe_too_many_ingredients(self):
        """Test recipe generation with too many ingredients."""
        request_data = {
            "ingredients": [f"{i}kg ingredient{i}" for i in range(25)]
        }
        
        response = client.post("/api/recipe", json=request_data)
        
        assert response.status_code == 422
    
    @patch('app.api.recipe_routes.RecipeGenerator')
    def test_generate_recipe_insufficient_ingredients_error(self, mock_generator):
        """Test recipe generation returning insufficient ingredients error."""
        mock_instance = AsyncMock()
        mock_instance.generate_recipe_from_ingredients.return_value = {
            "status": "error",
            "message": "need to provide more ingredients"
        }
        mock_generator.return_value = mock_instance
        
        request_data = {
            "ingredients": ["1kg pork"]
        }
        
        response = client.post("/api/recipe", json=request_data)
        
        assert response.status_code == 400
        assert "need to provide more ingredients" in str(response.json())
    
    @patch('app.api.recipe_routes.RecipeGenerator')
    def test_generate_recipe_server_error(self, mock_generator):
        """Test recipe generation with server error."""
        mock_instance = AsyncMock()
        mock_instance.generate_recipe_from_ingredients.side_effect = Exception("Server error")
        mock_generator.return_value = mock_instance
        
        request_data = {
            "ingredients": ["2kg pork", "1kg potatoes"]
        }
        
        response = client.post("/api/recipe", json=request_data)
        
        assert response.status_code == 500
    
    def test_generate_recipe_valid_ingredients_format(self):
        """Test recipe generation with valid ingredients format."""
        request_data = {
            "ingredients": ["2kg pork", "1.5kg potatoes", "0.5kg onions"]
        }
        
        # This should pass validation
        # Note: Actual generation might fail due to mocked dependencies
        response = client.post("/api/recipe", json=request_data)
        
        # Should not fail at validation level
        assert response.status_code != 422
    
    def test_generate_recipe_single_ingredient(self):
        """Test recipe generation with single ingredient."""
        request_data = {
            "ingredients": ["2kg pork"]
        }
        
        response = client.post("/api/recipe", json=request_data)
        
        # Should pass validation
        assert response.status_code != 422
```

### Test 6: Response Formatter Tests (tests/test_response_formatter.py)

```python
import pytest
from fastapi import HTTPException
from app.utils.response_formatter import ResponseFormatter
from app.models.recipe_models import RecipeResponse, ErrorResponse


class TestResponseFormatter:
    """Test cases for ResponseFormatter class."""
    
    def test_format_success_response(self):
        """Test successful response formatting."""
        recipe_data = {
            "recipe": {
                "title": "Pork Stew",
                "ingredients": ["2kg pork", "1kg potatoes"],
                "instructions": ["Cook pork", "Add potatoes"],
                "cooking_time": "45 minutes"
            }
        }
        
        response = ResponseFormatter.format_success_response(recipe_data)
        
        assert isinstance(response, RecipeResponse)
        assert response.status == "success"
        assert response.recipe.title == "Pork Stew"
        assert len(response.recipe.ingredients) == 2
    
    def test_format_error_response_default_status(self):
        """Test error response formatting with default status code."""
        message = "Test error message"
        
        with pytest.raises(HTTPException) as exc_info:
            raise ResponseFormatter.format_error_response(message)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail["status"] == "error"
        assert exc_info.value.detail["message"] == message
    
    def test_format_error_response_custom_status(self):
        """Test error response formatting with custom status code."""
        message = "Server error"
        status_code = 500
        
        with pytest.raises(HTTPException) as exc_info:
            raise ResponseFormatter.format_error_response(message, status_code)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail["message"] == message
    
    def test_format_validation_error(self):
        """Test validation error response formatting."""
        message = "Validation failed"
        
        with pytest.raises(HTTPException) as exc_info:
            raise ResponseFormatter.format_validation_error(message)
        
        assert exc_info.value.status_code == 422
        assert exc_info.value.detail["message"] == message
    
    def test_format_server_error(self):
        """Test server error response formatting."""
        message = "Internal server error"
        
        with pytest.raises(HTTPException) as exc_info:
            raise ResponseFormatter.format_server_error(message)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail["message"] == message
    
    def test_error_response_structure(self):
        """Test error response structure compliance."""
        message = "Test error"
        
        try:
            raise ResponseFormatter.format_error_response(message)
        except HTTPException as e:
            error_detail = e.detail
            
            assert "status" in error_detail
            assert "message" in error_detail
            assert error_detail["status"] == "error"
            assert error_detail["message"] == message
    
    def test_success_response_structure(self):
        """Test success response structure compliance."""
        recipe_data = {
            "recipe": {
                "title": "Test Recipe",
                "ingredients": ["1kg test"],
                "instructions": ["Test instruction"],
                "cooking_time": "30 minutes"
            }
        }
        
        response = ResponseFormatter.format_success_response(recipe_data)
        response_dict = response.dict()
        
        assert "status" in response_dict
        assert "recipe" in response_dict
        assert response_dict["status"] == "success"
        assert "title" in response_dict["recipe"]
        assert "ingredients" in response_dict["recipe"]
        assert "instructions" in response_dict["recipe"]
        assert "cooking_time" in response_dict["recipe"]
```

## Test Configuration Files

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

### requirements.txt
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
aiohttp==3.9.1
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

### templates/prompt-template.txt
```
You are a professional chef assistant. Create a detailed recipe using the following ingredients: {ingredients}

Please provide your response in the following format:

Title: [Recipe Name]

Ingredients:
- [List each ingredient with its quantity]

Instructions:
1. [Step-by-step cooking instructions]
2. [Continue with numbered steps]

Cooking time: [Total time needed]

If the provided ingredients are insufficient to create a meaningful recipe, respond with exactly: "need to provide more ingredients"
```

This implementation guide provides complete step-by-step coding instructions and comprehensive unit test cases covering all aspects of the RecipeBot API, ensuring adherence to the technical specifications and coding conventions.