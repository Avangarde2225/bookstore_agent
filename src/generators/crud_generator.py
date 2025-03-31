import os
from typing import List, Dict, Any
from ..config.settings import logger, CRUD_DIR
from .step_generator import generate_step_definitions

def generate_crud_e2e_scenarios(endpoints: List[Dict[str, Any]]) -> Dict[str, str]:
    """Generate CRUD end-to-end scenarios by analyzing endpoint patterns."""
    logger.info("Starting CRUD scenario generation")
    
    # Group endpoints by their base path
    endpoint_groups = {}
    for endpoint in endpoints:
        base_path = endpoint['endpoint'].split('/')[1]  # e.g., 'Account' or 'BookStore'
        if base_path not in endpoint_groups:
            endpoint_groups[base_path] = []
        endpoint_groups[base_path].append(endpoint)
    
    logger.info(f"Found {len(endpoint_groups)} endpoint groups")
    crud_scenarios = {}
    
    # Generate CRUD scenarios for each group
    for group_name, group_endpoints in endpoint_groups.items():
        logger.info(f"Processing group: {group_name}")
        feature_name = f"test_{group_name.lower()}_crud_e2e.feature"
        
        # Analyze endpoints to find CRUD operations
        crud_ops = {
            'create': [e for e in group_endpoints if e['method'] == 'POST'],
            'read': [e for e in group_endpoints if e['method'] == 'GET'],
            'update': [e for e in group_endpoints if e['method'] in ['PUT', 'PATCH']],
            'delete': [e for e in group_endpoints if e['method'] == 'DELETE']
        }
        
        logger.info(f"Found CRUD operations for {group_name}: {[k for k, v in crud_ops.items() if v]}")
        
        # Generate the feature file content with dynamic setup
        content = f"""Feature: End-to-End CRUD Testing for {group_name} API

Background:
    Given the API service is running
    And I am authenticated with valid credentials
"""
        
        # Generate CRUD scenarios dynamically based on available operations
        for operation, endpoints in crud_ops.items():
            if endpoints:
                endpoint = endpoints[0]  # Use the first matching endpoint
                logger.info(f"Adding {operation} scenario for {endpoint['endpoint']}")
                
                # Generate scenario based on operation type
                if operation == 'create':
                    content += f"""
@e2e @crud @{operation}
Scenario: Create {group_name} Resource
    Given I prepare test data for {group_name.lower()} creation
    When I send a POST request to "{endpoint['endpoint']}" with valid data
    Then the response status code should be 200
    And I store the created {group_name.lower()} ID
"""
                elif operation == 'read':
                    content += f"""
@e2e @crud @{operation}
Scenario: Read {group_name} Resource
    Given I have a valid {group_name.lower()} ID
    When I send a GET request to "{endpoint['endpoint']}"
    Then the response status code should be 200
    And the response should contain valid {group_name.lower()} data
"""
                elif operation == 'update':
                    content += f"""
@e2e @crud @{operation}
Scenario: Update {group_name} Resource
    Given I have a valid {group_name.lower()} ID
    And I prepare updated data for {group_name.lower()}
    When I send a {endpoint['method']} request to "{endpoint['endpoint']}"
    Then the response status code should be 200
    And the {group_name.lower()} should be updated
"""
                elif operation == 'delete':
                    content += f"""
@e2e @crud @{operation}
Scenario: Delete {group_name} Resource
    Given I have a valid {group_name.lower()} ID
    When I send a DELETE request to "{endpoint['endpoint']}"
    Then the response status code should be 200
    And the {group_name.lower()} should be deleted
"""
        
        # Generate integration scenarios dynamically
        integration_scenarios = []
        for other_group in endpoint_groups:
            if other_group != group_name:
                logger.info(f"Checking integration with {other_group}")
                if any(e['method'] == 'POST' for e in endpoint_groups[other_group]):
                    integration_scenarios.append(other_group)
        
        if integration_scenarios:
            logger.info(f"Adding integration scenarios with: {integration_scenarios}")
            content += f"""
@e2e @integration
Scenario: {group_name} Integration with Other Resources
    Given I have valid credentials
    And I am authenticated
"""
            
            for other_group in integration_scenarios:
                content += f"""
    # {other_group} Integration
    When I create a new {other_group.lower()} resource
    Then I can associate it with {group_name.lower()}
    And I can verify the association
"""
            
            content += """
    # Cleanup
    When I remove all created resources
    Then all resources should be properly cleaned up
"""
        
        crud_scenarios[feature_name] = content
        logger.info(f"Generated feature file: {feature_name}")
    
    return crud_scenarios

def generate_crud_files(endpoints: List[Dict[str, Any]]) -> List[str]:
    """Generate CRUD feature files and their step definitions."""
    os.makedirs(CRUD_DIR, exist_ok=True)
    crud_feature_files = []
    crud_step_files = []
    
    # Generate CRUD scenarios
    crud_scenarios = generate_crud_e2e_scenarios(endpoints)
    
    # Save CRUD scenarios
    for feature_name, content in crud_scenarios.items():
        feature_path = os.path.join(CRUD_DIR, feature_name)
        with open(feature_path, 'w') as f:
            f.write(content)
        crud_feature_files.append(feature_path)
        
        # Generate step definitions for CRUD scenarios
        step_file = generate_step_definitions(feature_path, {'endpoint': '/crud', 'method': 'CRUD'})
        crud_step_files.append(step_file)
    
    return crud_feature_files + crud_step_files 