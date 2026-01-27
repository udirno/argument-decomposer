"""Configuration module for the Debate Explorer backend."""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Anthropic API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

# API Configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"
API_TIMEOUT = 30  # seconds per agent
ORCHESTRATION_TIMEOUT = 60  # seconds for all agents combined

# Input Validation
MAX_QUESTION_LENGTH = 2000  # Maximum characters for input question

# Response Configuration
EXPECTED_WORD_COUNT = "250-350 words"  # Target length mentioned in prompts

# Environment
ENV = os.getenv("ENV", "development")  # development or production

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080").split(",")

# Logging Configuration
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO if ENV == "production" else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'app.log'),
        logging.StreamHandler()
    ]
)

