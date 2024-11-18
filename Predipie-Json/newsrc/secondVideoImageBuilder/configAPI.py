import os
from dotenv import load_dotenv
from config.config import SHOTSTACK_API_KEY,CREATIFY_API_ID,CREATIFY_API_KEY,START_AFTER


load_dotenv()

class Config:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    output_dir = os.path.join(base_dir, "output_second_video_images")
    os.makedirs(output_dir, exist_ok=True)

    today_date = START_AFTER
    json_base_dir = os.path.join(base_dir, f"{today_date}_json_match_output_folder")

    shotstack_api_key = SHOTSTACK_API_KEY
    creatify_api_id = CREATIFY_API_ID
    creatify_api_key = CREATIFY_API_KEY

    if not shotstack_api_key:
        raise ValueError("SHOTSTACK_API_KEY is missing. Please check your .env file.")
    
    json_paths = {
        "match_introduction": os.path.join(json_base_dir, "team_info.json"),
        "stats": os.path.join(json_base_dir, "match_times.json"),
        "odds": os.path.join(json_base_dir, "odds_ranks_data.json"),
        "recent_matches": os.path.join(json_base_dir, "last5matches_data.json"),
        "card_results": os.path.join(json_base_dir, "match_prediction_result.json"),
    }

    assets_dir = os.path.abspath(os.path.join(base_dir, "assets"))
    templates = [
        os.path.join(assets_dir, "match-introduction.jpg"),
        os.path.join(assets_dir, "stats.jpg"),
        os.path.join(assets_dir, "odds.jpg"),
        os.path.join(assets_dir, "recent-matches.jpg"),
        os.path.join(assets_dir, "away.jpg")
    ]
