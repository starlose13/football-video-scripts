import os
import json
import time
import requests
import openai
from dotenv import load_dotenv
from ProgramNumberManager import get_program_number, increment_program_number, reset_program_number

# Load OpenAI and Creatify API keys
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
X_API_ID = os.getenv('CREATIFY_API_ID')
X_API_KEY = os.getenv('CREATIFY_API_KEY')
creator_id = "3f2a4ff3-3aa8-4522-b545-0814627a31b9"  # Replace with your actual creator ID from Creatify
program_name = "Predi Pie Fans"
increment_program_number()
program_number = get_program_number()
# Folders where JSON files are stored
folders = [
    "scene2",  # secondEpisodeJsonCreator.py
    "scene3",               # thirdEpisodeJsonCreator.py
    "scene4",                     # fourthEpisodeJsonCreator.py
    "scene5",                     # fifthEpisodeJsonCreator.py
    "scene6"                      # sixEpisodeJsonCreator.py
]
adjusted_reading_speed = 3.10

# Define punctuation pause times
pause_times = {
    ',': 0.21,
    '.': 0.21,
    '!': 0.18,
    '?': 0.18,
    ';': 0.17,
}


# Output folder for final combined narration
output_folder = "combined-voiceAI"
os.makedirs(output_folder, exist_ok=True)

def read_description_from_json(file_path):
    """Reads the description from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data.get("description", "")

def generate_intro_with_openai(program_number):
    """Generates an introduction for the narration using OpenAI and calculates reading time."""

    # Construct the prompt for OpenAI
    prompt = (
    f"Start with: 'Hi {program_name}!' Tonight, we’re bringing you 5 fantastic lineup of top matches for you. "
    f"Keep it upbeat, friendly, and super energetic. Make it concise—under 40 words with a punchy, engaging tone! "
    f"Use only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon. "
    f"Important: Do not mention any game statistics, player names, or game history information in the output."
)




    # Use OpenAI API to generate a custom introduction
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant generating a football video introduction."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=60
    )

    # Extract generated introduction
    intro_text = response['choices'][0]['message']['content'].strip()

    # Calculate word count
    word_count = len(intro_text.split())

    # Calculate total punctuation pause time
    pause_time = sum(intro_text.count(p) * pause_times.get(p, 0) for p in pause_times)

    # Calculate reading time based on word count, adjusted reading speed, and punctuation pauses
    reading_time = round((word_count / adjusted_reading_speed) + pause_time, 2)

    # Format the data to save in JSON
    intro_info = {
        "prompt_output": intro_text,
        "word_count": word_count,
        "reading_time": reading_time
    }

    # Define the output folder and create it if it doesn't exist
    folder_name = "intro"
    os.makedirs(folder_name, exist_ok=True)

    # Define the fixed output file path
    output_file = os.path.join(folder_name, 'intro.json')

    # Write the intro details to the JSON file, replacing any existing file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(intro_info, f, ensure_ascii=False, indent=4)
    
    print(f"Introduction for Episode {program_number} saved to {output_file}")
    
    return intro_text

def generate_closing_with_openai(program_number):
    """Generates a closing statement for the narration using OpenAI."""
    prompt = (
    f" Wrap up Episode {program_number} with: 'Remember, I'm just an AI; this isn't financial advice!' "
    f"Encourage viewers to tune in daily at 13 UTC, join the PrediPie community, and end with 'dont trade your life for an entertainment ,Goodbye!'"
    f"it should be complete and under 25 words"
    f"use these punctuation marks in the output alot : dot, comma, exclamation mark, question mark, and semicolon."
    )


    # Use OpenAI API to generate a custom closing statement
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant generating a football video closing statement."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    
    # Extract generated closing statement
    closing_text = response['choices'][0]['message']['content'].strip()
    return closing_text


def create_video_with_creatify(narration_text, program_number):
    """Generates a lipsync video using the Creatify API."""
    lipsync_url = "https://api.creatify.ai/api/lipsyncs/"
    headers = {
        "X-API-ID": X_API_ID,
        "X-API-KEY": X_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": narration_text,
        "creator": creator_id,
        "aspect_ratio": "1:1"
    }

    # Send POST request to initiate video generation
    response = requests.post(lipsync_url, headers=headers, json=payload)
    if response.status_code == 200:
        lipsync_data = response.json()
        lipsync_id = lipsync_data.get("id")
        print(f"Video generation initiated. Lipsync ID: {lipsync_id}")

        # Check video generation status
        status_url = f"https://api.creatify.ai/api/lipsyncs/{lipsync_id}/"
        video_ready = False
        while not video_ready:
            status_response = requests.get(status_url, headers=headers)
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status")
                if status == "done":
                    video_ready = True
                    video_url = status_data.get("output")
                    print(f"Video generation completed. Download your video at: {video_url}")
                    return video_url
                else:
                    print("Video generation in progress. Checking again in 10 seconds...")
                    time.sleep(10)
            else:
                print(f"Failed to check status: {status_response.text}")
                break
    else:
        print(f"Failed to initiate video generation: {response.text}")
    return None

# Main script to generate combined narration for five games in sequence

intro_text = generate_intro_with_openai(program_number)

narration_parts = []
narration_parts.append(intro_text)  # Add introduction

# Loop over each of the five matches to gather descriptions in sequence
for match_number in range(1, 6):
    for folder in folders:
        file_path = os.path.join(folder, f"match_{match_number}.json")
        if os.path.exists(file_path):
            description = read_description_from_json(file_path)
            narration_parts.append(description)

# Generate dynamic closing statement using OpenAI
closing_text = generate_closing_with_openai(program_number)
narration_parts.append(closing_text)

# Combine narration parts into a single script
full_narration = " ".join(narration_parts)

# Save narration to a JSON file
output_file_path = os.path.join(output_folder, f"narration_episode_{program_number}.json")
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump({"narration": full_narration}, output_file, ensure_ascii=False, indent=4)

print(f"Narration for episode {program_number} saved to {output_file_path}")

# Generate video with Creatify API
# video_url = create_video_with_creatify(full_narration, program_number)
# if video_url:
#     print(f"Video for episode {program_number} is ready: {video_url}")
# else:
#     print("Failed to generate the video.")
