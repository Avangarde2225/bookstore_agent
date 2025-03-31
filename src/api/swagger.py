import json
from typing import List, Dict, Any
from requests_html import HTMLSession
from ..config.settings import logger, openai

def scrape_swagger_ui(url: str) -> List[str]:
    """Scrapes a Swagger UI page and extracts individual endpoint operations."""
    session = HTMLSession()
    response = session.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch Swagger UI page. Status code: {response.status_code}")
    
    try:
        response.html.render(timeout=30)
    except Exception as e:
        logger.warning(f"JavaScript rendering failed: {str(e)}")
        logger.info("Continuing with static HTML content...")
    
    # Updated selectors for Swagger UI
    opblock_classes = [
        '.opblock.opblock-get',
        '.opblock.opblock-post',
        '.opblock.opblock-put',
        '.opblock.opblock-delete',
        '.opblock.opblock-patch'
    ]
    operation_chunks = []
    
    for op_class in opblock_classes:
        blocks = response.html.find(op_class)
        for block in blocks:
            operation_chunks.append(block.html)
    
    if not operation_chunks:
        logger.warning("No operation blocks found. The page might not be a Swagger UI or the selectors might need adjustment.")
        # Try alternative selectors
        alt_selectors = [
            '.operation-tag-content',
            '.opblock-summary',
            '.opblock-section'
        ]
        for selector in alt_selectors:
            blocks = response.html.find(selector)
            if blocks:
                for block in blocks:
                    operation_chunks.append(block.html)
                break
    
    if not operation_chunks:
        logger.error("Could not find any API operations. Please verify the Swagger UI URL and page structure.")
    
    return operation_chunks

def extract_endpoint_info_via_llm(chunk_html: str, model_name="gpt-3.5-turbo") -> Dict[str, Any]:
    """Extracts structured endpoint information from a Swagger UI HTML chunk using an LLM."""
    logger.debug("Processing HTML chunk with LLM")

    if not openai.api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

    prompt_text = f"""
Extract API endpoint information and generate BDD test implementations from this Swagger UI HTML.
Focus on generating pytest-bdd step definitions that follow these guidelines:

1. Authentication Steps:
   - Handle authentication setup
   - Manage API tokens
   - Verify authentication state

2. Request Building:
   - Build proper request URLs
   - Set correct headers
   - Handle request parameters
   - Prepare request bodies

3. Response Validation:
   - Verify status codes
   - Validate response structures
   - Check error conditions
   - Handle different response types

4. Resource Management:
   - Create test resources
   - Clean up after tests
   - Handle resource dependencies

Return a JSON object with this structure:
{{
    "endpoint": {{
        "path": "string",
        "method": "string",
        "description": "string"
    }},
    "test_implementation": {{
        "imports": [
            "string (import statements)"
        ],
        "fixtures": [
            {{
                "name": "string",
                "code": "string"
            }}
        ],
        "steps": [
            {{
                "type": "given/when/then",
                "pattern": "string",
                "code": "string",
                "description": "string"
            }}
        ]
    }}
}}

Guidelines:
1. Generate complete step definitions with proper error handling
2. Include all necessary imports and fixtures
3. Follow pytest-bdd best practices
4. Handle authentication and authorization properly
5. Include proper cleanup in teardown
6. Generate descriptive step patterns

HTML:
{chunk_html}
"""

    try:
        response = openai.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an API documentation analyzer. Extract structured endpoint information from Swagger UI HTML and return only valid JSON without any additional text."},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=2000,
            temperature=0.0,
        )
        
        completion_text = response.choices[0].message.content.strip()
        completion_text = completion_text.strip().replace('```json', '').replace('```', '')
        
        data = json.loads(completion_text)
        
        # Validate required fields
        required_fields = ["endpoint", "method"]
        if not all(field in data for field in required_fields):
            logger.warning("Missing required fields in LLM response")
            return {}
            
        # Ensure parameters is a list
        if "parameters" not in data:
            data["parameters"] = []
        elif not isinstance(data["parameters"], list):
            data["parameters"] = []
            
        # Ensure requestBody is a dict
        if "requestBody" not in data:
            data["requestBody"] = {}
        elif not isinstance(data["requestBody"], dict):
            data["requestBody"] = {}
            
        # Ensure responses is a dict
        if "responses" not in data:
            data["responses"] = {}
        elif not isinstance(data["responses"], dict):
            data["responses"] = {}
            
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON from LLM: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Error processing HTML chunk: {str(e)}")
        return {}

def assemble_endpoints_from_chunks(endpoint_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Assembles and validates endpoint information from multiple chunks."""
    endpoints_by_path: Dict[str, Dict[str, Any]] = {}
    
    for chunk in endpoint_chunks:
        if not chunk or "endpoint" not in chunk or "method" not in chunk:
            logger.warning("Skipping invalid endpoint chunk")
            continue
            
        path = chunk["endpoint"]
        method = chunk["method"].upper()
        
        if path not in endpoints_by_path:
            endpoints_by_path[path] = {
                "endpoint": path,
                "methods": {},
                "parameters": [],
                "requestBody": {},
                "responses": {}
            }
        
        # Check for method conflicts
        if method in endpoints_by_path[path]["methods"]:
            logger.warning(f"Found duplicate method {method} for endpoint {path}")
            existing = endpoints_by_path[path]["methods"][method]
            if existing.get("parameters") != chunk.get("parameters", []):
                logger.warning(f"Parameter mismatch for {method} {path}")
            if existing.get("requestBody") != chunk.get("requestBody", {}):
                logger.warning(f"Request body mismatch for {method} {path}")
            if existing.get("responses") != chunk.get("responses", {}):
                logger.warning(f"Response mismatch for {method} {path}")
        
        # Store method-specific information
        endpoints_by_path[path]["methods"][method] = {
            "parameters": chunk.get("parameters", []),
            "requestBody": chunk.get("requestBody", {}),
            "responses": chunk.get("responses", {})
        }
        
        # Merge parameters, removing duplicates
        existing_params = {p["name"]: p for p in endpoints_by_path[path]["parameters"]}
        for param in chunk.get("parameters", []):
            if param["name"] in existing_params:
                if existing_params[param["name"]] != param:
                    logger.warning(f"Parameter conflict for {param['name']} in {path}")
            else:
                endpoints_by_path[path]["parameters"].append(param)
        
        # Merge request body if present
        if chunk.get("requestBody"):
            if endpoints_by_path[path]["requestBody"]:
                if endpoints_by_path[path]["requestBody"] != chunk["requestBody"]:
                    logger.warning(f"Request body conflict for {path}")
            else:
                endpoints_by_path[path]["requestBody"] = chunk["requestBody"]
        
        # Merge responses
        for status_code, response in chunk.get("responses", {}).items():
            if status_code in endpoints_by_path[path]["responses"]:
                if endpoints_by_path[path]["responses"][status_code] != response:
                    logger.warning(f"Response conflict for status {status_code} in {path}")
            else:
                endpoints_by_path[path]["responses"][status_code] = response
    
    # Convert the nested structure to a flat list of endpoints
    final_endpoints = []
    for path, endpoint_info in endpoints_by_path.items():
        for method, method_info in endpoint_info["methods"].items():
            final_endpoint = {
                "endpoint": path,
                "method": method,
                "parameters": method_info["parameters"],
                "requestBody": method_info["requestBody"],
                "responses": method_info["responses"]
            }
            final_endpoints.append(final_endpoint)
    
    return final_endpoints 