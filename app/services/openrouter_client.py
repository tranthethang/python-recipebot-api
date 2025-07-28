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