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
        self.output_folder = ConfigAPI.OUTPUT_FOLDER
        os.makedirs(self.output_folder, exist_ok=True)

        # تعیین مسیر تصاویر بر اساس مقادیر `Card`
        self.template_map = {
            "Win Away Team": os.path.join(ConfigAPI.ASSET_DIR, "first_video", "Match-prediction-Away.jpg"),
            "Win Home Team": os.path.join(ConfigAPI.ASSET_DIR, "first_video", "Match-prediction-Home.jpg"),
            "Win or Draw Home Team": os.path.join(ConfigAPI.ASSET_DIR, "first_video", "Match-prediction-Home-Draw.jpg"),
            "Win or Draw Away Team": os.path.join(ConfigAPI.ASSET_DIR, "first_video", "Match-prediction-Draw-Away.jpg"),
            "Win Home or Away Team": os.path.join(ConfigAPI.ASSET_DIR, "first_video", "Match-prediction-Home-Away.jpg"),
        }

        # مسیر آیکون‌های True و False
        self.true_icon_path = os.path.join(ConfigAPI.ASSET_DIR,"first_video", "True-Icon.png")
        self.false_icon_path = os.path.join(ConfigAPI.ASSET_DIR,"first_video", "False-Icon.png")

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
        """
        انتخاب آیکون صحیح بر اساس شرط‌های داده‌شده و نتیجه Score.
        """
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

    def generate_images(self):
        data = self.data_loader.load_data()
        if not data:
            print("No data loaded for image generation.")
            return

        # موقعیت‌های نمایش اطلاعات
        positions = {
            "home_team_name": (100, 50),
            "home_team_logo": (100, 100),
            "away_team_name": (500, 50),
            "away_team_logo": (1000, 100),
            "startTimestamp": (300, 250),
            "Score": (300, 300),
            "icon": (700, 400)  # موقعیت برای نمایش آیکون True یا False
        }

        for game_id, match_info in enumerate(data, start=1):
            # انتخاب قالب بر اساس مقدار `Card`
            card_value = match_info.get("Card", "none")
            template_path = self.template_map.get(card_value, ConfigAPI.TEMPLATE_PATH)

            # تولید اولین عکس (اولین قالب)
            output_path_1 = os.path.join(self.output_folder, f"game_{game_id}_prediction1.jpg")
            template_manager_1 = TemplateManager(ConfigAPI.TEMPLATE_PATH)

            # اضافه کردن اطلاعات به اولین عکس
            self.add_text_and_logos(template_manager_1, match_info, positions)
            template_manager_1.save_image(output_path_1)
            print(f"Saved image 1 for game {game_id} at {output_path_1}")

            # تولید دومین عکس (قالب بر اساس `Card`)
            output_path_2 = os.path.join(self.output_folder, f"game_{game_id}_prediction2.jpg")
            template_manager_2 = TemplateManager(template_path)

            # اضافه کردن اطلاعات به دومین عکس
            self.add_text_and_logos(template_manager_2, match_info, positions)

            # انتخاب آیکون True یا False بر اساس شرط‌ها و اضافه کردن آن به دومین عکس
            score = match_info.get("Score", "0-0")
            icon_path = self.select_icon(card_value, score)
            icon_image = Image.open(icon_path).convert("RGBA").resize((50, 50))
            template_manager_2.add_image(icon_image, position=positions["icon"], size=(50, 50))

            # ذخیره دومین عکس
            template_manager_2.save_image(output_path_2)
            print(f"Saved image 2 for game {game_id} at {output_path_2}")

    def add_text_and_logos(self, template_manager, match_info, positions):
        """
        افزودن متن‌ها و لوگوهای تیم‌ها به تصویر.
        """
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
