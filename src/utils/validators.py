from typing import List, Dict, Any
from ..config.settings import logger

def validate_scenario_parameters(scenario: str, endpoint_info: Dict[str, Any]) -> bool:
    """Validates that all parameters referenced in a scenario exist in the endpoint info."""
    # Extract all parameter names from the scenario
    param_references = set()
    for line in scenario.split('\n'):
        if '|' in line:
            # Handle table parameters
            params = [p.strip() for p in line.split('|')[1:-1]]
            param_references.update(params)
        elif '<' in line and '>' in line:
            # Handle scenario outline parameters
            params = [p.strip() for p in line.split('<')[1].split('>')[0].split(',')]
            param_references.update(params)
    
    # Get valid parameter names from endpoint info
    valid_params = {p['name'] for p in endpoint_info.get('parameters', [])}
    if 'requestBody' in endpoint_info:
        body_schema = endpoint_info['requestBody'].get('content', {}).get('application/json', {}).get('schema', {})
        if 'properties' in body_schema:
            valid_params.update(body_schema['properties'].keys())
    
    # Check for invalid parameters
    invalid_params = param_references - valid_params
    if invalid_params:
        logger.warning(f"Found invalid parameter references: {invalid_params}")
        return False
    
    return True

def generate_parameter_combinations(parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generates parameter combinations for scenario outlines."""
    import itertools
    
    required_params = [p for p in parameters if p.get('required', False)]
    optional_params = [p for p in parameters if not p.get('required', False)]
    
    combinations = []
    
    # Generate combinations with required parameters
    base_combo = {p['name']: f"valid_{p['name']}" for p in required_params}
    combinations.append(base_combo)
    
    # Add combinations with optional parameters
    for i in range(1, len(optional_params) + 1):
        for combo in itertools.combinations(optional_params, i):
            combo_dict = base_combo.copy()
            for param in combo:
                combo_dict[param['name']] = f"valid_{param['name']}"
            combinations.append(combo_dict)
    
    return combinations 