import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Base directories
ROOT_DIR = Path(__file__).parent.parent.parent
SRC_DIR = ROOT_DIR / "src"
TESTS_DIR = ROOT_DIR / "tests"

# Test directories
FEATURES_DIR = TESTS_DIR / "features"
STEPS_DIR = TESTS_DIR / "steps"
REPORTS_DIR = TESTS_DIR / "reports"
CRUD_DIR = FEATURES_DIR / "crud"

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# API Configuration
API_BASE_URL = "https://bookstore.toolsqa.com"
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "")

# Ensure directories exist
for directory in [FEATURES_DIR, STEPS_DIR, REPORTS_DIR, CRUD_DIR]:
    directory.mkdir(parents=True, exist_ok=True) 