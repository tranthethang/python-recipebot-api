import pytest
from unittest.mock import patch, AsyncMock, mock_open
from fastapi.testclient import TestClient

# Mock environment variables and template file before importing the app
with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'}), \
     patch('builtins.open', mock_open(read_data="Template {ingredients}")):
    from app.main import app
    from app.api.recipe_routes import get_recipe_generator

client = TestClient(app)

# Create a mock generator for validation tests
def get_mock_recipe_generator():
    mock_generator = AsyncMock()
    return mock_generator


class TestRecipeRoutes:
    """Test cases for recipe API routes."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.valid_request = {
            "ingredients": ["2kg pork", "1kg potatoes", "0.5kg onions"]
        }
        
        self.mock_success_response = {
            "status": "success",
            "recipe": {
                "title": "Pork and Potato Stew",
                "ingredients": ["2kg pork", "1kg potatoes", "0.5kg onions"],
                "instructions": ["Brown the pork", "Add vegetables", "Simmer"],
                "cooking_time": "45 minutes"
            }
        }
    
    @patch('app.api.recipe_routes.RecipeGenerator')
    def test_generate_recipe_success(self, mock_generator_class):
        """Test successful recipe generation endpoint."""
        mock_generator = AsyncMock()
        mock_generator.generate_recipe_from_ingredients.return_value = self.mock_success_response
        mock_generator_class.return_value = mock_generator
        
        response = client.post("/api/recipe", json=self.valid_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "recipe" in data
        assert data["recipe"]["title"] == "Pork and Potato Stew"
    
    @patch('app.api.recipe_routes.RecipeGenerator')
    def test_generate_recipe_insufficient_ingredients(self, mock_generator_class):
        """Test recipe generation with insufficient ingredients."""
        mock_generator = AsyncMock()
        mock_generator.generate_recipe_from_ingredients.return_value = {
            "status": "error",
            "message": "need to provide more ingredients"
        }
        mock_generator_class.return_value = mock_generator
        
        response = client.post("/api/recipe", json=self.valid_request)
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["status"] == "error"
        assert data["detail"]["message"] == "need to provide more ingredients"
    
    def test_generate_recipe_invalid_request_format(self):
        """Test recipe generation with invalid request format."""
        # Override the dependency to avoid initialization issues
        app.dependency_overrides[get_recipe_generator] = get_mock_recipe_generator
        
        try:
            invalid_request = {"invalid_field": "value"}
            
            response = client.post("/api/recipe", json=invalid_request)
            
            assert response.status_code == 422
        finally:
            # Clean up the override
            app.dependency_overrides.clear()
    
    def test_generate_recipe_empty_ingredients(self):
        """Test recipe generation with empty ingredients list."""
        # Override the dependency to avoid initialization issues
        app.dependency_overrides[get_recipe_generator] = get_mock_recipe_generator
        
        try:
            empty_request = {"ingredients": []}
            
            response = client.post("/api/recipe", json=empty_request)
            
            assert response.status_code == 422
        finally:
            # Clean up the override
            app.dependency_overrides.clear()
    
    def test_generate_recipe_ingredients_without_quantity(self):
        """Test recipe generation with ingredients missing quantities."""
        # Override the dependency to avoid initialization issues
        app.dependency_overrides[get_recipe_generator] = get_mock_recipe_generator
        
        try:
            invalid_request = {"ingredients": ["pork", "potatoes"]}
            
            response = client.post("/api/recipe", json=invalid_request)
            
            assert response.status_code == 422
        finally:
            # Clean up the override
            app.dependency_overrides.clear()
    
    @patch('app.api.recipe_routes.RecipeGenerator')
    def test_generate_recipe_server_error(self, mock_generator_class):
        """Test recipe generation with server error."""
        mock_generator = AsyncMock()
        mock_generator.generate_recipe_from_ingredients.side_effect = Exception("Server error")
        mock_generator_class.return_value = mock_generator
        
        response = client.post("/api/recipe", json=self.valid_request)
        
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["status"] == "error"
        assert "Internal server error occurred" in data["detail"]["message"]
    
    def test_health_check_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "RecipeBot API"