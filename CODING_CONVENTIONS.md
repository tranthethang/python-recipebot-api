# RecipeBot API - Coding Conventions & Standards

## Overview
This document establishes mandatory coding standards for the RecipeBot API project, ensuring consistency, maintainability, and adherence to Python FastAPI best practices.

## 1. Naming Conventions

### Variables and Functions
- Use **snake_case** for all variables and function names
- Use descriptive, meaningful names
- Avoid abbreviations unless widely understood

```python
# Good
ingredient_list = []
user_request_data = {}

def validate_ingredients(ingredients: list) -> bool:
    pass

def process_openrouter_response(response: dict) -> dict:
    pass

# Bad
ing_lst = []
usrReqData = {}
def valIng(ing):
    pass
```

### Classes
- Use **PascalCase** for class names
- Use noun phrases that clearly describe the purpose

```python
# Good
class RecipeGenerator:
    pass

class OpenRouterClient:
    pass

class IngredientValidator:
    pass

# Bad
class recipeGenerator:
    pass

class openrouterAPI:
    pass
```

### Constants
- Use **UPPER_SNAKE_CASE** for constants
- Define all constants at module level

```python
# Good
MAX_INGREDIENTS = 20
API_TIMEOUT = 30
DEFAULT_COOKING_TIME = "30 minutes"

# Bad
maxIngredients = 20
api_timeout = 30
```

### Files and Modules
- Use **snake_case** for file names
- Use descriptive names that indicate purpose

```python
# Good
recipe_generator.py
openrouter_client.py
ingredient_validator.py

# Bad
RecipeGenerator.py
openrouterAPI.py
validator.py
```

### FastAPI Specific Conventions
- Use **snake_case** for endpoint paths
- Use descriptive endpoint names

```python
# Good
@app.post("/api/recipe")
@app.get("/health_check")

# Bad
@app.post("/api/Recipe")
@app.get("/healthCheck")
```

## 2. Code Quality Principles

### SOLID Principles

#### Single Responsibility Principle (SRP)
Each class/function should have one reason to change.

```python
# Good - Each class has single responsibility
class IngredientValidator:
    def validate(self, ingredients: list) -> bool:
        pass

class RecipeGenerator:
    def generate(self, ingredients: list) -> dict:
        pass

# Bad - Multiple responsibilities
class RecipeHandler:
    def validate_ingredients(self, ingredients: list) -> bool:
        pass
    
    def call_openrouter_api(self, prompt: str) -> dict:
        pass
    
    def log_request(self, data: dict) -> None:
        pass
```

#### Open/Closed Principle (OCP)
Open for extension, closed for modification.

```python
# Good - Use abstract base classes
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def generate_recipe(self, prompt: str) -> dict:
        pass

class OpenRouterProvider(AIProvider):
    def generate_recipe(self, prompt: str) -> dict:
        pass
```

#### Liskov Substitution Principle (LSP)
Derived classes must be substitutable for base classes.

#### Interface Segregation Principle (ISP)
Clients should not depend on interfaces they don't use.

#### Dependency Inversion Principle (DIP)
Depend on abstractions, not concretions.

### DRY (Don't Repeat Yourself)
Eliminate code duplication through functions, classes, and modules.

```python
# Good
def format_error_response(message: str, status_code: int = 400) -> dict:
    return {"error": message, "status_code": status_code}

# Use the function
validation_error = format_error_response("Invalid ingredients")
api_error = format_error_response("API timeout", 500)

# Bad - Repeated code
validation_error = {"error": "Invalid ingredients", "status_code": 400}
api_error = {"error": "API timeout", "status_code": 500}
```

### KISS (Keep It Simple, Stupid)
Write simple, readable code. Avoid unnecessary complexity.

```python
# Good - Simple and clear
def is_ingredient_list_valid(ingredients: list) -> bool:
    return ingredients is not None and len(ingredients) > 0

# Bad - Unnecessarily complex
def is_ingredient_list_valid(ingredients: list) -> bool:
    if ingredients:
        if isinstance(ingredients, list):
            if len(ingredients) > 0:
                return True
            else:
                return False
        else:
            return False
    else:
        return False
```

### YAGNI (You Ain't Gonna Need It)
Don't implement features until they're actually needed.

