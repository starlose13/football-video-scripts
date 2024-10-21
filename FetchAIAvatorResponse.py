import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()
url = "https://api.creatify.ai/api/lipsyncs/"

creatify_api_id = os.getenv('CREATIFY_API_ID')
creatify_api_key = os.getenv('CREATIFY_API_KEY')

# Use the actual variables for API credentials
headers = {
    "X-API-ID": creatify_api_id,
    "X-API-KEY": creatify_api_key
}

# Make the GET request
response = requests.request("GET", url, headers=headers)

# Parse the JSON response
data = response.json()

# Convert the 'created_at' field to datetime and sort by it in descending order
sorted_data = sorted(data, key=lambda x: datetime.strptime(x['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z'), reverse=False)

# Filter and display only 'id', 'output', 'created_at', and 'status' fields
filtered_data = [
    {
        'id': item['id'],
        'output': item.get('output', 'N/A'),
        'created_at': item.get('created_at', 'N/A'),
        'status': item.get('status', 'N/A')
    } 
    for item in sorted_data
]

# Output the filtered result
print(json.dumps(filtered_data, indent=4))
