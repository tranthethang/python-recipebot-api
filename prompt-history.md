Prompt History
---


### Prompt 1
Join me to discuss a Python FastAPI - RecipeBot API. This is an AI tool that suggests recipes based on ingredients.
You give it a list of ingredients (for example, ['pork', 'potatoes', 'onions']). The tool then sends your ingredients to an AI system, which finds the best recipe for you.
Our discussion is strictly about business, not about writing code.

### Prompt 2
- This tool is for people who cook at home.
- We made this app to show what our AI can do, not to sell it or make money right now.
- We use AI just to create new recipes or find existing ones. This is its main purpose.

### Prompt 3
I need some suggestions because I don't have a full idea yet. I want to build a very simple, compact API. Its only function is this: you give it ingredients, and an AI (via OpenRouter) finds the best recipe. If no recipe is found, it will say 'need to provide more ingredients'.

### Prompt 4
I agree with the main ideas. The goal is just to show off the technology.

### Prompt 5
- Create a technical documentation file (.md). This document describes the technical flow for our recipe recommendation API. Endpoint: "POST /api/recipe"
- Receive Request: The API receives a POST request at /api/recipe.
- Parameter Extraction: It extracts the ingredients from the request body. This parameter must be an array of cooking ingredients, with each ingredient's quantity specified in kilograms.
- Input Validation: The API validates the incoming data. It specifically checks if the ingredient array is present and not empty. If validation fails, an appropriate error response is returned.
- Prompt Generation: A prompt-template.txt file is used to create the AI prompt. This template includes a placeholder that will be filled with the provided ingredient list.
- OpenRouter Integration: The OpenRouter SDK for Python is used to interact with the AI model.
- API Key Retrieval: The API_KEY for OpenRouter is securely read from the .env file.
- Send Request to OpenRouter: The generated prompt is sent as a request to the OpenRouter AI model.
- Process AI Response: The API handles the response from OpenRouter, distinguishing between success and failure cases.
- Logging: Each significant processing step, including requests and responses, is logged to a file for monitoring and debugging purposes.
- Return Response: Finally, the API constructs and returns the appropriate response to the client, which will either be a recommended recipe or an error message.

### Prompt 6
Create a naming convention and coding convention document for the project. Add the following mandatory standards:
1. Naming and Coding Rules: Create a document that explains our naming and coding rules. These rules must match the standards used in Python FastAPI.
2. Code Quality Principles: All code must follow these important principles: SOLID, DRY (Don't Repeat Yourself), KISS (Keep It Simple, Stupid), YAGNI (You Ain't Gonna Need It), and general Clean Code practices.
3. File Size Limit: Each code file should not be longer than 200 lines.
4. Nesting Limit: Do not nest code (like loops or 'if' statements) more than 3 levels deep.


### Prompt 7
From the TECHNICAL_DOCS.md document - business description, and the CODING_CONVENTIONS.md document - coding standards, naming.
Create a more detailed document to:
- list each step for coding,
- all unit-test cases.