# image_generator.py
import os
import requests
from PIL import Image
from datetime import datetime
from .data_loader import DataLoader
from .template_manager import TemplateManager
from .configAPI import ConfigAPI

class ImageGenerator:
    def __init__(self):
        self.data_loader = DataLoader()
        self.output_folder = ConfigAPI.OUTPUT_FOLDER
        os.makedirs(self.output_folder, exist_ok=True)

        self.template_map = {
            "Win Away Team": os.path.join(ConfigAPI.ASSET_DIR, "first_video", "Match-prediction-Away.jpg"),
            "Win Home Team": os.path.join(ConfigAPI.ASSET_DIR, "first_video", "Match-prediction-Home.jpg"),
            "Win or Draw Home Team": os.path.join(ConfigAPI.ASSET_DIR, "first_video", "Match-prediction-Home-Draw.jpg"),
            "Win or Draw Away Team": os.path.join(ConfigAPI.ASSET_DIR, "first_video", "Match-prediction-Draw-Away.jpg"),
            "Win Home or Away Team": os.path.join(ConfigAPI.ASSET_DIR, "first_video", "Match-prediction-Home-Away.jpg"),
        }

        self.true_icon_path = os.path.join(ConfigAPI.ASSET_DIR,"first_video", "True-Icon.png")
        self.false_icon_path = os.path.join(ConfigAPI.ASSET_DIR, "first_video", "False-Icon.png")

    def download_image(self, url):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                return Image.open(response.raw)
            else:
                print(f"Failed to download image from URL: {url}")
                return None
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

    def select_icon(self, card_value, score):
        home_score, away_score = map(int, score.split('-'))

        if card_value == "Win Home or Away Team":
            return self.false_icon_path if home_score == away_score else self.true_icon_path
        elif card_value == "Win Away Team":
            return self.false_icon_path if away_score <= home_score else self.true_icon_path
        elif card_value == "Win Home Team":
            return self.false_icon_path if home_score <= away_score else self.true_icon_path
        elif card_value == "Win or Draw Home Team":
            return self.false_icon_path if home_score < away_score else self.true_icon_path
        elif card_value == "Win or Draw Away Team":
            return self.false_icon_path if away_score < home_score else self.true_icon_path
        return self.true_icon_path

    def format_timestamp(self, timestamp):
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        date_str = dt.strftime("%Y-%m-%d")  
        day_str = dt.strftime("%A") 
        time_str = dt.strftime("%H:%M") + " (UTC Time)"  
        return date_str, day_str, time_str

    def adjust_y_positions(self, positions, offset=78):
        adjusted_positions = {}
        for key, (x, y) in positions.items():
            adjusted_positions[key] = (x, y + offset)
        return adjusted_positions

# در image_generator.py
    def generate_images(self):
        """
        مدیریت تولید تصاویر برای تمام بازی‌ها.
        """
        data = self.data_loader.load_data()
        if not data:
            print("No data loaded for image generation.")
            return

        for game_id, match_info in enumerate(data, start=1):
            self.generate_images_for_game(game_id, match_info)

    def generate_images_for_game(self, game_id, match_info):
        """
        تولید تصاویر برای یک بازی خاص.
        """
        base_positions = {
            "home_team_name": (595, 475),
            "home_team_logo": (370, 420),
            "away_team_name": (2500, 475),
            "away_team_logo": (3280, 420),
            "date": (1753, 830),
            "day": (1595, 830),
            "time": (2048, 830),
            "Score": (1845, 1187),
            "icon": (1847, 0)
        }

        card_value = match_info.get("Card", "none")
        template_path = self.template_map.get(card_value, ConfigAPI.TEMPLATE_PATH)

        date_str, day_str, time_str = self.format_timestamp(
            match_info.get('startTimestamp', '2024-01-01T00:00:00.000Z')
        )

        # تولید تصویر اول
        output_path_1 = os.path.join(self.output_folder, f"game_{game_id}_prediction1.jpg")
        template_manager_1 = TemplateManager(ConfigAPI.TEMPLATE_PATH)

        adjusted_positions = self.adjust_y_positions(base_positions, offset=78)
        self.add_text_and_logos(template_manager_1, match_info, adjusted_positions, date_str, day_str, time_str)
        template_manager_1.save_image(output_path_1)
        print(f"Saved image 1 for game {game_id} at {output_path_1}")

        # تولید تصویر دوم
        output_path_2 = os.path.join(self.output_folder, f"game_{game_id}_prediction2.jpg")
        template_manager_2 = TemplateManager(template_path)

        self.add_text_and_logos(template_manager_2, match_info, base_positions, date_str, day_str, time_str)

        score = match_info.get("Score", "0-0")
        icon_path = self.select_icon(card_value, score)
        icon_image = Image.open(icon_path).convert("RGBA").resize((200, 200))
        template_manager_2.add_image(icon_image, position=base_positions["icon"], size=(200, 200))

        template_manager_2.save_image(output_path_2)
        print(f"Saved image 2 for game {game_id} at {output_path_2}")


    def add_text_and_logos(self, template_manager, match_info, positions, date_str, day_str, time_str):

        template_manager.add_text(match_info.get('home_team_name', 'Home Team'), position=positions["home_team_name"], font_size=74)  
        template_manager.add_text(match_info.get('away_team_name', 'Away Team'), position=positions["away_team_name"], font_size=74) 
        template_manager.add_text(date_str, position=positions["date"], font_size=28) 
        template_manager.add_text(day_str, position=positions["day"], font_size=28)   
        template_manager.add_text(time_str, position=positions["time"], font_size=32)  
        template_manager.add_text(match_info.get('Score', 'Final Score'), position=positions["Score"], font_size=108)  

        home_logo = match_info.get('home_team_logo', '')
        if home_logo.startswith("http"):
            logo_image = self.download_image(home_logo)
            if logo_image:
                template_manager.add_image(logo_image, position=positions["home_team_logo"], size=(200, 200))
        else:
            template_manager.add_image(home_logo, position=positions["home_team_logo"], size=(200, 200))

        away_logo = match_info.get('away_team_logo', '')
        if away_logo.startswith("http"):
            logo_image = self.download_image(away_logo)
            if logo_image:
                template_manager.add_image(logo_image, position=positions["away_team_logo"], size=(200, 200)) 
        else:
            template_manager.add_image(away_logo, position=positions["away_team_logo"], size=(200, 200))