```python
# Good - Only implement what's needed now
class RecipeGenerator:
    def generate_recipe(self, ingredients: list) -> dict:
        pass

# Bad - Adding unnecessary features
class RecipeGenerator:
    def generate_recipe(self, ingredients: list) -> dict:
        pass
    
    def save_recipe_to_database(self, recipe: dict) -> None:  # Not needed yet
        pass
    
    def share_recipe_on_social_media(self, recipe: dict) -> None:  # Not needed yet
        pass
```

### Clean Code Practices

#### Function Guidelines
- Functions should do one thing
- Keep functions small (ideally under 20 lines)
- Use descriptive names
- Minimize parameters (max 3-4)

```python
# Good
def validate_ingredient_format(ingredient: str) -> bool:
    """Check if ingredient has proper format with quantity."""
    return " " in ingredient and any(char.isdigit() for char in ingredient)

def extract_quantity_from_ingredient(ingredient: str) -> str:
    """Extract quantity portion from ingredient string."""
    return ingredient.split()[0]

# Bad
def process_ingredient(ingredient: str, validate: bool = True, 
                      extract: bool = False, format_check: bool = True) -> tuple:
    # 50+ lines of mixed responsibilities
    pass
```

## 3. File Size Limit
**Maximum 200 lines per file**

- Split large files into smaller, focused modules
- Use clear module boundaries
- Each file should have a single, well-defined purpose

```python
# Good structure
# recipe_generator.py (150 lines)
# ingredient_validator.py (120 lines)
# openrouter_client.py (180 lines)

# Bad
# main.py (500 lines) - Too large, split into modules
```

## 4. Nesting Limit
**Maximum 3 levels of nesting**

```python
# Good - 2 levels of nesting
def process_recipe_request(ingredients: list) -> dict:
    if ingredients:
        for ingredient in ingredients:
            if not validate_ingredient(ingredient):
                return create_error_response("Invalid ingredient")
    return generate_recipe(ingredients)

# Bad - 4 levels of nesting (exceeds limit)
def process_recipe_request(ingredients: list) -> dict:
    if ingredients:  # Level 1
        for ingredient in ingredients:  # Level 2
            if validate_ingredient(ingredient):  # Level 3
                if has_quantity(ingredient):  # Level 4 - TOO DEEP
                    process_ingredient(ingredient)

# Better - Extract to separate functions
def process_recipe_request(ingredients: list) -> dict:
    if not ingredients:
        return create_error_response("No ingredients provided")
    
    validated_ingredients = validate_all_ingredients(ingredients)
    if not validated_ingredients:
        return create_error_response("Invalid ingredients")
    
    return generate_recipe(validated_ingredients)

def validate_all_ingredients(ingredients: list) -> list:
    validated = []
    for ingredient in ingredients:
        if validate_ingredient(ingredient) and has_quantity(ingredient):
            validated.append(ingredient)
    return validated
```

## 5. Additional Python FastAPI Standards

### Type Hints
Always use type hints for function parameters and return values.

```python
from typing import List, Dict, Optional

def validate_ingredients(ingredients: List[str]) -> bool:
    pass

def generate_recipe(ingredients: List[str]) -> Dict[str, any]:
    pass

async def get_recipe(ingredients: List[str]) -> Optional[Dict[str, any]]:
    pass
```

### Docstrings
Use Google-style docstrings for all functions and classes.

```python
def validate_ingredients(ingredients: List[str]) -> bool:
    """Validate the provided ingredients list.
    
    Args:
        ingredients: List of ingredient strings with quantities
        
    Returns:
        True if all ingredients are valid, False otherwise
        
    Raises:
        ValueError: If ingredients list is None
    """
    pass
```

### Error Handling
Use specific exception types and proper error messages.

```python
# Good
try:
    response = await openrouter_client.generate_recipe(prompt)
except TimeoutError:
    logger.error("OpenRouter API timeout")
    raise HTTPException(status_code=504, detail="AI service timeout")
except ConnectionError:
    logger.error("OpenRouter API connection failed")
    raise HTTPException(status_code=503, detail="AI service unavailable")

# Bad
try:
    response = await openrouter_client.generate_recipe(prompt)
except Exception as e:
    raise HTTPException(status_code=500, detail="Something went wrong")
```

## 6. Enforcement
These conventions are mandatory for all code contributions. Code reviews must verify adherence to these standards before merging.