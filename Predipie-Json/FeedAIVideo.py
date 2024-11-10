import json
import logging
import os
import requests
from dotenv import load_dotenv
from typing import Dict, Optional

# Load environment variables
load_dotenv()
shotstack_api_key = os.getenv("SHOTSTACK_API_KEY")
shotstack_env = os.getenv("SHOTSTACK_ENVIRONMENT", "production")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BASE_URL = f"https://api.shotstack.io/ingest/v1/sources"
scene_dir_template = './scene{scene_num}/match_{match_num}.json'
MAX_GAMES = 5
MAX_SCENES_PER_GAME = 5  # Each game has scenes from scene2 to scene6

def retrieve_ingested_file_links() -> (Dict[str, str], Optional[str]):
    headers = {"x-api-key": shotstack_api_key, "Accept": "application/json"}
    with open("uploaded_files.json", "r") as f:
        uploaded_files = json.load(f)

    links = {}
    file_url = None  # Initialize file_url

    try:
        response = requests.get(BASE_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        # Sort 'data' list by 'created' attribute in descending order
        sorted_data = sorted(data['data'], key=lambda x: x['attributes']['created'], reverse=True)
        for item in sorted_data:
            if item['id'] in uploaded_files.values():
                file_name = [name for name, id in uploaded_files.items() if id == item['id']][0]
                file_url = item['attributes']['source']  # Set file_url for the last matched item
                links[file_name] = file_url
        with open("ingested_files_links.json", "w") as json_file:
            json.dump(links, json_file, indent=4)
            
        print("Ingested file URLs with original names have been saved to ingested_files_links.json")
    except requests.RequestException as e:
        logging.error(f"Error retrieving file links: {e}")
    
    return links, file_url  # Return both links and file_url

def get_reading_time(scene_num: int, match_num: int) -> Optional[float]:
    try:
        with open(scene_dir_template.format(scene_num=scene_num, match_num=match_num), 'r') as scene_file:
            return json.load(scene_file).get('reading_time')
    except FileNotFoundError:
        logging.warning(f"Scene file not found for scene {scene_num}, match {match_num}.")
        return None

def build_timeline_and_merge(links: Dict[str, str]) -> Dict:
    # Load AVATAR URL from shotstack_video_url.json
    avatar_url = ""
    try:
        with open("shotstack_video_url.json", "r") as file:
            shotstack_data = json.load(file)
            avatar_url = shotstack_data.get("shotstack_video_url", avatar_url)
    except FileNotFoundError:
        print("shotstack_video_url.json file not found. Using default avatar URL.")

    # Load intro.json reading_time
    intro_reading_time = 0
    intro_file_path = os.path.join("intro", "intro.json")
    if os.path.exists(intro_file_path):
        try:
            with open(intro_file_path, "r") as intro_file:
                intro_data = json.load(intro_file)
                intro_reading_time = intro_data.get("reading_time", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Error reading intro.json or missing reading_time in {intro_file_path}. Using default of 0.")

    # Define timeline and merge structures
    timeline = {
        "background": "#ffffff",
        "tracks": [{"clips": []}]
    }
    merge = [{"find": "AVATAR", "replace": avatar_url}]
    previous_start = 0  # Initialize start time for the first clip
    image_index = 0

    # Add AVATAR clip with the specified structure and resolve "{{ AVATAR }}" placeholder
    avatar_clip = {
        "asset": {
            "type": "video",
            "src": "{{ AVATAR }}",
            "volume": 1
        },
        "offset": {
            "x": 0.388,
            "y": -0.308
        },
        "fit": "cover",
        "scale": 0.25,
        "start": previous_start,
        "length": "auto"
    }
    timeline["tracks"][0]["clips"].append(avatar_clip)

    # Handle IMAGE_0 with starting-scene-with-program-number.jpg
    length_image_0 = intro_reading_time
    file_link_image_0 = links.get("starting-scene-with-program-number.jpg")

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
        previous_start += length_image_0  # Update start for the next image
        image_index += 1

    # Add clips dynamically from IMAGE_1 to IMAGE_25
    for match_num in range(1, MAX_GAMES + 1):
        for scene_num in range(2, 7):
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
                    "start": previous_start  # Dynamically calculated
                }
                timeline["tracks"][0]["clips"].append(clip)
                merge.append({"find": placeholder, "replace": file_link})
                
                previous_start += reading_time  # Update start time for the next clip
                image_index += 1

    # Add IMAGE_26 with a fixed length of 4 seconds
    file_link_image_26 = "https://shotstack-ingest-api-v1-sources.s3.ap-southeast-2.amazonaws.com/4c7kem3rad/zzz01jc8-kngdq-12qg8-2xyk7-4nv8h3/source.jpg"
    if file_link_image_26:
        clip = {
            "asset": {"type": "image", "src": "{{ IMAGE_26 }}"},
            "effect": "zoomInSlow",
            "transition": {"in": "carouselLeft"},
            "position": "center",
            "length": 4,
            "start": previous_start
        }
        timeline["tracks"][0]["clips"].append(clip)
        merge.append({"find": "IMAGE_26", "replace": file_link_image_26})
        previous_start += 4  # Update start for IMAGE_27

    # Add IMAGE_27 with a dynamic or "auto" length
    file_link_image_27 = "https://shotstack-ingest-api-v1-sources.s3.ap-southeast-2.amazonaws.com/4c7kem3rad/zzz01jc8-kpwf1-nxm7v-2r4fn-a8wyf1/source.jpg"
    if file_link_image_27:
        clip = {
            "asset": {"type": "image", "src": "{{ IMAGE_27 }}"},
            "effect": "zoomInSlow",
            "transition": {"in": "carouselLeft"},
            "position": "center",
            "length": "auto",
            "start": previous_start
        }
        timeline["tracks"][0]["clips"].append(clip)
        merge.append({"find": "IMAGE_27", "replace": file_link_image_27})

    final_output = {"timeline": timeline, "merge": merge}

    # Save the JSON to assemble-video-updated.json
    with open("assemble-video-updated.json", "w") as f:
        json.dump(final_output, f, indent=4)
    print("AVATAR and timeline added to assemble-video-updated.json successfully.")
    
    return final_output



def main():
    # Set up the template
    output_template = {
        "output": {"format": "mp4", "fps": 25, "size": {"width": 1920, "height": 1080}}
    }

    # Load data
    links, file_url = retrieve_ingested_file_links()  # Unpack both links and file_url
    
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
