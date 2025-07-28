# RecipeBot API

An AI-powered FastAPI application that generates recipe recommendations from ingredients using OpenRouter AI services.

## Features

- **Recipe Generation**: Generate recipes from a list of ingredients with quantities
- **Input Validation**: Comprehensive validation of ingredient formats and quantities
- **AI Integration**: Uses OpenRouter API for intelligent recipe generation
- **Error Handling**: Robust error handling with detailed error messages
- **Health Monitoring**: Health check endpoint for service monitoring
- **Comprehensive Testing**: Full test coverage with unit and integration tests

## Project Structure

```
python-recipebot-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── recipe_routes.py    # Recipe API endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── recipe_models.py    # Pydantic models for request/response
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ingredient_validator.py    # Ingredient validation logic
│   │   ├── openrouter_client.py      # OpenRouter API client
│   │   ├── prompt_generator.py       # AI prompt generation
│   │   └── recipe_generator.py       # Main recipe generation service
│   └── utils/
│       ├── __init__.py
│       ├── logger_config.py          # Logging configuration
│       └── response_formatter.py     # Response formatting utilities
├── templates/
│   └── recipe_prompt.txt             # AI prompt template
├── tests/                            # Comprehensive test suite
├── requirements.txt                  # Python dependencies
├── pytest.ini                       # Pytest configuration
├── .env.example                      # Environment variables example
└── README.md                         # This file
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd python-recipebot-api
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### OpenRouter API Key

1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Generate an API key
3. Add it to your `.env` file

## Usage

### Starting the Server

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

### API Endpoints

#### Health Check
```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "RecipeBot API"
}
```

#### Generate Recipe
```http
POST /api/recipe
```

**Request Body**:
```json
{
  "ingredients": [
    "2kg pork shoulder",
    "1kg potatoes",
    "500g onions",
    "3 cloves garlic"
  ]
}
```

**Success Response** (200):
```json
{
  "status": "success",
  "recipe": {
    "title": "Hearty Pork and Potato Stew",
    "ingredients": [
      "2kg pork shoulder",
      "1kg potatoes",
      "500g onions",
      "3 cloves garlic"
    ],
    "instructions": [
      "Cut pork shoulder into chunks",
      "Dice potatoes and onions",
      "Brown the pork in a large pot",
      "Add vegetables and simmer for 45 minutes"
    ],
    "cooking_time": "45 minutes"
  }
}
```

**Error Response** (400):
```json
{
  "detail": {
    "status": "error",
    "message": "need to provide more ingredients"
  }
}
```

### Input Validation

The API validates:
- **Ingredient format**: Each ingredient must include a quantity (numbers)
- **List size**: 1-20 ingredients maximum
- **Content**: Non-empty strings only

**Valid ingredients**:
- `"2kg pork"`
- `"500g flour"`
- `"3 large eggs"`
- `"1 cup milk"`

**Invalid ingredients**:
- `"pork"` (no quantity)
- `""` (empty string)
- `"   "` (whitespace only)

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_recipe_generator.py

# Run with verbose output
pytest -v
```

### Test Structure

- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing
- **API Tests**: Endpoint testing with mocked dependencies

## Development

### Code Quality Standards

The project follows strict coding conventions defined in `CODING_CONVENTIONS.md`:

- **Naming**: snake_case for variables/functions, PascalCase for classes
- **File Size**: Maximum 200 lines per file
- **Nesting**: Maximum 3 levels of nesting
- **SOLID Principles**: Single responsibility, dependency injection
- **Type Hints**: All functions have type annotations
- **Documentation**: Google-style docstrings

### Adding New Features

1. **Create feature branch**: `git checkout -b feature/new-feature`
2. **Write tests first**: Follow TDD approach
3. **Implement feature**: Follow coding conventions
4. **Run tests**: Ensure all tests pass
5. **Update documentation**: Update README and docstrings
6. **Submit PR**: Include test coverage and documentation

### Project Architecture

The application follows a clean architecture pattern:

- **API Layer** (`app/api/`): FastAPI routes and request handling
- **Service Layer** (`app/services/`): Business logic and external integrations
- **Model Layer** (`app/models/`): Data models and validation
- **Utility Layer** (`app/utils/`): Cross-cutting concerns (logging, formatting)

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup

For production deployment:

1. Set environment variables securely
2. Use a production ASGI server (uvicorn with workers)
3. Set up proper logging and monitoring
4. Configure reverse proxy (nginx)
5. Enable HTTPS

## Monitoring and Logging

The application includes:

- **Structured logging**: JSON format for production
- **Health checks**: `/health` endpoint for monitoring
- **Error tracking**: Comprehensive error logging
- **Request logging**: All API requests are logged

## Troubleshooting

### Common Issues

1. **OpenRouter API Key Error**:
   ```
   ValueError: OPENROUTER_API_KEY environment variable not set
   ```
   **Solution**: Set the `OPENROUTER_API_KEY` environment variable

2. **Import Errors**:
   ```
   ModuleNotFoundError: No module named 'app'
   ```
   **Solution**: Run from project root directory

3. **Test Failures**:
   ```
   Failed: async def functions are not natively supported
   ```
   **Solution**: Ensure `pytest-asyncio` is installed

### Debug Mode

Enable debug logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow coding conventions
4. Write comprehensive tests
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation at `/docs`