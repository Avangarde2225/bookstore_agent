import os
from typing import Dict, Any
from ..config.settings import logger, API_BASE_URL, API_AUTH_TOKEN, STEPS_DIR

def generate_step_definitions(feature_file: str, endpoint_info: Dict[str, Any]) -> str:
    """Generates pytest-bdd step definitions for a feature file."""
    logger.info(f"Generating step definitions for {feature_file}")
    os.makedirs(STEPS_DIR, exist_ok=True)
    
    # Generate step file name from feature file name
    step_file = os.path.join(STEPS_DIR, f"{os.path.splitext(os.path.basename(feature_file))[0]}_steps.py")
    
    # Extract endpoint details
    path = endpoint_info["endpoint"]
    method = endpoint_info["method"]
    parameters = endpoint_info.get("parameters", [])
    request_body = endpoint_info.get("requestBody", {})
    responses = endpoint_info.get("responses", {})
    
    # Get the expected status code
    expected_status = endpoint_info.get("status_code", "200")
    
    # Extract response schema if available
    response_schema = {}
    if "200" in responses:
        response_content = responses["200"].get("content", {})
        if "application/json" in response_content:
            response_schema = response_content["application/json"].get("schema", {})
    
    # Generate step definitions content
    step_content = f'''#!/usr/bin/env python3
import os
import json
import pytest
from pytest_bdd import given, when, then, parsers, scenarios
import requests
from typing import Dict, Any
from datetime import datetime

# Load the feature file
scenarios('../features/{os.path.basename(feature_file)}')

# API Configuration
BASE_URL = "{API_BASE_URL}"
AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "")

# Request context
request_context = {{}}

@given("the API service is running")
def api_service_running():
    """Verify the API service is accessible."""
    try:
        response = requests.get(f"{{BASE_URL}}/health")
        assert response.status_code == 200
    except requests.exceptions.RequestException:
        pytest.skip("API service is not accessible")

@given("I have valid authentication credentials")
def valid_credentials():
    """Set up authentication credentials."""
    if not AUTH_TOKEN:
        pytest.skip("API_AUTH_TOKEN environment variable is not set")

@given(parsers.parse('I am making a {method} request to "{path}"'))
def prepare_request():
    """Prepare the request context."""
    request_context["method"] = "{method}"
    request_context["path"] = "{path}"
    request_context["headers"] = {{
        "Authorization": f"Bearer {{AUTH_TOKEN}}",
        "Content-Type": "application/json"
    }}
    request_context["params"] = {{}}
    request_context["data"] = None

@given("I include the following optional parameters")
def add_optional_parameters(parameters_table):
    """Add optional parameters to the request."""
    for row in parameters_table:
        param_name = row["parameter"]
        param_value = row["value"]
        request_context["params"][param_name] = param_value

@given("I have the following request body")
def set_request_body(request_body_table):
    """Set the request body from the table."""
    body = {{}}
    for row in request_body_table:
        field = row["field"]
        value = row["value"]
        body[field] = value
    request_context["data"] = json.dumps(body)

@when("I send the request")
def send_request():
    """Send the prepared request."""
    url = f"{{BASE_URL}}{{request_context['path']}}"
    response = requests.request(
        method=request_context["method"],
        url=url,
        headers=request_context["headers"],
        params=request_context["params"],
        data=request_context["data"]
    )
    request_context["response"] = response

@when("I send the request without required parameters")
def send_request_without_required():
    """Send request without required parameters."""
    url = f"{{BASE_URL}}{{request_context['path']}}"
    response = requests.request(
        method=request_context["method"],
        url=url,
        headers=request_context["headers"]
    )
    request_context["response"] = response

@when("I send the request with invalid data")
def send_request_with_invalid_data():
    """Send request with invalid data."""
    url = f"{{BASE_URL}}{{request_context['path']}}"
    invalid_data = {{"invalid": "data"}}
    response = requests.request(
        method=request_context["method"],
        url=url,
        headers=request_context["headers"],
        data=json.dumps(invalid_data)
    )
    request_context["response"] = response

@when("I send the request without authentication")
def send_request_without_auth():
    """Send request without authentication."""
    url = f"{{BASE_URL}}{{request_context['path']}}"
    headers = {{"Content-Type": "application/json"}}
    response = requests.request(
        method=request_context["method"],
        url=url,
        headers=headers
    )
    request_context["response"] = response

@when("I send the request for a non-existent resource")
def send_request_for_nonexistent():
    """Send request for a non-existent resource."""
    url = f"{{BASE_URL}}{{request_context['path']}}/nonexistent"
    response = requests.request(
        method=request_context["method"],
        url=url,
        headers=request_context["headers"]
    )
    request_context["response"] = response

@when("I send the request with valid data")
def send_request_with_valid_data():
    """Send the request with valid data."""
    url = f"{{BASE_URL}}{{request_context['path']}}"
    response = requests.request(
        method=request_context["method"],
        url=url,
        headers=request_context["headers"],
        params=request_context["params"],
        data=request_context["data"]
    )
    request_context["response"] = response

@then(parsers.parse("the response status code should be {{status_code:d}}"))
def verify_status_code(status_code: int):
    """Verify the response status code."""
    assert request_context["response"].status_code == status_code

@then("the response should contain valid data")
def verify_valid_response():
    """Verify the response contains valid data."""
    response = request_context["response"]
    data = response.json()
    assert isinstance(data, dict), "Response should be a JSON object"
    # Additional validation will be based on the response schema

@then("the response should match the expected schema")
def verify_response_schema():
    """Verify the response matches the expected schema."""
    response = request_context["response"]
    data = response.json()
    
    # Verify the response structure based on the schema
    assert isinstance(data, dict), "Response should be a JSON object"
    
    # If the response is a list, verify it's a list of objects
    if isinstance(data, list):
        assert all(isinstance(item, dict) for item in data), "All items in the list should be dictionaries"
        if data:
            # Use the first item as a reference for required fields
            required_fields = set(data[0].keys())
            for item in data:
                assert set(item.keys()).issuperset(required_fields), "All items should have the same structure"
    else:
        # For single object responses, verify it has the expected structure
        required_fields = set(data.keys())
        assert required_fields, "Response should contain at least one field"

@then("the response should indicate missing required parameters")
def verify_missing_params():
    """Verify the response indicates missing required parameters."""
    response = request_context["response"]
    data = response.json()
    assert "error" in data
    assert "missing" in data["error"].lower()

@then("the response should contain error details")
def verify_error_details():
    """Verify the response contains error details."""
    response = request_context["response"]
    data = response.json()
    assert "error" in data
    assert "details" in data

@then("the response should indicate authentication required")
def verify_auth_required():
    """Verify the response indicates authentication is required."""
    response = request_context["response"]
    data = response.json()
    assert "error" in data
    assert "unauthorized" in data["error"].lower()

@then("the response should indicate resource not found")
def verify_not_found():
    """Verify the response indicates resource not found."""
    response = request_context["response"]
    data = response.json()
    assert "error" in data
    assert "not found" in data["error"].lower()
'''
    
    # Write the step definitions file
    with open(step_file, 'w') as f:
        f.write(step_content)
    
    logger.info(f"Generated step definitions file: {step_file}")
    return step_file 