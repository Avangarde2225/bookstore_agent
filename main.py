#!/usr/bin/env python3
import os
import json
import openai
import mlflow
from dotenv import load_dotenv
from mlflow_tracking import MLflowTracker

from requests_html import HTML, HTMLSession

# Load environment variables from .env file
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize the tracker
tracker = MLflowTracker()

#############################################
# 1. SCRAPE THE SWAGGER UI (HTML)
#############################################

def get_swagger_html(url: str) -> str:
    """
    Fetch the raw HTML from a Swagger UI page using requests-html.
    If the page relies on JavaScript for rendering, .render() is used.
    """
    print("[DEBUG] Entering get_swagger_html")  # DEBUG STATEMENT

    session = HTMLSession()
    response = session.get(url)
    
    print("[DEBUG] HTTP status code:", response.status_code)  # DEBUG: Check if 200, etc.
    
    try:
        # If the page uses JavaScript to dynamically load endpoints, we need .render().
        # This requires a Chromium install. If the page is entirely static, you can skip render().
        print("[DEBUG] Rendering HTML with requests-html...")  # DEBUG STATEMENT
        response.html.render(timeout=60, sleep=5)  # Increased timeout and sleep
        print("[DEBUG] Done rendering.")  # DEBUG STATEMENT
    except Exception as e:
        print(f"[WARNING] Failed to render JavaScript: {str(e)}")
        print("[INFO] Continuing with static HTML content...")
    
    html_content = response.html.html
    print("[DEBUG] Length of HTML content:", len(html_content))  # DEBUG: Checking how much data we got
    
    # Print a preview of the HTML content to verify we're getting the right content
    print("[DEBUG] HTML Content Preview:")
    print(html_content[:500])  # Print first 500 chars
    
    return html_content

#print(get_swagger_html("https://bookstore.toolsqa.com/swagger/"))


#############################################
# 2. CHUNK THE HTML BY OPERATION BLOCKS
#############################################

def chunk_swagger_html(html_text: str):
    """
    Yields chunks of HTML, each corresponding to one endpoint or method.
    In many Swagger UIs, each endpoint or operation is under a <div class="opblock">.
    Adjust the selector if your HTML differs.
    """
    print("[DEBUG] Entering chunk_swagger_html")  # DEBUG STATEMENT

    doc = HTML(html=html_text)
    
    # Try different common Swagger UI selectors
    blocks = doc.find('div.opblock') or doc.find('div[class*="opblock"]') or doc.find('div[class*="operation"]')
    
    if not blocks:
        # If no blocks found, try to find any div that might contain endpoint information
        blocks = doc.find('div[class*="endpoint"]') or doc.find('div[class*="api"]')
    
    print("[DEBUG] Found", len(blocks), "blocks.")  # DEBUG: How many chunks?

    if not blocks:
        # If still no blocks found, print the HTML structure for debugging
        print("[DEBUG] HTML Structure Preview:")
        print(doc.html[:500])  # Print first 500 chars of HTML for debugging

    for i, block in enumerate(blocks, start=1):
        block_html = block.html
        print(f"[DEBUG] Yielding chunk #{i}, length={len(block_html)}")  # DEBUG: Each chunk's size
        yield block_html


#############################################
# 3. EXTRACT ENDPOINT INFO VIA LLM
#############################################

def extract_endpoint_info_via_llm(chunk_html: str, model_name="text-davinci-003") -> list:
    """
    Sends a prompt to the LLM to parse the chunked HTML from the Swagger UI.
    Instructs the model to return JSON describing endpoints, methods, parameters, etc.
    """
    print("[DEBUG] Entering extract_endpoint_info_via_llm")  # DEBUG STATEMENT
    print("[DEBUG] Model name:", model_name)  # DEBUG: Which model is being used?

    openai.api_key = os.getenv("OPENAI_API_KEY", "")
    if not openai.api_key:
        raise RuntimeError("[ERROR] Missing OPENAI_API_KEY environment variable.")

    # Print a small snippet of chunk_html to verify content
    print("[DEBUG] chunk_html snippet:", chunk_html[:100].replace("\n", " "), "...")  # Just a preview

    prompt_text = f"""
Below is a snippet of HTML from a Swagger UI.
Extract all endpoint paths, HTTP methods, and any parameter info you can find.
Return valid JSON in the format:
[
  {{
    "endpoint": "string",
    "method": "GET/POST/PUT/DELETE/etc.",
    "parameters": [
      {{
        "name": "param_name",
        "in": "path/query/header/etc.",
        "required": true/false,
        "description": "string"
      }}
    ]
  }},
  ...
]

HTML:
{chunk_html}
"""

    print("[DEBUG] Sending prompt to LLM, prompt length:", len(prompt_text))  # DEBUG: Prompt size

    with mlflow.start_run(nested=True):
        response = openai.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts API endpoint information from Swagger UI HTML. Return only valid JSON without any markdown formatting or additional text."},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=1500,
            temperature=0.0,
        )
        completion_text = response.choices[0].message.content.strip()

        # Track API usage
        tracker.log_api_call(
            model=model_name,
            tokens=response.usage.total_tokens
        )

    # DEBUG: Print a small portion of the LLM response
    print("[DEBUG] LLM raw response snippet:", completion_text[:200], "...")

    # Clean up the response text
    completion_text = completion_text.strip()
    if completion_text.startswith("```json"):
        completion_text = completion_text[7:]
    if completion_text.endswith("```"):
        completion_text = completion_text[:-3]
    completion_text = completion_text.strip()

    # Attempt to parse JSON
    try:
        data = json.loads(completion_text)
        if not isinstance(data, list):
            print("[WARN] Expected a list at top level. Got something else.")
            return []
        print("[DEBUG] Successfully parsed JSON with", len(data), "items.")  # DEBUG
        return data
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON from LLM. Could not parse: {str(e)}")
        print("[DEBUG] Raw response:", completion_text)
        return []


