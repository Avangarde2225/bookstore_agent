import os
from typing import List, Dict, Any
from ..config.settings import logger, FEATURES_DIR
from ..utils.validators import validate_scenario_parameters, generate_parameter_combinations
from .step_generator import generate_step_definitions

def generate_feature_files(endpoints: List[Dict[str, Any]], model_name: str = "gpt-3.5-turbo") -> List[str]:
    """Generates comprehensive Gherkin feature files for each endpoint."""
    logger.info(f"Generating feature files for {len(endpoints)} endpoints")
    os.makedirs(FEATURES_DIR, exist_ok=True)
    feature_files = []
    step_files = []
    
    for endpoint in endpoints:
        path = endpoint["endpoint"]
        method = endpoint["method"]
        parameters = endpoint.get("parameters", [])
        request_body = endpoint.get("requestBody", {})
        responses = endpoint.get("responses", {})
        
        # Generate feature file name
        feature_name = f"{method}_{path.strip('/').replace('/', '_')}.feature"
        feature_path = os.path.join(FEATURES_DIR, feature_name)
        
        # Prepare parameter scenarios
        param_scenarios = []
        required_params = [p for p in parameters if p.get("required", False)]
        optional_params = [p for p in parameters if not p.get("required", False)]
        
        # Generate parameter combinations for scenario outlines
        param_combinations = generate_parameter_combinations(parameters)
        
        # Generate parameter test scenarios
        if required_params:
            param_scenarios.append(f"""
  @negative @validation
  Scenario: Missing required parameters
    Given I am making a {method} request to "{path}"
    When I send the request without required parameters
    Then the response status code should be 400
    And the response should indicate missing required parameters
""")
        
        if param_combinations:
            # Generate parameter rows for each combination
            param_rows = []
            for combo in param_combinations:
                for name, value in combo.items():
                    param_rows.append(f"      | {name} | {value} |")
            
            param_scenarios.append(f"""
  @validation
  Scenario Outline: Parameter combinations
    Given I am making a {method} request to "{path}"
    And I include the following parameters:
      | parameter | value |
{chr(10).join(param_rows)}
    When I send the request
    Then the response status code should be <status>
    And the response should contain <validation>

  Examples:
    | status | validation |
    | 200 | "successful response" |
    | 400 | "invalid parameters" |
""")
        
        # Generate request body scenarios if applicable
        body_scenarios = []
        if request_body and method in ["POST", "PUT", "PATCH"]:
            body_schema = request_body.get("content", {}).get("application/json", {}).get("schema", {})
            if body_schema:
                # Valid payload scenario
                body_scenarios.append(f"""
  @validation
  Scenario: Valid request body
    Given I am making a {method} request to "{path}"
    And I have the following valid request body:
      | field | value |
      {chr(10).join(f"      | {field} | {field} |" for field in body_schema.get('properties', {}).keys())}
    When I send the request
    Then the response status code should be 200
    And the response should contain valid data
""")
                
                # Invalid payload scenarios
                body_scenarios.append(f"""
  @negative @validation
  Scenario Outline: Invalid request body validation
    Given I am making a {method} request to "{path}"
    And I have the following invalid request body:
      | field | value |
      | <field> | <value> |
    When I send the request
    Then the response status code should be 400
    And the response should contain <validation>

  Examples:
    | field | value | validation |
    | title | "" | "Title cannot be empty" |
    | price | -1 | "Price must be positive" |
    | isbn | "invalid" | "Invalid ISBN format" |
""")
        
        # Generate response validation scenarios
        response_scenarios = []
        for status_code, response in responses.items():
            if status_code == "200":
                response_scenarios.append(f"""
  @validation
  Scenario: Successful response validation
    Given I am making a {method} request to "{path}"
    When I send the request with valid data
    Then the response status code should be 200
    And the response should contain valid data
    And the response should match the expected schema
""")
            elif status_code == "400":
                response_scenarios.append(f"""
  @negative @validation
  Scenario: Bad request validation
    Given I am making a {method} request to "{path}"
    When I send the request with invalid data
    Then the response status code should be 400
    And the response should contain error details
""")
            elif status_code == "401":
                response_scenarios.append(f"""
  @negative @auth
  Scenario: Unauthorized access
    Given I am making a {method} request to "{path}"
    When I send the request without authentication
    Then the response status code should be 401
    And the response should indicate authentication required
""")
            elif status_code == "404":
                response_scenarios.append(f"""
  @negative @validation
  Scenario: Resource not found
    Given I am making a {method} request to "{path}"
    When I send the request for a non-existent resource
    Then the response status code should be 404
    And the response should indicate resource not found
""")
        
        # Validate all scenarios before writing
        all_scenarios = param_scenarios + body_scenarios + response_scenarios
        valid_scenarios = []
        for scenario in all_scenarios:
            if validate_scenario_parameters(scenario, endpoint):
                valid_scenarios.append(scenario)
            else:
                logger.warning(f"Removing invalid scenario from {feature_name}")
        
        # Generate the complete feature file content
        feature_content = f"""Feature: {method} {path} API Endpoint

  As an API client
  I want to interact with the {path} endpoint
  So that I can {method.lower()} resources

  Background:
    Given the API service is running
    And I have valid authentication credentials

{chr(10).join(valid_scenarios)}
"""
        
        # Write the feature file
        with open(feature_path, 'w') as f:
            f.write(feature_content)
        
        logger.info(f"Generated feature file: {feature_path}")
        feature_files.append(feature_path)
        
        # Generate step definitions
        endpoint_info_with_status = endpoint.copy()
        endpoint_info_with_status["status_code"] = next(iter(responses.keys()), "200")
        step_file = generate_step_definitions(feature_path, endpoint_info_with_status)
        step_files.append(step_file)
    
    return feature_files, step_files 