import os
import json
import requests
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()
shotstack_api_key = os.getenv("SHOTSTACK_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://api.shotstack.io/ingest/v1/sources"

def retrieve_ingested_file_links():
    headers = {
        "x-api-key": shotstack_api_key,
        "Accept": "application/json"
    }
    
    # Check if uploaded_files.json exists
    if not os.path.exists("uploaded_files.json"):
        logging.error("uploaded_files.json not found. Make sure the file exists with valid content.")
        return
    
    # Load uploaded files with their source IDs
    with open("uploaded_files.json", "r") as f:
        uploaded_files = json.load(f)
    
    links = {}

    try:
        response = requests.get(BASE_URL, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Sort 'data' list by 'created' attribute in descending order
        sorted_data = sorted(data['data'], key=lambda x: x['attributes']['created'], reverse=True)
        
        # Match each source ID with original file names
        for item in sorted_data:
            source_id = item['id']
            if source_id in uploaded_files.values():  # Only add known source IDs
                file_name = [name for name, id in uploaded_files.items() if id == source_id][0]
                file_url = item['attributes']['source']
                links[file_name] = file_url

        # Save the URLs to a JSON file with original names
        with open("ingested_files_links.json", "w") as json_file:
            json.dump(links, json_file, indent=4)
        
        logging.info("Ingested file URLs with original names have been saved to ingested_files_links.json")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving ingested file links: {e}")

# Run the function
retrieve_ingested_file_links()
