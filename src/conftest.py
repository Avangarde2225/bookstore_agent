import pytest
import os
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture to provide the test data directory path."""
    return Path(__file__).parent / "tests" / "data"

@pytest.fixture(scope="session")
def output_dir():
    """Fixture to provide the output directory path for generated files."""
    output_path = Path(__file__).parent / "tests" / "output"
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path

@pytest.fixture(scope="function")
def features_dir(output_dir):
    """Fixture to provide a clean features directory for each test."""
    features_path = output_dir / "features"
    if features_path.exists():
        shutil.rmtree(features_path)
    features_path.mkdir(parents=True, exist_ok=True)
    return features_path

@pytest.fixture(scope="function")
def steps_dir(output_dir):
    """Fixture to provide a clean steps directory for each test."""
    steps_path = output_dir / "steps"
    if steps_path.exists():
        shutil.rmtree(steps_path)
    steps_path.mkdir(parents=True, exist_ok=True)
    return steps_path

@pytest.fixture(scope="function")
def reports_dir(output_dir):
    """Fixture to provide a clean reports directory for each test."""
    reports_path = output_dir / "reports"
    if reports_path.exists():
        shutil.rmtree(reports_path)
    reports_path.mkdir(parents=True, exist_ok=True)
    return reports_path

@pytest.fixture(scope="session")
def sample_swagger_html():
    """Fixture to provide sample Swagger UI HTML content."""
    return """
    <div class="opblock-get">
        <div class="opblock-summary-method">GET</div>
        <div class="opblock-summary-path">/books</div>
        <div class="opblock-summary-description">Get all books</div>
        <div class="opblock-parameters">
            <div class="parameter">
                <div class="parameter-name">limit</div>
                <div class="parameter-in">query</div>
                <div class="parameter-required">false</div>
            </div>
        </div>
    </div>
    """

@pytest.fixture(scope="session")
def sample_endpoint_info():
    """Fixture to provide sample endpoint information."""
    return {
        "endpoint": "/books",
        "method": "GET",
        "parameters": [
            {
                "name": "limit",
                "in": "query",
                "required": False,
                "type": "integer",
                "description": "Number of books to return"
            }
        ],
        "responses": {
            "200": {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "title": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }

@pytest.fixture(scope="session")
def mock_openai_response():
    """Fixture to provide a mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": """
                    {
                        "endpoint": "/books",
                        "method": "GET",
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "required": false,
                                "type": "integer",
                                "description": "Number of books to return"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "string"},
                                                    "title": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    """
                }
            }
        ]
    } 