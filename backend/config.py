"""Configuration module for the Debate Explorer backend."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Anthropic API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

# API Configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"
API_TIMEOUT = 30  # seconds

# Response Configuration
MIN_WORDS = 200
MAX_WORDS = 300

