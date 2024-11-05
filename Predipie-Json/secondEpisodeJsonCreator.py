import requests
import json
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define the API endpoint
url = 'https://dataprovider.predipie.com/api/v1/ai/test/'

# Function to generate a match description with the ChatGPT API
def generate_match_description(host_team, guest_team):
    prompt = f" [Smile warmly as you begin speaking]. Let's jump into the action with our first match-up between {host_team} and {guest_team}!  Now, create an energetic, dynamic description of this match-up in less than 200 characters.Be sure you put pause and smile before you want to point to the game."

    # Call the ChatGPT API to generate the script
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant helping to create dynamic football video scripts."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    generated_script = response['choices'][0]['message']['content'].strip()
    return generated_script

try:
    # Send a GET request to the API
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes

    # Parse the JSON response
    data = response.json()

    # Create a folder to store the files if it doesn't already exist
    folder_name = 'match_descriptions_scene2'
    os.makedirs(folder_name, exist_ok=True)

    # Extract and save each of the first 5 matches to separate JSON files
    for i, item in enumerate(data[:5], start=1):  # Limit to the first 5 matches
        host_team_name = item.get('home', {}).get('name', 'Unknown Host Team')
        guest_team_name = item.get('away', {}).get('name', 'Unknown Guest Team')
        host_team_logo = item.get('home', {}).get('logo', 'No Logo Available')
        guest_team_logo = item.get('away', {}).get('logo', 'No Logo Available')
        
        # Use a conditional expression to safely retrieve the country name
        host_team_country = item.get('home', {}).get('country', {}).get('name') if item.get('home', {}).get('country') else 'Unknown Country'
        guest_team_country = item.get('away', {}).get('country', {}).get('name') if item.get('away', {}).get('country') else 'Unknown Country'
        
        # Generate the description using ChatGPT API
        match_description = generate_match_description(host_team_name, guest_team_name)
        
        # Format the data with host and guest team details and description
        match_info = {
            "description": match_description,
            "home_team": {
                "name": host_team_name,
                "logo": host_team_logo,
                "country": host_team_country
            },
            "away_team": {
                "name": guest_team_name,
                "logo": guest_team_logo,
                "country": guest_team_country
            }
        }

        # Define the output file path for each match
        output_file = os.path.join(folder_name, f'match_{i}.json')
        
        # Write each match's description and team details to its own JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(match_info, f, ensure_ascii=False, indent=4)
        
        print(f"Match {i} description and team data saved to {output_file}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred with the API request: {e}")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON response: {e}")
except openai.error.OpenAIError as e:
    print(f"An error occurred with the OpenAI API: {e}")
except IOError as e:
    print(f"Error saving file: {e}")
