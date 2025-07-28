import pytest
from unittest.mock import patch, mock_open
from app.services.prompt_generator import PromptGenerator


class TestPromptGenerator:
    """Test cases for PromptGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_template = "Generate recipe with {ingredients}"
        
    @patch("builtins.open", new_callable=mock_open, read_data="Generate recipe with {ingredients}")
    def test_generate_prompt_success(self, mock_file):
        """Test successful prompt generation."""
        generator = PromptGenerator()
        ingredients = ["2kg pork", "1kg potatoes"]
        
        result = generator.generate_prompt(ingredients)
        
        assert "2kg pork, 1kg potatoes" in result
        assert "Generate recipe with" in result
    
    def test_generate_prompt_empty_ingredients(self):
        """Test prompt generation with empty ingredients list."""
        with patch("builtins.open", mock_open(read_data="Template {ingredients}")):
            generator = PromptGenerator()
            
            with pytest.raises(ValueError, match="Cannot generate prompt from empty ingredients list"):
                generator.generate_prompt([])
    
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_load_template_empty_file(self, mock_file):
        """Test loading empty template file."""
        with pytest.raises(ValueError, match="Template file is empty"):
            PromptGenerator()
    
    @patch("builtins.open", new_callable=mock_open, read_data="Template without placeholder")
    def test_load_template_missing_placeholder(self, mock_file):
        """Test loading template without ingredients placeholder."""
        with pytest.raises(ValueError, match="Template missing ingredients placeholder"):
            PromptGenerator()
    
    @patch("builtins.open", side_effect=FileNotFoundError())
    def test_load_template_file_not_found(self, mock_file):
        """Test loading non-existent template file."""
        with pytest.raises(FileNotFoundError):
            PromptGenerator()
    
    @patch("builtins.open", new_callable=mock_open, read_data="Recipe template {ingredients}")
    def test_format_ingredients_list(self, mock_file):
        """Test ingredients list formatting."""
        generator = PromptGenerator()
        ingredients = ["2kg pork", "1kg potatoes", "0.5kg onions"]
        
        result = generator._format_ingredients_list(ingredients)
        
        assert result == "2kg pork, 1kg potatoes, 0.5kg onions"
    
    @patch("builtins.open", new_callable=mock_open, read_data="Recipe template {ingredients}")
    def test_format_single_ingredient(self, mock_file):
        """Test single ingredient formatting."""
        generator = PromptGenerator()
        ingredients = ["2kg pork"]
        
        result = generator._format_ingredients_list(ingredients)
        
        assert result == "2kg pork"