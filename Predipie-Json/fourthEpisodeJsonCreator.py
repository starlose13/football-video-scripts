import requests
import json
import os
import openai
from datetime import datetime
from dotenv import load_dotenv

# Define your OpenAI API key
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define the API endpoint
url = 'https://dataprovider.predipie.com/api/v1/ai/test/'

# Function to generate a match description with odds using the ChatGPT API
def generate_match_description_with_odds(host_team, guest_team, home_odds, guest_odds, draw_odds):
    # Create a prompt for OpenAI to generate the description
    prompt = (
        f"[Generate a concise and complete description for football match odds, using only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon. "
        f"Provide only the odds information directly, without introducing the teams or match. State each type of odds clearly and avoid abbreviations or parentheses. Keep it under 45 words.] "
        f"The home team, {host_team}, has odds of winning at {home_odds}. The away team, {guest_team}, has odds of winning at {guest_odds}. The odds for a draw are {draw_odds}."
    )


    # Call the ChatGPT API to generate the description
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant helping to create dynamic football match descriptions with odds information."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    generated_script = response['choices'][0]['message']['content'].strip()
    return generated_script

try:
    # Send a GET request to the API
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes

    # Parse the JSON response
    data = response.json()

    # Create the folder `scene4` to store the files if it doesn't already exist
    folder_name = 'scene4'
    os.makedirs(folder_name, exist_ok=True)

    # Extract and save each of the first 5 matches to separate JSON files
    for i, item in enumerate(data[:5], start=1):  # Limit to the first 5 matches
        host_team = item.get('home', {}).get('name', 'Unknown Host Team')
        guest_team = item.get('away', {}).get('name', 'Unknown Guest Team')
        home_odds = item.get('odds', {}).get('home', 'N/A')
        guest_odds = item.get('odds', {}).get('away', 'N/A')
        draw_odds = item.get('odds', {}).get('draw', 'N/A')
        
        # Generate the description with odds using ChatGPT API
        match_description = generate_match_description_with_odds(host_team, guest_team, home_odds, guest_odds, draw_odds)
        
        # Format the data as required, including odds
        match_info = {
            "description": match_description,
            "odds": {
                "home": home_odds,
                "away": guest_odds,
                "draw": draw_odds
            }
        }

        # Define the output file path for each match
        output_file = os.path.join(folder_name, f'match_{i}.json')
        
        # Write each match's description and odds to its own JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(match_info, f, ensure_ascii=False, indent=4)
        
        print(f"Match {i} description with odds saved to {output_file}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred with the API request: {e}")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON response: {e}")
except openai.error.OpenAIError as e:
    print(f"An error occurred with the OpenAI API: {e}")
except IOError as e:
    print(f"Error saving file: {e}")