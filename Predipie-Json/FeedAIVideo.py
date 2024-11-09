import json
import logging
import os
import requests
from dotenv import load_dotenv
from typing import Dict, Optional

# Load environment variables
load_dotenv()
shotstack_api_key = os.getenv("SHOTSTACK_API_KEY")
shotstack_env = os.getenv("SHOTSTACK_ENVIRONMENT", "stage")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BASE_URL = f"https://api.shotstack.io/ingest/{shotstack_env}/sources"
scene_dir_template = './scene{scene_num}/match_{match_num}.json'
MAX_GAMES = 5
MAX_SCENES_PER_GAME = 5  # Each game has scenes from scene2 to scene6

def retrieve_ingested_file_links() -> Dict[str, str]:
    headers = {"x-api-key": shotstack_api_key, "Accept": "application/json"}
    with open("uploaded_files.json", "r") as f:
        uploaded_files = json.load(f)

    links = {}
    try:
        response = requests.get(BASE_URL, headers=headers)
        response.raise_for_status()
        for item in sorted(response.json()['data'], key=lambda x: x['attributes']['created'], reverse=True):
            if item['id'] in uploaded_files.values():
                file_name = [name for name, id in uploaded_files.items() if id == item['id']][0]
                links[file_name] = item['attributes']['source']
    except requests.RequestException as e:
        logging.error(f"Error retrieving file links: {e}")
    return links

def get_reading_time(scene_num: int, match_num: int) -> Optional[float]:
    try:
        with open(scene_dir_template.format(scene_num=scene_num, match_num=match_num), 'r') as scene_file:
            return json.load(scene_file).get('reading_time')
    except FileNotFoundError:
        logging.warning(f"Scene file not found for scene {scene_num}, match {match_num}.")
        return None

def build_timeline_and_merge(links: Dict[str, str]) -> Dict:
    timeline = {
        "background": "#ffffff",
        "tracks": [{"clips": []}]
    }
    merge = [{"find": "AVATAR", "replace": "https://your-avatar-url.com"}]
    previous_start = 0
    image_index = 0  # Start with IMAGE_0

    # Handle IMAGE_0 separately
    reading_time_image_1 = get_reading_time(2, 1)  # match_1, scene2 for IMAGE_1
    length_image_0 = reading_time_image_1 - 0.01 if reading_time_image_1 else 0
    file_link_image_0 = links.get("game_1_image_1.jpg")

    if file_link_image_0 and length_image_0 > 0:
        clip = {
            "asset": {"type": "image", "src": "{{ IMAGE_0 }}"},
            "effect": "zoomInSlow",
            "transition": {"in": "carouselLeft"},
            "position": "center",
            "length": length_image_0,
            "start": previous_start
        }
        timeline["tracks"][0]["clips"].append(clip)
        merge.append({"find": "IMAGE_0", "replace": file_link_image_0})
        previous_start = length_image_0  # Update start for IMAGE_1
        image_index += 1

    # Start from IMAGE_1 and continue for IMAGE_1 to IMAGE_26
    for match_num in range(1, MAX_GAMES + 1):  # match_1 to match_5
        for scene_num in range(2, 7):  # scene2 to scene6
            placeholder = f"IMAGE_{image_index}"
            file_link = links.get(f"game_{match_num}_image_{scene_num - 1}.jpg")
            reading_time = get_reading_time(scene_num, match_num)

            if file_link and reading_time is not None:
                clip = {
                    "asset": {"type": "image", "src": f"{{{{ {placeholder} }}}}"},
                    "effect": "zoomInSlow",
                    "transition": {"in": "carouselLeft"},
                    "position": "center",
                    "length": reading_time,
                    "start": previous_start
                }
                timeline["tracks"][0]["clips"].append(clip)
                merge.append({"find": placeholder, "replace": file_link})
                
                # Update start time and move to the next IMAGE_X
                previous_start += reading_time
                image_index += 1

    return {"timeline": timeline, "merge": merge}

def main():
    # Set up the template
    output_template = {
        "output": {"format": "mp4", "fps": 25, "size": {"width": 1920, "height": 1080}}
    }

    # Load data
    links = retrieve_ingested_file_links()
    
    # Generate timeline and merge sections
    timeline_and_merge = build_timeline_and_merge(links)
    
    # Combine with template
    final_output = {**timeline_and_merge, **output_template}

    # Save the JSON file
    with open("assemble-video-updated.json", "w") as f:
        json.dump(final_output, f, indent=4)
    logging.info("JSON saved successfully.")

if __name__ == "__main__":
    main()
