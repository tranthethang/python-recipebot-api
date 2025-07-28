# OpenRouter Request/Response Logging

This document describes the request/response logging feature for OpenRouter API calls.

## Overview

The OpenRouter client can optionally log all requests and responses to individual JSON files. This feature is useful for:

- Debugging API interactions
- Monitoring API usage and costs
- Analyzing response patterns
- Compliance and audit requirements

## Configuration

### Environment Variables

Add the following to your `.env` file:

```bash
# Enable/disable request logging (optional, defaults to false)
OPENROUTER_LOG_REQUESTS=true
```

Supported values for `OPENROUTER_LOG_REQUESTS`:
- `true`, `1`, `yes`, `on` - Enable logging
- `false`, `0`, `no`, `off` - Disable logging (default)

### Log Directory

When logging is enabled, log files are automatically created in:
```
logs/openrouter_requests/
```

The directory is created automatically if it doesn't exist.

## Log File Format

Each request-response pair is saved to a separate JSON file with the following naming convention:
```
request_YYYYMMDD_HHMMSS_microseconds.json
```

Example: `request_20250728_122815_892817.json`

### Log File Structure

```json
{
  "timestamp": "2025-07-28T12:28:15.892817",
  "request": {
    "url": "https://openrouter.ai/api/v1/chat/completions",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "HTTP-Referer": "http://localhost:8000",
      "X-Title": "RecipeBot API",
      "Authorization": "Bearer ***MASKED***"
    },
    "payload": {
      "model": "google/gemma-3-27b-it:free",
      "messages": [
        {
          "role": "user",
          "content": "Create a simple pasta recipe"
        }
      ],
      "max_tokens": 1000,
      "temperature": 0.7
    },
    "prompt": "Create a simple pasta recipe"
  },
  "response": {
    "status_code": 200,
    "data": {
      "choices": [
        {
          "message": {
            "content": "Here's a delicious pasta recipe..."
          }
        }
      ],
      "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 75,
        "total_tokens": 85
      }
    }
  }
}
```

## Security Considerations

- **API Key Protection**: The Authorization header is automatically masked in logs as `"Bearer ***MASKED***"`
- **File Permissions**: Log files are created with default system permissions
- **Storage**: Consider log rotation and cleanup for production environments

## Error Logging

The system logs all types of responses, including:

- **Successful responses** (status 200)
- **API errors** (4xx, 5xx status codes)
- **Timeout errors** (status: "TIMEOUT")
- **Connection errors** (status: "CONNECTION_ERROR")

## Usage Examples

### Enable Logging
```bash
# In .env file
OPENROUTER_LOG_REQUESTS=true
```

### Disable Logging
```bash
# In .env file
OPENROUTER_LOG_REQUESTS=false
# or simply omit the variable (defaults to false)
```

### Programmatic Check
```python
from app.services.openrouter_client import OpenRouterClient

client = OpenRouterClient()
if client.log_requests:
    print(f"Logging enabled. Files saved to: {client.logs_dir}")
else:
    print("Logging disabled")
```

## Performance Impact

- **Minimal overhead** when logging is disabled
- **Small I/O overhead** when logging is enabled (async file writing)
- **Storage usage** grows with each request (typically 1-5KB per log file)

## Maintenance

Consider implementing log rotation and cleanup strategies for production:

```bash
# Example: Keep only logs from last 30 days
find logs/openrouter_requests/ -name "*.json" -mtime +30 -delete
```

## Troubleshooting

### Logs Not Being Created

1. Check that `OPENROUTER_LOG_REQUESTS=true` in your `.env` file
2. Verify the application has write permissions to the `logs/` directory
3. Check application logs for any file system errors

### Large Log Files

If individual log files are unexpectedly large:
1. Check if the API is returning very long responses
2. Consider implementing response truncation for logging purposes
3. Monitor disk space usage

## Related Configuration

This logging feature works alongside other OpenRouter configuration:

```bash
# Complete OpenRouter configuration example
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_API_MODEL=google/gemma-3-27b-it:free
OPENROUTER_LOG_REQUESTS=true
```