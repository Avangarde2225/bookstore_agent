import os
from typing import Dict, Any
from ..config.settings import logger, API_BASE_URL

def generate_conftest() -> str:
    """Generates the conftest.py file with proper pytest-bdd configuration."""
    logger.info("Generating conftest.py file")
    
    conftest_content = f'''import os
import pytest
import requests
from dotenv import load_dotenv
from pytest_bdd import given, when, then, parsers

# Load environment variables
load_dotenv()

# Base URL for the API
BASE_URL = "{API_BASE_URL}"

# Shared context for storing request/response data between steps
request_context = {{}}

def pytest_configure(config):
    """Configure pytest-bdd for feature discovery."""
    config.addinivalue_line(
        "markers",
        "bdd: mark test as bdd style test."
    )

@pytest.fixture(scope="session")
def api_base_url():
    """Fixture to provide the base URL for API requests."""
    return BASE_URL

@pytest.fixture(scope="session")
def auth_token():
    """Fixture to provide the authentication token."""
    token = os.getenv("API_AUTH_TOKEN")
    if not token:
        pytest.skip("API_AUTH_TOKEN environment variable is not set")
    return token

@pytest.fixture(scope="session")
def headers(auth_token):
    """Fixture to provide common headers for API requests."""
    return {{
        "Authorization": f"Bearer {{auth_token}}",
        "Content-Type": "application/json"
    }}

@pytest.fixture(scope="function")
def context():
    """Fixture to provide a clean context for each test."""
    request_context.clear()
    return request_context

# Common step definitions that can be reused across feature files
@given("the API service is running", target_fixture="api_service")
def api_service():
    """Verify the API service is accessible."""
    try:
        response = requests.get(f"{{BASE_URL}}/health")
        assert response.status_code == 200
        return True
    except requests.exceptions.RequestException:
        pytest.skip("API service is not accessible")

@given("I have valid authentication credentials", target_fixture="valid_auth")
def valid_auth(auth_token):
    """Ensure valid authentication credentials are available."""
    assert auth_token, "Authentication token is required"
    return auth_token
'''
    
    # Write the conftest.py file
    conftest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'tests', 'conftest.py')
    os.makedirs(os.path.dirname(conftest_path), exist_ok=True)
    
    with open(conftest_path, 'w') as f:
        f.write(conftest_content)
    
    logger.info(f"Generated conftest.py file: {conftest_path}")
    return conftest_path 