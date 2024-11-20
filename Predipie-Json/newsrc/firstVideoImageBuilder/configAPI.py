import os
from config.config import START_BEFORE
class ConfigAPI:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ASSET_DIR = os.path.abspath(os.path.join(BASE_DIR, "assets"))

    DATA_FOLDER = os.path.join(BASE_DIR,f"{START_BEFORE}_json_match_output_folder")
    JSON_FILE = os.path.join(DATA_FOLDER, "match_prediction_result.json")
    
    TEMPLATE_PATH = os.path.join(ASSET_DIR, "first_video", "Match-result.jpg")
    OUTPUT_FOLDER = os.path.join(DATA_FOLDER, "first_video_images")
