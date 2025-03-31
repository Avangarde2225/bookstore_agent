import pytest
from pytest_bdd import given, when, then, parsers
import os
import glob
import random
import requests
import json
from pathlib import Path
from typing import Dict, Any

# Global context dictionary for sharing data between steps
context = {}

# Import all step definition files
step_dir = "step_definitions"
step_files = glob.glob(os.path.join(step_dir, "test_*.py"))
for step_file in step_files:
    module_name = os.path.splitext(os.path.basename(step_file))[0]
    __import__(f"{step_dir}.{module_name}")

# Base URL for the API
BASE_URL = "https://bookstore.toolsqa.com"

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "tests" / "test_data"

# Create test data directory if it doesn't exist
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Common fixtures
@pytest.fixture
def random_number():
    """Fixture for generating random numbers"""
    return random.randint(10000, 99999)

@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Return the base URL for the API."""
    return BASE_URL

@pytest.fixture(scope="session")
def auth_token() -> str:
    """Return the authentication token."""
    return os.getenv("API_AUTH_TOKEN", "")

@pytest.fixture(scope="function")
def request_context() -> Dict[str, Any]:
    """Create a request context for API calls."""
    return {
        "method": None,
        "path": None,
        "headers": {
            "Authorization": f"Bearer {os.getenv('API_AUTH_TOKEN', '')}",
            "Content-Type": "application/json"
        },
        "params": {},
        "data": None,
        "response": None
    }

@pytest.fixture(scope="function")
def api_client(request_context: Dict[str, Any]) -> requests.Session:
    """Create an API client session."""
    session = requests.Session()
    session.headers.update(request_context["headers"])
    return session

@pytest.fixture(scope="function")
def test_data_dir() -> Path:
    """Return the test data directory."""
    return TEST_DATA_DIR

@pytest.fixture(scope="function")
def mock_response():
    """Create a mock response for testing."""
    class MockResponse:
        def __init__(self, status_code=200, json_data=None):
            self.status_code = status_code
            self._json = json_data or {}

        def json(self):
            return self._json

    return MockResponse

@pytest.fixture(scope="function")
def cleanup_test_data(test_data_dir: Path):
    """Clean up test data after tests."""
    yield
    # Add cleanup logic here if needed
    pass

# BDD fixtures
@pytest.fixture
def feature_file(request):
    """Fixture to get the current feature file"""
    return request.module.__file__.replace('.py', '.feature')

@pytest.fixture
def scenario(request):
    """Fixture to get the current scenario"""
    return request.node.name

# BDD hooks
def pytestbdd_before_scenario(request, feature, scenario):
    """Hook to run before each scenario"""
    context.clear()

def pytestbdd_after_scenario(request, feature, scenario):
    """Hook to run after each scenario"""
    context.clear()

# Register custom markers
def pytest_configure(config):
    """Register custom markers for BDD scenarios"""
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "api: mark test as API test")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
    config.addinivalue_line("markers", "crud: mark test as CRUD operation test")
    config.addinivalue_line("markers", "integration: mark test as integration test") 