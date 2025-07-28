# RecipeBot API - Technical Documentation

## Overview
The RecipeBot API is a simple, compact service that generates recipe recommendations based on provided ingredients using AI technology via OpenRouter.

## API Endpoint

### POST /api/recipe

**Description:** Generates a recipe recommendation based on provided ingredients.

## Technical Flow

### 1. Receive Request
The API receives a POST request at `/api/recipe` endpoint.

### 2. Parameter Extraction
The system extracts the `ingredients` parameter from the request body.

**Expected Format:**
- Parameter: `ingredients` (required)
- Type: Array of strings
- Content: Cooking ingredients with quantities specified in kilograms
- Example: `["2kg pork", "1kg potatoes", "0.5kg onions"]`

### 3. Input Validation
The API validates incoming data:
- Checks if `ingredients` array is present
- Verifies the array is not empty
- Returns appropriate error response if validation fails

### 4. Prompt Generation
- Reads template from `prompt-template.txt` file
- Replaces placeholder with the provided ingredient list
- Generates complete AI prompt for recipe recommendation

### 5. OpenRouter Integration

#### API Key Retrieval
- Securely reads `API_KEY` from `.env` file
- Uses environment variable for OpenRouter authentication

#### Send Request to OpenRouter
- Utilizes OpenRouter SDK for Python
- Sends generated prompt to AI model
- Handles communication with external AI service

### 6. Process AI Response
The API processes the OpenRouter response:
- **Success Case:** Parse and format recipe recommendation
- **Failure Case:** Handle errors and generate fallback response
- **Insufficient Data:** Return "need to provide more ingredients" message

### 7. Logging
Comprehensive logging system tracks:
- Incoming requests with ingredients
- Prompt generation steps
- OpenRouter API calls and responses
- Processing outcomes
- Error conditions

All logs are written to file for monitoring and debugging purposes.

### 8. Return Response
Constructs and returns JSON response to client:
- **Success:** Recipe recommendation object
- **Error:** Appropriate error message with status codes

## Response Format

### Success Response
```json
{
  "status": "success",
  "recipe": {
    "title": "Recipe Name",
    "ingredients": [...],
    "instructions": [...],
    "cooking_time": "30 minutes"
  }
}
```

### Error Response
```json
{
  "status": "error",
  "message": "need to provide more ingredients"
}
```

## Technology Stack
- **Framework:** Python FastAPI
- **AI Integration:** OpenRouter SDK for Python
- **Configuration:** Environment variables (.env)
- **Template System:** Text file templates (prompt-template.txt)
- **Logging:** File-based logging system

## Security Considerations
- API keys stored securely in environment variables
- Input validation prevents malformed requests
- Error handling prevents information leakage
- Comprehensive logging for audit trails