import os
import json
import openai
from ProgramNumberManager import get_program_number, increment_program_number,reset_program_number
from dotenv import load_dotenv

# Define your OpenAI API key
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
# Folders where the JSON files are stored
folders = [
    "match_descriptions_scene2",  # secondEpisodeJsonCreator.py
    "match-scene3",               # thirdEpisodeJsonCreator.py
    "scene4",                     # fourthEpisodeJsonCreator.py
    "scene5",                     # fifthEpisodeJsonCreator.py
    "scene6"                      # sixEpisodeJsonCreator.py
]

# Output folder for final combined narrations
output_folder = "voiceAI"
os.makedirs(output_folder, exist_ok=True)

def read_description_from_json(file_path):
    """Reads the description from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data.get("description", "")

def generate_intro_with_openai(program_number):
    """Generates an introduction for the narration using OpenAI."""
    prompt = (
        f"Generate an introduction for a football prediction video. less than 60 characters "
        f"The episode number is {program_number}. "
        f"The introduction should be friendly, engaging, and in the style of a football commentator."
    )

    # Use OpenAI's API to create a custom introduction
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant generating a football video introduction."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    
    # Extract the generated introduction from the response
    intro_text = response['choices'][0]['message']['content'].strip()
    return intro_text

# Generate combined narration for each match
for match_number in range(1, 6):  # Assuming each episode has 5 matches
    narration_parts = []
    program_number = get_program_number()
    increment_program_number()
    intro_text = generate_intro_with_openai(program_number)
    # Add introduction
    narration_parts.append(intro_text)

    # Extract descriptions from each folder for the current match
    for folder in folders:
        file_path = os.path.join(folder, f"match_{match_number}.json")
        if os.path.exists(file_path):
            description = read_description_from_json(file_path)
            narration_parts.append(description)

    # Closing part of the narration
    narration_parts.append("Thanks for watching today’s episode! Don’t forget to tune in daily at 11:00 UTC for more match insights. Join the PrediPie community, and let’s make predictions together!")

    # Combine narration parts into a single script
    full_narration = " ".join(narration_parts)

    # Save the narration to a new JSON file
    output_file_path = os.path.join(output_folder, f"narration_{match_number}.json")
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump({"narration": full_narration}, output_file, ensure_ascii=False, indent=4)

    print(f"Narration for match {match_number} saved to {output_file_path}")


# reset_program_number()
