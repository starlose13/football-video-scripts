# config.py

from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
SHOTSTACK_API_KEY = os.getenv("SHOTSTACK_API_KEY")
CREATIFY_API_ID = os.getenv("CREATIFY_API_ID")
CREATIFY_API_KEY = os.getenv("CREATIFY_API_KEY")
BASE_URL = os.getenv("BASE_DATA_PROVIDER_URL") 
PROGRAM_NAME = os.getenv("PROGRAM_NAME")
today = datetime.now()
yesterday = today - timedelta(days=1)
# START_AFTER = today.strftime("%Y-%m-%d")
# START_BEFORE = yesterday.strftime("%Y-%m-%d")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSET_DIR = os.path.abspath(os.path.join(BASE_DIR, "assets"))

START_AFTER = "2024-11-22" 
START_BEFORE = "2024-11-21"
