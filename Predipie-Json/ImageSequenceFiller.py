import os
import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

# Automatically set the base directory for JSON files relative to the script's location
base_json_dir = os.path.join(os.path.dirname(__file__), 'scene{scene_num}')

# Define the image template paths
templates = [
    './assets/match-introduction.jpg',
    './assets/stats.jpg',
    './assets/odds.jpg',
    './assets/recent-matches.jpg',
    './assets/Ai-analysis-suggestion.jpg'
]

# Define JSON path templates for each image, replacing scene number dynamically
json_paths = [
    os.path.join(base_json_dir.format(scene_num=2), 'match_{i}.json'),
    os.path.join(base_json_dir.format(scene_num=3), 'match_{i}.json'),
    os.path.join(base_json_dir.format(scene_num=4), 'match_{i}.json'),
    os.path.join(base_json_dir.format(scene_num=5), 'match_{i}.json'),
    os.path.join(base_json_dir.format(scene_num=6), 'match_{i}.json')
]

position_mappings = [
    # Positions for Match Introduction (scene2/match_{i}.json)
    {
        "home_team_logo": (410, 845),
        "home_team_name": (730, 900),
        "away_team_logo": (3220, 845),
        "away_team_name": (2480, 900)
    },
    # Positions for Stats (scene3/match_{i}.json)
    {
        "match_date": (50, 50),
        "match_time": (50, 100),
        "match_day": (50, 150)
    },
    # Positions for Odds (scene4/match_{i}.json)
    {
        "home_odds": (50, 100),
        "away_odds": (200, 100),
        "draw_odds": (350, 100)
    },
    # Positions for Recent Matches (scene5/match_{i}.json)
    {
        "home_team_last_5": (50, 100),
        "away_team_last_5": (400, 100)
    },
    # Positions for AI Analysis Suggestion (scene6/match_{i}.json)
    {
        "card": (50, 100)
    }
]

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
            "away_odds": json_data.get("odds", {}).get("away", ""),
            "draw_odds": json_data.get("odds", {}).get("draw", "")
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


def fill_image_template(template_path, json_data, positions, previous_positions=None, font_size=80):
    image = Image.open(template_path)
    draw = ImageDraw.Draw(image)
    
    # Load a bold, sans-serif font appropriate for sports reporting
    try:
        font = ImageFont.truetype("Roboto-Bold.ttf", font_size)
    except IOError:
        print("Custom font not found, using default font.")
        font = ImageFont.load_default()

    # Combine previous and current positions
    all_positions = {**previous_positions} if previous_positions else {}
    
    # Choose a color for high contrast with a blue background
    font_color = "white"
    
    for key, pos in positions.items():
        if key in json_data:
            if "logo" in key:  # Handle logo image
                logo_url = json_data[key]
                
                try:
                    response = requests.get(logo_url)
                    logo = Image.open(BytesIO(response.content))
                    
                    # Convert to RGBA and resize to fit a 200x200 circle
                    if logo.mode != "RGBA":
                        logo = logo.convert("RGBA")
                    logo = logo.resize((200, 200))  # Smaller diameter for further reduction
                    
                    # Create a circular mask
                    mask = Image.new("L", (200, 200), 0)
                    draw_mask = ImageDraw.Draw(mask)
                    draw_mask.ellipse((0, 0, 200, 200), fill=255)
                    
                    # Apply mask to create a circular logo
                    logo.putalpha(mask)
                    
                    # Paste the circular logo on the template
                    image.paste(logo, pos, logo)  # Using logo as the mask to retain transparency
                except Exception as e:
                    print(f"Could not load logo from {logo_url}: {e}")
            
            elif "name" in key:  # Handle team name text with dynamic positioning
                team_name = str(json_data[key])
                
                # Get the bounding box for the text to determine its width and height
                text_bbox = font.getbbox(team_name)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # Adjust name position based on text width relative to logo
                if "home_team" in key:
                    name_pos = (positions["home_team_logo"][0] + 200 + 80, pos[1])  # 10 pixels right of the logo
                elif "away_team" in key:
                    name_pos = (positions["away_team_logo"][0] - text_width - 80, pos[1])  # 10 pixels left of the logo
                
                # Draw team name with calculated position
                draw.text(name_pos, team_name, fill=font_color, font=font)
                all_positions[key] = name_pos  # Update position tracking
            else:  # Handle other text fields
                text_value = str(json_data[key])
                draw.text(pos, text_value, fill=font_color, font=font)
                all_positions[key] = pos

    return image, all_positions


def generate_images_for_game(game_index, templates, json_paths, position_mappings):
    images = []
    previous_positions = {}  # Keeps track of positions across images
    
    for i, template_path in enumerate(templates):
        json_data_path = json_paths[i].format(i=game_index + 1)
        
        # Load JSON data with error handling
        json_data = load_json_data(json_data_path)
        
        # Get specific data for the current image
        image_data = get_data_for_image(json_data, i)
        
        # Fill image template with JSON data
        image, previous_positions = fill_image_template(
            template_path,
            image_data,
            position_mappings[i],
            previous_positions
        )
        images.append(image)
    
    return images

# Ensure the output directory exists
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)
# Example usage for five games
for game_index in range(5):  # Assuming 5 games
    game_images = generate_images_for_game(game_index, templates, json_paths, position_mappings)
    
    # Save each generated image for this game
    for i, img in enumerate(game_images):
        img.save(f"./output/game_{game_index+1}_image_{i+1}.jpg")