#############################################
# 4. GENERATE .FEATURE FILES
#############################################

def generate_feature_file_for_endpoint(endpoint_info: dict, output_dir="features", model_name="gpt-3.5-turbo"):
    """
    Given a single endpoint info dict (with 'endpoint', 'method', 'parameters'),
    prompt the LLM to produce a Gherkin .feature file containing scenarios 
    for the endpoint & parameters.
    """
    print("[DEBUG] Entering generate_feature_file_for_endpoint")  # DEBUG STATEMENT

    endpoint = endpoint_info.get("endpoint", "unknown")
    method = endpoint_info.get("method", "GET")
    parameters = endpoint_info.get("parameters", [])

    # Quick check what endpoint/method we got
    print("[DEBUG] Generating feature for endpoint:", endpoint, "| method:", method)

    prompt_text = f"""
        Generate a comprehensive pytest-bdd Gherkin feature file for the endpoint "{endpoint}" with HTTP method "{method}".
        Parameters: {json.dumps(parameters, indent=2)}.

        Create meaningful scenarios that:
        1. Test the basic functionality of the endpoint
        2. Include edge cases and error conditions
        3. Consider the business context and user workflows
        4. Follow a logical flow of operations

        Format strictly as a .feature file with:
        - Feature: A clear description of the endpoint's purpose
        - Background: Common setup steps if needed
        - Scenarios: Multiple test cases with Given/When/Then steps
        - Use tables where appropriate for data variations

        Output only the feature text, no extra commentary.
        """

    with mlflow.start_run(nested=True):
        response = openai.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a test automation expert who creates comprehensive Gherkin feature files for API testing."},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=2000,
            temperature=0.0,
        )
        feature_text = response.choices[0].message.content.strip()

        # Track API usage
        tracker.log_api_call(
            model=model_name,
            tokens=response.usage.total_tokens
        )

    # Print snippet of generated feature
    print("[DEBUG] Feature snippet:", feature_text[:200].replace("\n", " "), "...")

    # Save to file
    import os
    os.makedirs(output_dir, exist_ok=True)
    endpoint_clean = endpoint.replace("/", "_").strip("_")
    filename = f"{output_dir}/test_{endpoint_clean}_{method}.feature"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(feature_text)
    
    print(f"[DEBUG] Generated feature file: {filename}")  # DEBUG: Which file was written


def generate_step_definition_file(feature_info: dict, output_dir="step_definitions"):
    """
    Generate a step definition file for a specific feature file.
    """
    endpoint = feature_info.get("endpoint", "unknown")
    method = feature_info.get("method", "GET")
    
    # Create step definitions directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename from endpoint
    filename = f"{output_dir}/test_{endpoint.replace('/', '_').strip('_')}_{method.lower()}_steps.py"
    
    with mlflow.start_run(nested=True):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a test automation expert who creates step definitions for BDD feature files."},
                {"role": "user", "content": f"""
                Create step definitions for the following API endpoint:
                Endpoint: {endpoint}
                Method: {method}
                Parameters: {json.dumps(feature_info.get('parameters', []), indent=2)}
                
                Include steps for:
                1. Setting up request data and headers
                2. Making the API call
                3. Validating response status and content
                4. Error handling scenarios
                5. Any specific business logic validations
                
                Use pytest-bdd decorators and follow Python best practices.
                """}
            ],
            max_tokens=2000,
            temperature=0.0,
        )
        
        step_definitions = response.choices[0].message.content.strip()
        
        # Track API usage
        tracker.log_api_call(
            model="gpt-3.5-turbo",
            tokens=response.usage.total_tokens
        )
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write('''import pytest
from pytest_bdd import given, when, then, parsers
import requests
from typing import Dict, Any

# Context to store data between steps
context = {}\n\n''')
            f.write(step_definitions)
    
    print(f"Generated step definitions: {filename}")

