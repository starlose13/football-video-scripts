import json
import os

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Define the path to match_data1.json in scene1 folder
file_path_1 = os.path.join(script_dir, 'scene3', 'match_2.json')

# Define the path to match_1.json in scene2 folder
file_path_2 = os.path.join(script_dir, 'scene2', 'match_1.json')

# Read the first JSON data from scene1/match_data1.json
try:
    with open(file_path_1, 'r') as file:
        json_data_1 = json.load(file)
except FileNotFoundError:
    print(f"File not found: {file_path_1}")
    exit(1)

# Read the second JSON data from scene2/match_1.json
try:
    with open(file_path_2, 'r') as file:
        json_data_2 = json.load(file)
except FileNotFoundError:
    print(f"File not found: {file_path_2}")
    exit(1)

# Integrate the description from the first JSON into the second JSON under the "pouya" field
json_data_2["pouya"] = json_data_1["description"]

# Define the output path for the updated file
output_path = os.path.join(script_dir, 'scene2', 'updated_match_2.json')
with open(output_path, 'w') as file:
    json.dump(json_data_2, file, indent=4)

print(f"Updated JSON data saved to '{output_path}'.")
