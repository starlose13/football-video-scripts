import os
from dotenv import load_dotenv
from config.config import BASE_DIR, START_BEFORE, START_AFTER, ASSET_DIR,OUTPUT_FOLDER

load_dotenv()

class ConfigAPI:
    @staticmethod
    def get_config(video_type: str):
        if video_type == "first":
            json_base_dir = os.path.join(BASE_DIR, f"{START_BEFORE}_json_match_output_folder")
            output_dir = os.path.join(json_base_dir, "first_video_images")
            json_file = os.path.join(json_base_dir, "match_prediction_result.json")
            template_path = os.path.join(ASSET_DIR, "first_video", "Match-result.jpg")
        elif video_type == "second":
            json_base_dir = os.path.join(BASE_DIR, f"{START_AFTER}_json_match_output_folder")
            output_dir = os.path.join(json_base_dir, "second_video_images")
            json_file = os.path.join(json_base_dir, "match_prediction_result.json")
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
            template_path = None
        else:
            raise ValueError(f"Unknown video type: {video_type}")

        os.makedirs(output_dir, exist_ok=True)

        return {
            "json_base_dir": json_base_dir,
            "output_dir": output_dir,
            "json_file": json_file,
            "template_path": template_path,
            "json_paths": json_paths if video_type == "second" else None,
        }
