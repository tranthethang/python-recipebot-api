import pytest
from unittest.mock import patch, AsyncMock, MagicMock, mock_open
from app.services.recipe_generator import RecipeGenerator


class TestRecipeGenerator:
    """Test cases for RecipeGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_ai_response = """
        Title: Pork and Potato Stew
        
        Ingredients:
        - 2kg pork, cubed
        - 1kg potatoes, diced
        - 0.5kg onions, sliced
        
        Instructions:
        1. Brown the pork in a large pot
        2. Add onions and cook until soft
        3. Add potatoes and simmer for 30 minutes
        
        Cooking time: 45 minutes
        """
    
    @pytest.mark.asyncio
    @patch('app.services.recipe_generator.IngredientValidator')
    @patch('app.services.recipe_generator.PromptGenerator')
    @patch('app.services.recipe_generator.OpenRouterClient')
    async def test_generate_recipe_success(self, mock_client, mock_prompt_gen, mock_validator):
        """Test successful recipe generation."""
        # Setup mocks
        mock_validator.return_value.validate_ingredients_list.return_value = True
        mock_prompt_gen.return_value.generate_prompt.return_value = "Test prompt"
        mock_client.return_value.generate_recipe = AsyncMock(
            return_value={"content": self.mock_ai_response}
        )
        
        generator = RecipeGenerator()
        ingredients = ["2kg pork", "1kg potatoes", "0.5kg onions"]
        
        result = await generator.generate_recipe_from_ingredients(ingredients)
        
        assert result["status"] == "success"
        assert "recipe" in result
        assert result["recipe"]["title"] == "Pork and Potato Stew"
    
    @pytest.mark.asyncio
    @patch('app.services.recipe_generator.IngredientValidator')
    @patch('app.services.recipe_generator.PromptGenerator')
    @patch('app.services.recipe_generator.OpenRouterClient')
    async def test_generate_recipe_invalid_ingredients(self, mock_client, mock_prompt_gen, mock_validator):
        """Test recipe generation with invalid ingredients."""
        mock_validator.return_value.validate_ingredients_list.return_value = False
        
        generator = RecipeGenerator()
        ingredients = ["invalid ingredients"]
        
        result = await generator.generate_recipe_from_ingredients(ingredients)
        
        assert result["status"] == "error"
        assert result["message"] == "need to provide more ingredients"
    
    @pytest.mark.asyncio
    @patch('app.services.recipe_generator.IngredientValidator')
    @patch('app.services.recipe_generator.PromptGenerator')
    @patch('app.services.recipe_generator.OpenRouterClient')
    async def test_generate_recipe_ai_insufficient_response(self, mock_client, mock_prompt_gen, mock_validator):
        """Test AI response indicating insufficient ingredients."""
        mock_validator.return_value.validate_ingredients_list.return_value = True
        mock_prompt_gen.return_value.generate_prompt.return_value = "Test prompt"
        mock_client.return_value.generate_recipe = AsyncMock(
            return_value={"content": "need to provide more ingredients"}
        )
        
        generator = RecipeGenerator()
        ingredients = ["1kg ingredient"]
        
        result = await generator.generate_recipe_from_ingredients(ingredients)
        
        assert result["status"] == "error"
        assert result["message"] == "need to provide more ingredients"
    
    @pytest.mark.asyncio
    @patch('app.services.recipe_generator.IngredientValidator')
    @patch('app.services.recipe_generator.PromptGenerator')
    @patch('app.services.recipe_generator.OpenRouterClient')
    async def test_generate_recipe_exception(self, mock_client, mock_prompt_gen, mock_validator):
        """Test recipe generation with exception."""
        mock_validator.return_value.validate_ingredients_list.return_value = True
        mock_prompt_gen.return_value.generate_prompt.side_effect = Exception("Test error")
        
        generator = RecipeGenerator()
        ingredients = ["2kg pork"]
        
        result = await generator.generate_recipe_from_ingredients(ingredients)
        
        assert result["status"] == "error"
        assert "Recipe generation failed" in result["message"]
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'})
    @patch('builtins.open', mock_open(read_data="Template {ingredients}"))
    def test_extract_title_success(self):
        """Test successful title extraction."""
        generator = RecipeGenerator()
        content = "Title: Delicious Recipe\nOther content..."
        
        result = generator._extract_title(content)
        
        assert result == "Delicious Recipe"
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'})
    @patch('builtins.open', mock_open(read_data="Template {ingredients}"))
    def test_extract_title_no_match(self):
        """Test title extraction with no match."""
        generator = RecipeGenerator()
        content = "No title in this content"
        
        result = generator._extract_title(content)
        
        assert result == "Generated Recipe"
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'})
    @patch('builtins.open', mock_open(read_data="Template {ingredients}"))
    def test_extract_ingredients_success(self):
        """Test successful ingredients extraction."""
        generator = RecipeGenerator()
        content = """
        Ingredients:
        - 2kg pork
        - 1kg potatoes

        Instructions:
        1. Cook everything
        """
        
        result = generator._extract_ingredients(content)
        
        assert "2kg pork" in result
        assert "1kg potatoes" in result
        assert len(result) == 2
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'})
    @patch('builtins.open', mock_open(read_data="Template {ingredients}"))
    def test_extract_ingredients_no_match(self):
        """Test ingredients extraction with no match."""
        generator = RecipeGenerator()
        content = "No ingredients section"
        
        result = generator._extract_ingredients(content)
        
        assert result == ["Ingredients not specified"]
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'})
    @patch('builtins.open', mock_open(read_data="Template {ingredients}"))
    def test_extract_instructions_success(self):
        """Test successful instructions extraction."""
        generator = RecipeGenerator()
        content = """
        Instructions:
        1. First step
        2. Second step
        3. Third step
        """
        
        result = generator._extract_instructions(content)
        
        assert "First step" in result
        assert "Second step" in result
        assert "Third step" in result
        assert len(result) == 3
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'})
    @patch('builtins.open', mock_open(read_data="Template {ingredients}"))
    def test_extract_instructions_no_match(self):
        """Test instructions extraction with no match."""
        generator = RecipeGenerator()
        content = "No instructions section"
        
        result = generator._extract_instructions(content)
        
        assert result == ["Instructions not provided"]
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'})
    @patch('builtins.open', mock_open(read_data="Template {ingredients}"))
    def test_extract_cooking_time_success(self):
        """Test successful cooking time extraction."""
        generator = RecipeGenerator()
        content = "Cooking time: 45 minutes"
        
        result = generator._extract_cooking_time(content)
        
        assert result == "45 minutes"
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'})
    @patch('builtins.open', mock_open(read_data="Template {ingredients}"))
    def test_extract_cooking_time_no_match(self):
        """Test cooking time extraction with no match."""
        generator = RecipeGenerator()
        content = "No cooking time mentioned"
        
        result = generator._extract_cooking_time(content)
        
        assert result == "30 minutes"