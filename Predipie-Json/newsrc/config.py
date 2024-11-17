# config.py

from datetime import datetime, timedelta

BASE_URL = "https://data-provider.ledoso.com"
PROGRAM_NAME = "PrediPie TV Series"

today = datetime.now()
yesterday = today - timedelta(days=1)

START_AFTER = today.strftime("%Y-%m-%d")
START_BEFORE = yesterday.strftime("%Y-%m-%d")

print("START_AFTER" ,START_AFTER)
print("START_BEFORE" ,START_BEFORE)