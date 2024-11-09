import os
import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
from dotenv import load_dotenv

load_dotenv()



# Generate images and save them to the output directory
folder = "generated_images"  # GitHub repository folder to save images
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)
shotstack_api_key = os.getenv("SHOTSTACK_API_KEY")

if not shotstack_api_key:
    raise ValueError("SHOTSTACK_API_KEY is missing. Please check your .env file.")

# Automatically set the base directory for JSON files relative to the script's location
base_json_dir = os.path.join(os.path.dirname(__file__), 'scene{scene_num}')
# Define the image template paths
templates = [
    './assets/match-introduction.jpg',
    './assets/stats.jpg',
    './assets/odds.jpg',
    './assets/recent-matches.jpg',
    './assets/away.jpg'
]

# Define JSON path templates for each image, replacing scene number dynamically
json_paths = [
    os.path.join(base_json_dir.format(scene_num=2), 'match_{i}.json'),
    os.path.join(base_json_dir.format(scene_num=3), 'match_{i}.json'),
    os.path.join(base_json_dir.format(scene_num=4), 'match_{i}.json'),
    os.path.join(base_json_dir.format(scene_num=5), 'match_{i}.json'),
    os.path.join(base_json_dir.format(scene_num=6), 'match_{i}.json')
]

base_positions = {
    "home_team_logo": (410, 845),
    "home_team_name": (730, 900),
    "away_team_logo": (3220, 845),
    "away_team_name": (2480, 900)
}

# Define unique positions for each image template, which will inherit base positions
position_mappings = [
    {**base_positions},
    {**base_positions, "match_date": (1736 , 847), "match_time": (2031, 847), "match_day": (1590, 847)},
    {**base_positions, "home_odds": (1298, 1086), "draw_odds": (1870, 1086), "away_odds": (2435, 1086)},
    {**base_positions, "home_team_last_5": (1137, 1357), "away_team_last_5": (2350, 1357)},
    {**base_positions}
]


def add_program_number_to_starting_scene(json_path, image_path, output_path, position=(2230, 125), font_size=110):
    """
    Adds the program number from JSON data to a specified position on an image.

    Parameters:
        json_path (str): Path to the JSON file containing the program number.
        image_path (str): Path to the image file where the program number will be added.
        output_path (str): Path where the modified image will be saved.
        position (tuple): Position (x, y) to place the program number on the image.
        font_size (int): Font size for the program number text.
    """
    # Load the program number from the JSON file
    try:
        with open(json_path, 'r') as file:
            json_data = json.load(file)
            program_number = str(json_data.get("program_number", ""))  # Read 'program_number' field
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_path}")
        return
    except json.JSONDecodeError:
        print("Error: JSON file is not properly formatted.")
        return
    
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Load the font
    try:
        font = ImageFont.truetype("Roboto-Bold.ttf", font_size)
    except IOError:
        print("Custom font not found, using default font.")
        font = ImageFont.load_default()

    # Define font color
    font_color = "white"
    
    # Draw the program number on the image
    draw.text(position, program_number, fill=font_color, font=font)
    
    # Save the modified image
    image.save(output_path)
    print(f"Image saved at {output_path}")



def load_json_data(filepath):
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Warning: JSON file not found at {filepath}")
        return {}  # Return an empty dictionary if the file is missing

def get_data_for_image(json_data, image_index):
    # Same data extraction logic based on image index
    if image_index == 0:
        return {
            "home_team_name": json_data.get("home_team", {}).get("name", ""),
            "home_team_logo": json_data.get("home_team", {}).get("logo", ""),
            "away_team_name": json_data.get("away_team", {}).get("name", ""),
            "away_team_logo": json_data.get("away_team", {}).get("logo", "")
        }
    elif image_index == 1:
        return {
            "match_date": json_data.get("match_date", ""),
            "match_time": json_data.get("match_time", ""),
            "match_day": json_data.get("match_day", "")
        }
    elif image_index == 2:
        return {
            "home_odds": json_data.get("odds", {}).get("home", ""),
            "draw_odds": json_data.get("odds", {}).get("draw", ""),
            "away_odds": json_data.get("odds", {}).get("away", "")
            
        }
    elif image_index == 3:
        return {
            "home_team_last_5": json_data.get("recent_form", {}).get("home_team", {}).get("last_5_matches", ""),
            "away_team_last_5": json_data.get("recent_form", {}).get("away_team", {}).get("last_5_matches", "")
        }
    elif image_index == 4:
        return {
            "card": json_data.get("card", "")
        }
    return {}


