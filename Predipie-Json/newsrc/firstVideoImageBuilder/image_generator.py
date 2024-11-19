# image_generator.py
import os
import requests
from PIL import Image
from .data_loader import DataLoader
from .template_manager import TemplateManager
from .configAPI import ConfigAPI

class ImageGenerator:
    def __init__(self):
        self.data_loader = DataLoader()
        self.template_path = ConfigAPI.TEMPLATE_PATH
        self.output_folder = ConfigAPI.OUTPUT_FOLDER
        os.makedirs(self.output_folder, exist_ok=True)

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

    def generate_images(self):
        data = self.data_loader.load_data()
        if not data:
            print("No data loaded for image generation.")
            return

        positions = {
            "home_team_name": (100, 50),
            "home_team_logo": (100, 100),
            "away_team_name": (500, 50),
            "away_team_logo": (1000, 100),
            "startTimestamp": (300, 250),
            "Score": (300, 300)
        }

        for game_id, match_info in enumerate(data, start=1):
            output_path = os.path.join(self.output_folder, f"game_{game_id}_prediction.jpg")
            template_manager = TemplateManager(self.template_path)

            # اضافه کردن متن‌ها و لوگوها به قالب
            template_manager.add_text(match_info.get('home_team_name', 'Home Team'), position=positions["home_team_name"])
            template_manager.add_text(match_info.get('away_team_name', 'Away Team'), position=positions["away_team_name"])
            template_manager.add_text(match_info.get('startTimestamp', 'Date Not Available'), position=positions["startTimestamp"])
            template_manager.add_text(match_info.get('Score', 'Final Score'), position=positions["Score"], font_size=36)

            # افزودن لوگوی تیم‌ها
            home_logo = match_info.get('home_team_logo', '')
            if home_logo.startswith("http"):
                logo_image = self.download_image(home_logo)
                if logo_image:
                    template_manager.add_image(logo_image, position=positions["home_team_logo"], size=(50, 50))
            else:
                template_manager.add_image(home_logo, position=positions["home_team_logo"], size=(50, 50))

            away_logo = match_info.get('away_team_logo', '')
            if away_logo.startswith("http"):
                logo_image = self.download_image(away_logo)
                if logo_image:
                    template_manager.add_image(logo_image, position=positions["away_team_logo"], size=(50, 50))
            else:
                template_manager.add_image(away_logo, position=positions["away_team_logo"], size=(50, 50))

            template_manager.save_image(output_path)
            print(f"Saved image for game {game_id} at {output_path}")
