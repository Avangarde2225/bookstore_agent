#!/usr/bin/env python3
import os
import json
import logging
import requests
import sys
import argparse
from typing import List, Dict, Any
import pytest
from pytest_bdd import given, when, then, parsers
import openai
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from requests_html import HTML, HTMLSession
import itertools
import mlflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Import from our modules
from src.api.swagger import scrape_swagger_ui, extract_endpoint_info_via_llm, assemble_endpoints_from_chunks
from src.generators.feature_generator import generate_feature_files
from src.generators.step_generator import generate_step_definitions
from src.generators.crud_generator import generate_crud_e2e_scenarios
from src.generators.conftest_generator import generate_conftest
from src.utils.validators import validate_scenario_parameters, generate_parameter_combinations
from src.config.settings import FEATURES_DIR, STEPS_DIR, REPORTS_DIR, CRUD_DIR

def validate_environment() -> bool:
    """Validate required environment variables and dependencies."""
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Missing OPENAI_API_KEY environment variable")
        return False
    
    # Check required packages
    try:
        import requests_html
        import pytest
        import pytest_bdd
        import openai
        import mlflow
    except ImportError as e:
        logger.error(f"Missing required package: {str(e)}")
        return False
    
    return True

def setup_directories():
    """Create necessary directories for output files."""
    directories = [
        FEATURES_DIR,
        CRUD_DIR,
        STEPS_DIR,
        REPORTS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def print_setup_instructions():
    """Print setup instructions for required packages and environment variables."""
    print("""
Setup Instructions:

1. Install Required Packages:
   pip install -r requirements.txt

2. Set up Environment Variables:
   Create a .env file with:
   OPENAI_API_KEY=your_api_key_here

3. Directory Structure:
   The script will create:
   - features/         # Feature files
   - features/crud/    # CRUD test scenarios
   - steps/           # Step definitions
   - reports/         # Test reports

4. Running Tests:
   pytest features/ -v --html=reports/report.html

5. Troubleshooting:
   - If you get OpenAI API errors, check your API key
   - For Swagger UI issues, ensure the URL is accessible
   - For test failures, check the reports/ directory
""")

def main():
    """Main CLI interface for the test generator."""
    parser = argparse.ArgumentParser(description='Generate pytest-bdd test files from Swagger UI URL')
    parser.add_argument('--swagger-url', required=True, help='URL of the Swagger UI page')
    parser.add_argument('--model', default='gpt-3.5-turbo', help='OpenAI model to use (default: gpt-3.5-turbo)')
    parser.add_argument('--output-dir', default='.', help='Output directory for generated files')
    parser.add_argument('--setup', action='store_true', help='Print setup instructions')
    
    args = parser.parse_args()
    
    if args.setup:
        print_setup_instructions()
        return
    
    # Validate environment and setup directories
    if not validate_environment():
        print_setup_instructions()
        return
    
    setup_directories()
    
    try:
        # Start MLflow tracking
        mlflow.set_experiment("Swagger_Test_Generation")
        mlflow.start_run(run_name="Pytest_BDD_Generation")
        mlflow.log_param("swagger_url", args.swagger_url)
        mlflow.log_param("model_name", args.model)
        
        # Generate conftest.py first
        logger.info("Generating conftest.py")
        conftest_file = generate_conftest()
        
        # Scrape Swagger UI and extract endpoint information
        logger.info(f"Scraping Swagger UI from {args.swagger_url}")
        endpoint_chunks = scrape_swagger_ui(args.swagger_url)
        
        logger.info("Extracting endpoint information")
        endpoint_infos = []
        for chunk in endpoint_chunks:
            info = extract_endpoint_info_via_llm(chunk, args.model)
            if info:
                endpoint_infos.append(info)
        
        # Assemble endpoints
        logger.info("Assembling endpoint information")
        endpoints = assemble_endpoints_from_chunks(endpoint_infos)
        
        # Generate feature files
        logger.info("Generating feature files")
        feature_files, step_files = generate_feature_files(endpoints, args.model)
        
        # Generate CRUD scenarios
        logger.info("Generating CRUD scenarios")
        crud_scenarios = generate_crud_e2e_scenarios(endpoints)
        
        # Save CRUD scenarios
        for feature_name, content in crud_scenarios.items():
            feature_path = CRUD_DIR / feature_name
            with open(feature_path, 'w') as f:
                f.write(content)
            feature_files.append(str(feature_path))
            
            # Generate step definitions for CRUD scenarios
            step_file = generate_step_definitions(str(feature_path), {'endpoint': '/crud', 'method': 'CRUD'})
            step_files.append(step_file)
        
        # Print summary
        print("\nGenerated Files:")
        print("Configuration:")
        print(f"  - {conftest_file}")
        print("\nFeature Files:")
        for file in feature_files:
            print(f"  - {file}")
        print("\nStep Definition Files:")
        for file in step_files:
            print(f"  - {file}")
        
        print("\nSetup complete! Run tests with:")
        print(f"pytest {FEATURES_DIR} -v --html={REPORTS_DIR}/report.html")
        
        # End MLflow run
        mlflow.end_run()
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print("\nError occurred. Please check the logs for details.")
        print_setup_instructions()
        mlflow.end_run(status="FAILED")
        sys.exit(1)

if __name__ == '__main__':
    main() 