def fill_image_template(template_path, json_data, positions, previous_positions=None, previous_data=None, font_size=80, background_color="#0056d7"):    
    image = Image.open(template_path)
    draw = ImageDraw.Draw(image)
    
    # Load fonts for different sizes
    try:
        default_font = ImageFont.truetype("Roboto-Bold.ttf", font_size)  # Default font size 80
        small_font = ImageFont.truetype("Roboto-Bold.ttf", 30)  # Small font for match details
        medium_font = ImageFont.truetype("Roboto-Bold.ttf", 55)  # Medium font for odds fields
    except IOError:
        print("Custom font not found, using default font.")
        default_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        medium_font = ImageFont.load_default()

    # Load and slightly increase the size of icons for win, draw, and lose
    icon_size = (60, 60)
    win_icon = Image.open('./assets/win.png').resize(icon_size)
    draw_icon = Image.open('./assets/draw.png').resize(icon_size)
    lose_icon = Image.open('./assets/lose.png').resize(icon_size)

    # Combine previous and current positions and data
    all_positions = {**(previous_positions or {}), **positions}
    all_data = {**(previous_data or {}), **json_data}  # Ensure previous_data is included in every image
    
    # Choose a color for high contrast with a blue background
    font_color = "white"
    
    for key, pos in all_positions.items():
        if key in all_data:
            # Choose font size based on the specific key
            if key in ["match_date", "match_time", "match_day"]:
                font = small_font
            elif key in ["home_odds", "draw_odds", "away_odds"]:
                font = medium_font
            else:
                font = default_font
            
            if "logo" in key:  # Handle logo image
                logo_url = all_data[key]
                try:
                    response = requests.get(logo_url)
                    logo = Image.open(BytesIO(response.content))
                    
                    # Convert to RGBA and resize to fit a 200x200 circle
                    if logo.mode != "RGBA":
                        logo = logo.convert("RGBA")
                    logo = logo.resize((228, 228))
                    
                    # Create a circular mask with the specified background color
                    mask = Image.new("RGBA", (228, 228), background_color)
                    draw_mask = ImageDraw.Draw(mask)
                    draw_mask.ellipse((0, 0, 228, 228), fill=(0, 0, 0, 0))  # Transparent fill for the circular area

                    # Apply mask to the logo
                    logo = Image.alpha_composite(mask, logo)

                    # Paste the circular logo with background on the template
                    image.paste(logo, pos, logo)
                except Exception as e:
                    print(f"Could not load logo from {logo_url}: {e}")
            
            elif key == "home_team_last_5":  # Handle recent matches for home team
                recent_matches = all_data[key]
                icon_spacing = 70  # Adjust spacing between icons
                x_offset = pos[0]
                
                for result in recent_matches:
                    # Select the appropriate icon
                    if result == 'w':
                        icon = win_icon
                    elif result == 'd':
                        icon = draw_icon
                    elif result == 'l':
                        icon = lose_icon
                    else:
                        continue  # Skip if not 'w', 'd', or 'l'
                    
                    # Paste the icon and update x position
                    image.paste(icon, (x_offset, pos[1]), icon)
                    x_offset += icon_spacing

            elif key == "away_team_last_5":  # Handle recent matches for away team
                recent_matches = all_data[key]
                icon_spacing = 70  # Adjust spacing between icons
                x_offset = pos[0]
                
                for result in recent_matches:
                    # Select the appropriate icon
                    if result == 'w':
                        icon = win_icon
                    elif result == 'd':
                        icon = draw_icon
                    elif result == 'l':
                        icon = lose_icon
                    else:
                        continue  # Skip if not 'w', 'd', or 'l'
                    
                    # Paste the icon and update x position
                    image.paste(icon, (x_offset, pos[1]), icon)
                    x_offset += icon_spacing

            elif "name" in key:  # Handle team name text
                team_name = str(all_data[key])
                
                # Measure text width to adjust the distance from the logo
                text_bbox = draw.textbbox((0, 0), team_name, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                
                # Determine position based on the logo position
                if "home_team" in key:
                    # Position the name to the right of the home team logo, with some padding
                    name_pos = (positions["home_team_logo"][0] + 200 + 80, positions["home_team_logo"][1] + (200 - font_size) // 2)
                elif "away_team" in key:
                    # Position the name to the left of the away team logo, with some padding
                    name_pos = (positions["away_team_logo"][0] - text_width - 80, positions["away_team_logo"][1] + (200 - font_size) // 2)
                
                # Draw team name with dynamically calculated position
                draw.text(name_pos, team_name, fill=font_color, font=font)
                all_positions[key] = name_pos  # Update position tracking
            else:  # Handle other text fields
                text_value = str(all_data[key])
                draw.text(pos, text_value, fill=font_color, font=font)
                all_positions[key] = pos

    return image, all_positions, all_data



def generate_images_for_game(game_index, templates, json_paths, position_mappings):
    images = []
    previous_positions = {}  # Keeps track of positions across images
    previous_data = {}        # Keeps track of data across images
    
    # Define the adjusted positions for logos and names for all images except the fifth one
    adjusted_y_positions = {
        "home_team_logo": (position_mappings[0]["home_team_logo"][0], 375),
        "home_team_name": (position_mappings[0]["home_team_name"][0], 435),
        "away_team_logo": (position_mappings[0]["away_team_logo"][0], 375),
        "away_team_name": (position_mappings[0]["away_team_name"][0], 435)
    }

    fifth_image_positions = {
        "home_team_logo": (position_mappings[0]["home_team_logo"][0], 340),
        "home_team_name": (position_mappings[0]["home_team_name"][0], 400),
        "away_team_logo": (position_mappings[0]["away_team_logo"][0], 340),
        "away_team_name": (position_mappings[0]["away_team_name"][0], 400),
        "match_date": (1700, 1307),
        "match_time": (1994, 1307),
        "match_day": (1554, 1307),
        "home_odds": (1275, 1546),
        "draw_odds": (1847, 1546),
        "away_odds": (2413, 1546),
        "home_team_last_5": (1128, 1813),
        "away_team_last_5": (2284, 1813),
    }
    
    for i, template_path in enumerate(templates):
        json_data_path = json_paths[i].format(i=game_index + 1)
        
        # Load JSON data with error handling
        json_data = load_json_data(json_data_path)
        
        # Get specific data for the current image
        image_data = get_data_for_image(json_data, i)
        
        # Apply adjusted positions for all images except the fifth one
        if i == 4:  # Check if it’s the fifth image
            card_result = image_data.get("card", "")
            # Determine the template based on card result
            if card_result == "Win or Draw Away Team":
                template_path = './assets/draw-away.jpg'
            elif card_result == "Win or Draw Home Team":
                template_path = './assets/home-draw.jpg'
            elif card_result == "Win Home or Away Team":
                template_path = './assets/home-away.jpg'
            elif card_result == "Win Home Team":
                template_path = './assets/home.jpg'
            elif card_result == "Win Away Team":
                template_path = './assets/away.jpg'
            else:
                template_path = templates[i]  # Default to original fifth image if card result doesn't match
            
            adjusted_positions = {**position_mappings[i], **fifth_image_positions}
            font_size = 60  # Reduced font size for home_team_name and away_team_name on the fifth image
        elif i != 0:
            adjusted_positions = {**position_mappings[i], **adjusted_y_positions}
        else:
            adjusted_positions = position_mappings[i]
            font_size = 80  # Default font size for other images

        # Fill image template with JSON data and inherited base data and positions
        image, previous_positions, previous_data = fill_image_template(
            template_path,
            image_data,
            adjusted_positions,
            previous_positions=previous_positions,
            previous_data=previous_data,
            font_size=font_size
        )
        images.append(image)
    
    return images





def get_signed_url():
    signed_url_request_url = "https://api.shotstack.io/ingest/stage/upload"
    headers = {"Accept": "application/json", "x-api-key": shotstack_api_key}
    response = requests.post(signed_url_request_url, headers=headers)
    if response.status_code == 200:
        data = response.json().get("data", {}).get("attributes", {})
        return data.get("url"), data.get("id")
    print("Failed to obtain signed URL:", response.status_code, response.text)
    return None, None

def upload_image_to_shotstack(image_path, file_name):
    signed_url, source_id = get_signed_url()
    if not signed_url:
        print(f"Skipping upload for {image_path}")
        return None

    with open(image_path, "rb") as file:
        upload_response = requests.put(signed_url, data=file)
        if upload_response.status_code == 200:
            print(f"Image uploaded successfully for {image_path}")
            # Save the source_id and original file name to track
            uploaded_files[file_name] = source_id
            return source_id
        print(f"Failed to upload {image_path}:", upload_response.status_code, upload_response.text)
    return None

uploaded_files = {}

def check_upload_status(source_id):
    """Check the status of the uploaded image by source ID."""
    status_url = f"https://api.shotstack.io/ingest/stage/sources/{source_id}"
    headers = {"Accept": "application/json", "x-api-key": shotstack_api_key}
    status_response = requests.get(status_url, headers=headers)
    if status_response.status_code == 200:
        attributes = status_response.json().get("data", {}).get("attributes", {})
        return attributes.get("status"), attributes.get("source")
    print("Failed to retrieve upload status:", status_response.status_code, status_response.text)
    return None, None


for game_index in range(5):  # Assuming 5 games
    game_images = generate_images_for_game(game_index, templates, json_paths, position_mappings)
    
    for i, img in enumerate(game_images):
        file_name = f"game_{game_index+1}_image_{i+1}.jpg"
        image_path = os.path.join(output_dir, file_name)
        img.save(image_path)
        
        # Upload each image to Shotstack
        source_id = upload_image_to_shotstack(image_path, file_name)
        if source_id:
            status, url = check_upload_status(source_id)
            print(f"Upload status for {image_path}: {status}")
            if status == "ready":
                print(f"Image URL: {url}")

# Save all uploaded file names and source IDs
with open("uploaded_files.json", "w") as f:
    json.dump(uploaded_files, f, indent=4)
print("Uploaded file names and source IDs have been saved to uploaded_files.json.")

# Upload the starting scene with program number to Shotstack
starting_scene_json_path = './program_number.json'
starting_scene_image_path = './assets/starting-scene.jpg'
starting_scene_output_path = './output/starting-scene-with-program-number.jpg'
add_program_number_to_starting_scene(starting_scene_json_path, starting_scene_image_path, starting_scene_output_path)

# Track starting scene upload with file name
source_id = upload_image_to_shotstack(starting_scene_output_path, "starting-scene-with-program-number.jpg")

if source_id:
    status, url = check_upload_status(source_id)
    print(f"Starting scene upload status: {status}")
    if status == "ready":
        print(f"Starting scene URL: {url}")