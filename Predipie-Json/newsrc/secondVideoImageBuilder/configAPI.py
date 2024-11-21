import os
from dotenv import load_dotenv
from config.config import START_AFTER,BASE_DIR


load_dotenv()

class Config:
    json_base_dir = os.path.join(BASE_DIR, f"{START_AFTER}_json_match_output_folder")
    output_dir = os.path.join(json_base_dir, "second_video_images")
    os.makedirs(output_dir, exist_ok=True)
    
    json_paths = {
        "match_introduction": os.path.join(json_base_dir, "team_info.json"),
        "stats": os.path.join(json_base_dir, "match_times.json"),
        "odds": os.path.join(json_base_dir, "odds_ranks_data.json"),
        "recent_matches": os.path.join(json_base_dir, "last5matches_data.json"),
        "card_results": os.path.join(json_base_dir, "match_prediction_result.json"),
    }

    assets_dir = os.path.abspath(os.path.join(BASE_DIR, "assets"))
    templates = [
        os.path.join(assets_dir, "match-introduction.jpg"),
        os.path.join(assets_dir, "stats.jpg"),
        os.path.join(assets_dir, "odds.jpg"),
        os.path.join(assets_dir, "recent-matches.jpg"),
        os.path.join(assets_dir, "away.jpg")
    ]
