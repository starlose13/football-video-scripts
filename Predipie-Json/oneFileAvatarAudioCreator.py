import os
import json
import openai
from ProgramNumberManager import get_program_number, increment_program_number, reset_program_number
from dotenv import load_dotenv

# Load OpenAI API key
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Folders where JSON files are stored
folders = [
    "match_descriptions_scene2",  # secondEpisodeJsonCreator.py
    "match-scene3",               # thirdEpisodeJsonCreator.py
    "scene4",                     # fourthEpisodeJsonCreator.py
    "scene5",                     # fifthEpisodeJsonCreator.py
    "scene6"                      # sixEpisodeJsonCreator.py
]

# Output folder for final combined narration
output_folder = "combined-voiceAI"
os.makedirs(output_folder, exist_ok=True)

def read_description_from_json(file_path):
    """Reads the description from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data.get("description", "")

def generate_intro_with_openai(program_number):
    """Generates an introduction for the narration using OpenAI."""
    prompt = (
        f"Generate an engaging introduction for a football prediction video. "
        f"The episode number is {program_number}. The introduction should be friendly, "
        f"engaging, and in the style of a football commentator, with less than 60 words."
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
    return intro_text

# Main script to generate combined narration for five games in sequence
program_number = get_program_number()
increment_program_number()
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

# Closing statement
narration_parts.append(
    "Thanks for watching today’s episode! Don’t forget to tune in daily at 13:00 UTC "
    "for more match insights. Join the PrediPie community, and let’s make predictions together!"
)

# Combine narration parts into a single script
full_narration = " ".join(narration_parts)

# Save narration to a JSON file
output_file_path = os.path.join(output_folder, f"narration_episode_{program_number}.json")
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump({"narration": full_narration}, output_file, ensure_ascii=False, indent=4)

print(f"Narration for episode {program_number} saved to {output_file_path}")
