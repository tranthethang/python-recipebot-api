import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import aiohttp
import asyncio
import os
import json
import tempfile
from app.services.openrouter_client import OpenRouterClient


class TestOpenRouterClient:
    """Test cases for OpenRouterClient class."""
    
    def setup_method(self, method):
        """Set up test fixtures."""
        with patch.dict('os.environ', {
            'OPENROUTER_API_KEY': 'test-api-key',
            'OPENROUTER_API_MODEL': 'anthropic/claude-3-haiku',
            'OPENROUTER_LOG_REQUESTS': 'false'
        }):
            self.client = OpenRouterClient()
        self.mock_response_data = {
            "choices": [
                {
                    "message": {
                        "content": "Test recipe content"
                    }
                }
            ]
        }
    
    @pytest.mark.asyncio
    @patch.dict('os.environ', {
        'OPENROUTER_API_KEY': 'test-api-key',
        'OPENROUTER_API_MODEL': 'anthropic/claude-3-haiku',
        'OPENROUTER_LOG_REQUESTS': 'false'
    })
    @patch('aiohttp.ClientSession.post')
    async def test_generate_recipe_success(self, mock_post):
        """Test successful recipe generation."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=self.mock_response_data)
        mock_post.return_value.__aenter__.return_value = mock_response
        
        result = await self.client.generate_recipe("Test prompt")
        
        assert result["content"] == "Test recipe content"
        assert "raw_response" in result
    
    @pytest.mark.asyncio
    @patch.dict('os.environ', {
        'OPENROUTER_API_KEY': 'test-api-key',
        'OPENROUTER_API_MODEL': 'anthropic/claude-3-haiku',
        'OPENROUTER_LOG_REQUESTS': 'false'
    })
    @patch('aiohttp.ClientSession.post')
    async def test_generate_recipe_api_error(self, mock_post):
        """Test API error response."""
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value="Bad request")
        mock_post.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(ConnectionError, match="API request failed: 400"):
            await self.client.generate_recipe("Test prompt")
    
    @pytest.mark.asyncio
    @patch.dict('os.environ', {
        'OPENROUTER_API_KEY': 'test-api-key',
        'OPENROUTER_API_MODEL': 'anthropic/claude-3-haiku',
        'OPENROUTER_LOG_REQUESTS': 'false'
    })
    @patch('aiohttp.ClientSession.post')
    async def test_generate_recipe_timeout(self, mock_post):
        """Test request timeout."""
        mock_post.side_effect = asyncio.TimeoutError()
        
        with pytest.raises(TimeoutError, match="AI service request timeout"):
            await self.client.generate_recipe("Test prompt")
    
    @pytest.mark.asyncio
    @patch.dict('os.environ', {
        'OPENROUTER_API_KEY': 'test-api-key',
        'OPENROUTER_API_MODEL': 'anthropic/claude-3-haiku',
        'OPENROUTER_LOG_REQUESTS': 'false'
    })
    @patch('aiohttp.ClientSession.post')
    async def test_generate_recipe_connection_error(self, mock_post):
        """Test connection error."""
        mock_post.side_effect = aiohttp.ClientError("Connection failed")
        
        with pytest.raises(ConnectionError, match="API connection failed"):
            await self.client.generate_recipe("Test prompt")
    
    def test_get_api_key_missing(self):
        """Test missing API key environment variable."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OPENROUTER_API_KEY environment variable not set"):
                OpenRouterClient()
    
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-api-key'}, clear=True)
    def test_get_model_fallback(self):
        """Test model fallback when OPENROUTER_API_MODEL is not set."""
        client = OpenRouterClient()
        assert client.model == "anthropic/claude-3-haiku"
    
    @patch.dict('os.environ', {
        'OPENROUTER_API_KEY': 'test-api-key',
        'OPENROUTER_API_MODEL': 'anthropic/claude-3-haiku',
        'OPENROUTER_LOG_REQUESTS': 'false'
    })
    def test_build_headers(self):
        """Test header building."""
        headers = self.client._build_headers()
        
        assert headers["Authorization"] == "Bearer test-api-key"
        assert headers["Content-Type"] == "application/json"
        assert "HTTP-Referer" in headers
        assert "X-Title" in headers
    
    @patch.dict('os.environ', {
        'OPENROUTER_API_KEY': 'test-api-key',
        'OPENROUTER_API_MODEL': 'anthropic/claude-3-haiku',
        'OPENROUTER_LOG_REQUESTS': 'false'
    })
    def test_build_request_payload(self):
        """Test request payload building."""
        payload = self.client._build_request_payload("Test prompt")
        
        assert payload["model"] == "anthropic/claude-3-haiku"
        assert payload["messages"][0]["content"] == "Test prompt"
        assert payload["max_tokens"] == 1000
        assert payload["temperature"] == 0.7
    
    @patch.dict('os.environ', {
        'OPENROUTER_API_KEY': 'test-api-key',
        'OPENROUTER_API_MODEL': 'anthropic/claude-3-haiku',
        'OPENROUTER_LOG_REQUESTS': 'false'
    })
    def test_parse_api_response_success(self):
        """Test successful API response parsing."""
        result = self.client._parse_api_response(self.mock_response_data)
        
        assert result["content"] == "Test recipe content"
        assert result["raw_response"] == self.mock_response_data
    
    @patch.dict('os.environ', {
        'OPENROUTER_API_KEY': 'test-api-key',
        'OPENROUTER_API_MODEL': 'anthropic/claude-3-haiku',
        'OPENROUTER_LOG_REQUESTS': 'false'
    })
    def test_parse_api_response_invalid_format(self):
        """Test parsing invalid API response format."""
        invalid_response = {"invalid": "format"}
        
        with pytest.raises(ValueError, match="Invalid API response"):
            self.client._parse_api_response(invalid_response)
    
    @pytest.mark.asyncio
    @patch.dict('os.environ', {
        'OPENROUTER_API_KEY': 'test-api-key',
        'OPENROUTER_API_MODEL': 'anthropic/claude-3-haiku',
        'OPENROUTER_LOG_REQUESTS': 'true'
    })
    @patch('aiohttp.ClientSession.post')
    async def test_request_response_logging(self, mock_post):
        """Test that requests and responses are logged to files."""
        # Create a new client with logging enabled
        client = OpenRouterClient()
        
        # Setup mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=self.mock_response_data)
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(client, 'logs_dir', temp_dir):
                # Make request
                result = await client.generate_recipe("Test prompt for logging")
                
                # Check that log file was created
                log_files = os.listdir(temp_dir)
                assert len(log_files) == 1
                assert log_files[0].startswith("request_")
                assert log_files[0].endswith(".json")
                
                # Check log file content
                log_file_path = os.path.join(temp_dir, log_files[0])
                with open(log_file_path, 'r') as f:
                    log_data = json.load(f)
                
                # Verify log structure
                assert "timestamp" in log_data
                assert "request" in log_data
                assert "response" in log_data
                
                # Verify request data
                assert log_data["request"]["prompt"] == "Test prompt for logging"
                assert log_data["request"]["payload"]["model"] == "anthropic/claude-3-haiku"
                assert log_data["request"]["headers"]["Authorization"] == "Bearer ***MASKED***"
                
                # Verify response data
                assert log_data["response"]["status_code"] == 200
                assert log_data["response"]["data"] == self.mock_response_data