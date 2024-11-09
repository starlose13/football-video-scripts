import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Shotstack configuration
SHOTSTACK_API_KEY = os.getenv("SHOTSTACK_API_KEY")
SHOTSTACK_ENVIRONMENT = os.getenv("SHOTSTACK_ENVIRONMENT", "stage")  # Default to 'stage'

# Set Shotstack API base URL
BASE_URL = f"https://api.shotstack.io/ingest/{SHOTSTACK_ENVIRONMENT}/sources"

def retrieve_ingested_file_links():
    headers = {
        "x-api-key": SHOTSTACK_API_KEY,
        "Accept": "application/json"
    }
    
    # Initialize an empty dictionary to store the links
    links = {}

    try:
        # Make a request to the Shotstack API to retrieve ingested files
        response = requests.get(BASE_URL, headers=headers)
        response.raise_for_status()  # Raise an error for any unsuccessful response

        # Parse the JSON response
        data = response.json()
        
        # Extract the 'source' URLs for each item in the response
        for item in data['data']:
            file_id = item['id']
            file_url = item['attributes']['source']
            links[file_id] = file_url

        # Save the URLs to a JSON file
        with open("ingested_files_links.json", "w") as json_file:
            json.dump(links, json_file, indent=4)
        
        print("Ingested file URLs have been saved to ingested_files_links.json")

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving ingested file links: {e}")

# Run the function
retrieve_ingested_file_links()
