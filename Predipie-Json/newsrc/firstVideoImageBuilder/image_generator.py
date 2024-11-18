# image_generator.py
import os
import requests
from PIL import Image
from .data_loader import DataLoader
from .template_manager import TemplateManager

class ImageGenerator:
    def __init__(self, data_folder, template_path, output_folder):
        self.data_loader = DataLoader(data_folder)
        self.template_path = template_path
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

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
        # بارگذاری داده‌های مورد نیاز از فایل‌های JSON
        team_info_list = self.data_loader.load_json("team_info.json")
        match_prediction_list = self.data_loader.load_json("match_prediction_result.json")

        # بررسی می‌کنیم که هر دو لیست دارای اطلاعات باشند و طول آن‌ها برابر باشد
        if not team_info_list or not match_prediction_list or len(team_info_list) != len(match_prediction_list):
            print("Error: Missing required JSON data or mismatched list lengths.")
            return

        # پردازش هر بازی بر اساس داده‌های هر دو لیست
        for game_id, (team_info, match_prediction) in enumerate(zip(team_info_list, match_prediction_list), start=1):
            output_path = os.path.join(self.output_folder, f"game_{game_id}_prediction.jpg")
            template_manager = TemplateManager(self.template_path)

            # اضافه کردن نام و لوگوی تیم‌ها
            template_manager.add_text(team_info.get('home_team_name', 'Home Team'), position=(100, 50))
            home_logo = team_info.get('home_team_logo', '')
            if home_logo.startswith("http"):
                logo_image = self.download_image(home_logo)
                if logo_image:
                    template_manager.add_image(logo_image, position=(100, 100), size=(50, 50))
            else:
                template_manager.add_image(home_logo, position=(100, 100), size=(50, 50))

            template_manager.add_text(team_info.get('away_team_name', 'Away Team'), position=(500, 50))
            away_logo = team_info.get('away_team_logo', '')
            if away_logo.startswith("http"):
                logo_image = self.download_image(away_logo)
                if logo_image:
                    template_manager.add_image(logo_image, position=(1000, 966), size=(50, 50))
            else:
                template_manager.add_image(away_logo, position=(1000, 966), size=(50, 50))

            # اضافه کردن پیش‌بینی کارت
            template_manager.add_text(match_prediction.get('Card', 'Prediction Card'), position=(300, 300), font_size=36)

            # ذخیره تصویر
            template_manager.save_image(output_path)
            print(f"Saved image for game {game_id} at {output_path}")
