import requests
import json
import os
import openai
from dotenv import load_dotenv

# Define your OpenAI API key
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define the API endpoint
url = 'https://dataprovider.predipie.com/api/v1/ai/test/'

# Function to generate a match description with recent form using the ChatGPT API
def generate_match_description_with_recent_form(host_team, guest_team, host_results, host_wins, host_draws, host_losses, guest_results, guest_wins, guest_draws, guest_losses):
    # Create a prompt for OpenAI to generate the description
    prompt = (
    f"[Generate a concise description of each team’s recent form, using full words for clarity and avoiding abbreviations like 'W', 'D', or 'L'. Focus on readability. Limit to 200 characters. using only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon.] "
    f"The home team’s recent form shows {host_results} (Wins: {host_wins}, Draws: {host_draws}, Losses: {host_losses}), "
    f"while the away team has recorded {guest_results} (Wins: {guest_wins}, Draws: {guest_draws}, Losses: {guest_losses}).")

    # Call the ChatGPT API to generate the description
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant helping to create dynamic football match descriptions with recent form information."},
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

    # Create the folder `scene6` to store the files if it doesn't already exist
    folder_name = 'scene5'
    os.makedirs(folder_name, exist_ok=True)

    # Extract and save each of the first 5 matches to separate JSON files
    for i, item in enumerate(data[:5], start=1):  # Limit to the first 5 matches
        host_team = item.get('home', {}).get('name', 'Unknown Host Team')
        guest_team = item.get('away', {}).get('name', 'Unknown Guest Team')
        
        # Extract recent form details for home team
        host_results = item.get('team_related_match', [{}])[0].get('five_previous_matches', [])
        host_wins = host_results.count('w')
        host_draws = host_results.count('d')
        host_losses = host_results.count('l')

        # Extract recent form details for away team
        guest_results = item.get('team_related_match', [{}])[1].get('five_previous_matches', [])
        guest_wins = guest_results.count('w')
        guest_draws = guest_results.count('d')
        guest_losses = guest_results.count('l')
        
        # Generate the description with recent form using ChatGPT API
        match_description = generate_match_description_with_recent_form(
            host_team, guest_team, host_results, host_wins, host_draws, host_losses,
            guest_results, guest_wins, guest_draws, guest_losses
        )
        
        # Format the data as required, including recent form details and structured summary
        match_info = {
            "description": match_description,
            "recent_form": {
                "home_team": {
                    "last_5_matches": host_results,
                    "wins": host_wins,
                    "draws": host_draws,
                    "losses": host_losses
                },
                "away_team": {
                    "last_5_matches": guest_results,
                    "wins": guest_wins,
                    "draws": guest_draws,
                    "losses": guest_losses
                }
            },
           
        }

        # Define the output file path for each match
        output_file = os.path.join(folder_name, f'match_{i}.json')
        
        # Write each match's description and recent form data to its own JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(match_info, f, ensure_ascii=False, indent=4)
        
        print(f"Match {i} description with recent form and structured summary saved to {output_file}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred with the API request: {e}")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON response: {e}")
except openai.error.OpenAIError as e:
    print(f"An error occurred with the OpenAI API: {e}")
except IOError as e:
    print(f"Error saving file: {e}")
