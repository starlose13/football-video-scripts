import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
shotstack_api_key = os.getenv("SHOTSTACK_API_KEY")
shotstack_env = os.getenv("SHOTSTACK_ENVIRONMENT", "stage")  # Default to 'stage'

BASE_URL = f"https://api.shotstack.io/ingest/{shotstack_env}/sources"

def retrieve_ingested_file_links():
    headers = {
        "x-api-key": shotstack_api_key,
        "Accept": "application/json"
    }
    
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
        
        print("Ingested file URLs with original names have been saved to ingested_files_links.json")

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving ingested file links: {e}")

# Run the function
retrieve_ingested_file_links()
