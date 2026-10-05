import os
from dotenv import load_dotenv

load_dotenv()

DEVX_BASE_URL = os.getenv("DEVX_BASE_URL", "https://join.devxlabs.ai/mcp/core")
DEVX_AUTH_TOKEN = os.getenv("DEVX_AUTH_TOKEN", "")
DEFAULT_ROLE = "Data Scientist"
DEFAULT_LOCATION = "Surat, Gujarat, India"
