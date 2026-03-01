"""
config.py — Shared configuration and constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_ENDPOINT: str = "https://api.mistral.ai/v1/chat/completions"