def generate_all_feature_files(api_endpoints: list, model_name="gpt-3.5-turbo"):
    """
    For each endpoint (dict) in api_endpoints, generate a .feature file and its corresponding step definitions.
    """
    print("[DEBUG] Entering generate_all_feature_files")
    print("[DEBUG] Total endpoints to process:", len(api_endpoints))

    for index, ep_info in enumerate(api_endpoints, start=1):
        print(f"[DEBUG] Processing endpoint #{index} / {len(api_endpoints)}")
        generate_feature_file_for_endpoint(ep_info, model_name=model_name)
        generate_step_definition_file(ep_info)  # Generate corresponding step definitions


#############################################
# 5. MASTER FUNCTION - SCRAPE, EXTRACT, GENERATE
#############################################

def scrape_and_generate_features(swagger_url: str, model_name="text-davinci-003"):
    """
    1) Scrape the raw HTML from swagger_url
    2) Chunk it
    3) Extract endpoint info from each chunk via LLM
    4) Combine them into a single list
    5) Generate .feature files for each endpoint
    """
    print("[DEBUG] Entering scrape_and_generate_features")  # DEBUG STATEMENT
    print("[DEBUG] swagger_url:", swagger_url)
    print("[DEBUG] model_name:", model_name)

    with mlflow.start_run(run_name="Swagger_EndToEnd"):
        print(f"[DEBUG] Scraping HTML from: {swagger_url}")
        html = get_swagger_html(swagger_url)

        print("[DEBUG] Length of scraped HTML:", len(html))

        print("Chunking the HTML into endpoint blocks...")
        all_endpoints = []
        for chunk_html in chunk_swagger_html(html):
            chunk_data = extract_endpoint_info_via_llm(chunk_html, model_name=model_name)
            # chunk_data is a list; extend our main list
            all_endpoints.extend(chunk_data)

        print("[DEBUG] Total endpoints extracted so far:", len(all_endpoints))

        # Optionally deduplicate or refine data here if needed
        # e.g., all_endpoints = deduplicate_endpoints(all_endpoints)

        # Generate .feature files
        generate_all_feature_files(all_endpoints, model_name=model_name)


#############################################
# TEST SECTION
#############################################

if __name__ == "__main__":
    try:
        # Test URL
        test_url = "https://bookstore.toolsqa.com/swagger/"
        
        print("\n=== Testing get_swagger_html ===")
        html_content = get_swagger_html(test_url)
        print(f"HTML Content Length: {len(html_content)}")
        
        print("\n=== Testing chunk_swagger_html ===")
        chunk_count = 0
        all_chunks = []
        for chunk in chunk_swagger_html(html_content):
            chunk_count += 1
            all_chunks.append(chunk)
            print(f"\nChunk {chunk_count}:")
            print(f"Length: {len(chunk)}")
            print("Preview:", chunk[:200] + "...")
        
        print(f"\nTotal chunks found: {chunk_count}")
        
        print("\n=== Testing extract_endpoint_info_via_llm ===")
        if not openai_api_key:
            print("[ERROR] OPENAI_API_KEY environment variable is not set!")
        else:
            all_endpoints = []
            # Process all chunks
            for i, chunk in enumerate(all_chunks, 1):
                print(f"\nProcessing chunk {i}/{len(all_chunks)}...")
                endpoint_info = extract_endpoint_info_via_llm(chunk, model_name="gpt-3.5-turbo")
                all_endpoints.extend(endpoint_info)
            
            print(f"\nTotal endpoints extracted: {len(all_endpoints)}")
            if all_endpoints:
                print("\nAll Endpoint Details:")
                for endpoint in all_endpoints:
                    print("\n" + "="*50)
                    print(f"Endpoint: {endpoint.get('endpoint', 'N/A')}")
                    print(f"Method: {endpoint.get('method', 'N/A')}")
                    print("Parameters:")
                    for param in endpoint.get('parameters', []):
                        print(f"  - {param.get('name', 'N/A')} ({param.get('in', 'N/A')})")
                        print(f"    Required: {param.get('required', 'N/A')}")
                        print(f"    Description: {param.get('description', 'N/A')}")
                
                print("\n=== Generating Feature Files ===")
                print(f"Generating feature files for {len(all_endpoints)} endpoints...")
                generate_all_feature_files(all_endpoints, model_name="gpt-3.5-turbo")
                print("\nFeature file generation complete!")
            else:
                print("[WARNING] No endpoints were extracted from any chunks.")

        # End tracking and log final metrics
        tracker.end_run()
    except Exception as e:
        print(f"Error: {str(e)}")
        tracker.end_run()  # Ensure we log metrics even on failure