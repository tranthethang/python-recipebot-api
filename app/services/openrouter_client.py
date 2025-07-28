import os
import json
from datetime import datetime
from typing import Dict, Any
import aiohttp
import asyncio
from app.utils.logger_config import get_logger

# Load environment variables if not in test environment
if not os.getenv('PYTEST_CURRENT_TEST'):
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

logger = get_logger(__name__)


class OpenRouterClient:
    """Handles communication with OpenRouter AI service."""
    
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    TIMEOUT_SECONDS = 30
    
    def __init__(self):
        self.api_key = self._get_api_key()
        self.model = self._get_model()
        self.headers = self._build_headers()
        self.log_requests = self._should_log_requests()
        if self.log_requests:
            self.logs_dir = self._ensure_logs_directory()
    
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
        request_timestamp = datetime.now()
        
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
                        
                        # Log request and response to file if enabled
                        if self.log_requests:
                            await self._log_request_response(
                                request_timestamp, prompt, payload, result, response.status
                            )
                        
                        return self._parse_api_response(result)
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error {response.status}: {error_text}")
                        
                        # Log failed request if enabled
                        if self.log_requests:
                            await self._log_request_response(
                                request_timestamp, prompt, payload, {"error": error_text}, response.status
                            )
                        
                        raise ConnectionError(f"API request failed: {response.status}")
                        
        except asyncio.TimeoutError:
            logger.error("OpenRouter API request timeout")
            # Log timeout if enabled
            if self.log_requests:
                await self._log_request_response(
                    request_timestamp, prompt, payload, {"error": "Request timeout"}, "TIMEOUT"
                )
            raise TimeoutError("AI service request timeout")
        except aiohttp.ClientError as e:
            logger.error(f"OpenRouter API connection error: {str(e)}")
            # Log connection error if enabled
            if self.log_requests:
                await self._log_request_response(
                    request_timestamp, prompt, payload, {"error": str(e)}, "CONNECTION_ERROR"
                )
            raise ConnectionError(f"API connection failed: {str(e)}")
    
    def _get_api_key(self) -> str:
        """Retrieve API key from environment variables."""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        return api_key
    
    def _get_model(self) -> str:
        """Retrieve model name from environment variables."""
        model = os.getenv("OPENROUTER_API_MODEL")
        if not model:
            # Fallback to default model if not set
            model = "anthropic/claude-3-haiku"
            logger.warning(f"OPENROUTER_API_MODEL not set, using default: {model}")
        return model
    
    def _should_log_requests(self) -> bool:
        """Check if request/response logging is enabled."""
        log_requests = os.getenv("OPENROUTER_LOG_REQUESTS", "false").lower()
        return log_requests in ("true", "1", "yes", "on")
    
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
            "model": self.model,
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
    
    def _ensure_logs_directory(self) -> str:
        """Ensure the logs directory exists and return its path."""
        logs_dir = os.path.join(os.getcwd(), "logs", "openrouter_requests")
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir
    
    async def _log_request_response(
        self, 
        timestamp: datetime, 
        prompt: str, 
        request_payload: Dict[str, Any], 
        response_data: Dict[str, Any], 
        status_code: Any
    ) -> None:
        """Log request and response to a separate file."""
        try:
            # Generate filename with timestamp
            filename = f"request_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}.json"
            filepath = os.path.join(self.logs_dir, filename)
            
            # Prepare log data
            log_data = {
                "timestamp": timestamp.isoformat(),
                "request": {
                    "url": self.BASE_URL,
                    "method": "POST",
                    "headers": {
                        # Log headers but mask the API key for security
                        **{k: v for k, v in self.headers.items() if k != "Authorization"},
                        "Authorization": "Bearer ***MASKED***"
                    },
                    "payload": request_payload,
                    "prompt": prompt
                },
                "response": {
                    "status_code": status_code,
                    "data": response_data
                }
            }
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Request-response logged to: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to log request-response: {str(e)}")