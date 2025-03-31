# API Test Generator

A Python-based tool that automatically generates pytest-bdd test suites from Swagger/OpenAPI documentation. The tool uses OpenAI's GPT models to generate comprehensive test scenarios and step definitions.

## Project Structure

```
api_test_generator/
├── src/
│   ├── api/
│   │   └── swagger.py          # Swagger UI scraping and parsing
│   ├── config/
│   │   └── settings.py         # Configuration and environment setup
│   ├── generators/
│   │   ├── feature_generator.py # Feature file generation
│   │   ├── step_generator.py    # Step definition generation
│   │   ├── crud_generator.py    # CRUD scenario generation
│   │   └── conftest_generator.py # Pytest configuration generator
│   └── utils/
│       └── validators.py        # Parameter validation utilities
├── tests/
│   ├── features/              # Generated feature files
│   │   └── crud/             # CRUD scenario feature files
│   ├── steps/                # Generated step definitions
│   └── reports/              # Test execution reports
├── archive/                  # Archived/unused files
├── requirements.txt          # Project dependencies
├── pytest.ini               # Pytest configuration
├── conftest.py             # Pytest fixtures and configuration
└── .env                    # Environment variables
```

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- pip or pipenv for package management

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd api_test_generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_api_key_here
API_AUTH_TOKEN=your_auth_token_here  # Optional
API_BASE_URL=your_api_base_url       # Required
```

## Usage

### Generating Tests

Run the main script with a Swagger UI URL:

```bash
PYTHONPATH=$PYTHONPATH:. python src/main.py --swagger-url "https://your-api-url/swagger/" --model "gpt-3.5-turbo"
```

This will:
1. Create necessary test directories under `tests/`
2. Generate `conftest.py` with proper pytest-bdd configuration
3. Scrape the Swagger UI documentation
4. Generate feature files and step definitions
5. Create CRUD scenarios and integration tests

### Directory Structure

The generator creates the following structure under `tests/`:
- `features/` - Contains generated feature files
  - `crud/` - Contains end-to-end CRUD scenario features
- `steps/` - Contains step definition files
- `reports/` - Contains test execution reports

### Running Tests

Execute the generated tests using pytest:

```bash
pytest tests/features -v --html=tests/reports/report.html
```

### Test Reports

- HTML reports are generated in `tests/reports/report.html`
- Console output includes detailed test execution logs
- MLflow tracking is enabled for test generation metrics

### MLflow Integration

The test generation process is tracked using MLflow:
- Experiment name: "Swagger_Test_Generation"
- Tracked parameters:
  - swagger_url
  - model_name

## Features

- Dynamic test generation from Swagger/OpenAPI documentation
- Generic step definitions that work with any REST API
- Automatic schema validation based on API documentation
- Comprehensive CRUD scenario generation
- Configurable test generation using OpenAI models
- MLflow integration for tracking test generation metrics
- HTML test reports with detailed execution information

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `API_AUTH_TOKEN`: Authentication token for the API (if required)
- `API_BASE_URL`: Base URL of the API

### Pytest Configuration

The generated `conftest.py` includes:
- Common fixtures for API requests
- Shared step definitions
- Proper pytest-bdd configuration
- Environment variable handling

### Test Generation

The generator creates:
- Feature files with Gherkin syntax
- Step definitions with proper pytest-bdd decorators
- Schema-aware response validation
- Error handling and authentication checks
- CRUD operation scenarios

## Troubleshooting

1. OpenAI API Issues:
   - Verify your API key in `.env`
   - Check API rate limits
   - Ensure model availability

2. Test Generation Issues:
   - Check Swagger UI accessibility
   - Verify JSON response format
   - Check log output for errors

3. Test Execution Issues:
   - Review test reports in `tests/reports/`
   - Check console output for errors
   - Verify environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

