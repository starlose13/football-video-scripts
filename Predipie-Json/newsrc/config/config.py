# config.py

from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
SHOTSTACK_API_KEY = os.getenv("SHOTSTACK_API_KEY")
CREATIFY_API_ID = os.getenv("CREATIFY_API_ID")
CREATIFY_API_KEY = os.getenv("CREATIFY_API_KEY")
BASE_URL = "https://data-provider.ledoso.com"
PROGRAM_NAME = "PrediPie TV Series"
today = datetime.now()
yesterday = today - timedelta(days=1)
START_AFTER = today.strftime("%Y-%m-%d")
START_BEFORE = yesterday.strftime("%Y-%m-%d")
