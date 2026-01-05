import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN", "")

if not API_TOKEN:
    raise ValueError("API_TOKEN environment variable is not set")

