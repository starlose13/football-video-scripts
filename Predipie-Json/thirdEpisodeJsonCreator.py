import requests
import json
import os
import openai
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define the API endpoint
url = 'https://dataprovider.predipie.com/api/v1/ai/test/'

# Adjusted reading speed (words per second) including pauses
adjusted_reading_speed = 3.10

# Define punctuation pause times
pause_times = {
    ',': 0.21,
    '.': 0.21,
    '!': 0.18,
    '?': 0.18,
    ';': 0.17,
}

# Function to generate a match description with the ChatGPT API
def generate_match_description(host_team, guest_team, match_time):
    # Format the match time to extract date and time
    match_datetime = datetime.strptime(match_time, "%Y-%m-%dT%H:%M:%SZ")
    time_str = match_datetime.strftime("%I:%M %p").lstrip("0")
    day_str = match_datetime.strftime("%A")
    date_str = match_datetime.strftime("%Y-%m-%d")
    
    # Create a prompt for OpenAI to generate the description
    prompt = (
    f"As if you're a live TV host, build excitement announcemen for the game of football.this match starts at : {time_str} on {day_str}, {date_str}' "
    f"Keep it upbeat, clear, and full of energy to captivate the audience.also it should be complete and under 22 words"
    "Remember: only use these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon."
)


    # Call the ChatGPT API to generate the description
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant helping to create dynamic football match descriptions."},
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

    # Create the folder `match-scene3` to store the files if it doesn't already exist
    folder_name = 'scene3'
    os.makedirs(folder_name, exist_ok=True)

    # Extract and save each of the first 5 matches to separate JSON files
    for i, item in enumerate(data[:5], start=1):  # Limit to the first 5 matches
        # Extract team and match details
        host_team = item.get('home', {}).get('name', 'Unknown Host Team')
        guest_team = item.get('away', {}).get('name', 'Unknown Guest Team')
        match_time = item.get('start_time', 'Unknown Time')
        
        # Parse match date and time fields
        match_datetime = datetime.strptime(match_time, "%Y-%m-%dT%H:%M:%SZ")
        match_date = match_datetime.strftime("%Y-%m-%d")
        match_time_str = match_datetime.strftime("%I:%M %p")
        match_day = match_datetime.strftime("%A")
        
        # Extract logos and countries for teams
        host_team_logo = item.get('home', {}).get('logo', 'No Logo Available')
        guest_team_logo = item.get('away', {}).get('logo', 'No Logo Available')
        host_team_country = item.get('home', {}).get('country', {}).get('name', 'Unknown Country') if item.get('home', {}).get('country') else 'Unknown Country'
        guest_team_country = item.get('away', {}).get('country', {}).get('name', 'Unknown Country') if item.get('away', {}).get('country') else 'Unknown Country'
        
        # Extract odds for the match
        home_odds = item.get('odds', {}).get('home', 'N/A')
        draw_odds = item.get('odds', {}).get('draw', 'N/A')
        guest_odds = item.get('odds', {}).get('away', 'N/A')
        
        # Generate the description using ChatGPT API
        match_description = generate_match_description(host_team, guest_team, match_time)
        
        # Calculate the word count of the generated description
        word_count = len(match_description.split())
        
        # Calculate the total punctuation pause time
        pause_time = sum(match_description.count(p) * pause_times.get(p, 0) for p in pause_times)
        
        # Calculate reading time based on word count, adjusted reading speed, and punctuation pauses
        reading_time = round((word_count / adjusted_reading_speed) + pause_time, 2)
        
        # Format the data with all details
        match_info = {
            "description": match_description,
            "match_date": match_date,
            "match_time": match_time_str + " (UTC Time)",
            "match_day": match_day,
            "odds": {
                "home": home_odds,
                "draw": draw_odds,
                "away": guest_odds
            },
            "word_count": word_count,  # Include word count
            "reading_time": reading_time,  # Include calculated reading time
            "home_team": {
                "name": host_team,
                "logo": host_team_logo,
                "country": host_team_country
            },
            "away_team": {
                "name": guest_team,
                "logo": guest_team_logo,
                "country": guest_team_country
            }
        }

        # Define the output file path for each match
        output_file = os.path.join(folder_name, f'match_{i}.json')
        
        # Write each match's description and team details to its own JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(match_info, f, ensure_ascii=False, indent=4)
        
        print(f"Match {i} description and additional data saved to {output_file}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred with the API request: {e}")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON response: {e}")
except openai.error.OpenAIError as e:
    print(f"An error occurred with the OpenAI API: {e}")
except IOError as e:
    print(f"Error saving file: {e}")
