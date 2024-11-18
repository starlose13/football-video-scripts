from .configAPI import Config
from .data_loader import DataLoader
from .template_manager import TemplateManager
from .image_renderer import ImageRenderer
from PIL import Image

class ImageGenerator:
    def __init__(self):
        self.data_loader = DataLoader(Config.json_paths)
        self.renderer = ImageRenderer()
            
    def generate_images_for_game(self, game_id):
        images = []
        
        # دریافت داده‌های مربوط به بازی برای هر JSON
        game_data = self.data_loader.get_game_data(game_id)
        
        json_data_match_introduction = game_data.get("match_introduction", {})
        json_data_stats = game_data.get("stats", {})
        json_data_odds = game_data.get("odds", {})
        json_data_recent_matches = game_data.get("recent_matches", {})
        json_data_card = game_data.get("card", "")

        # داده‌ها برای هر تصویر
        image_specific_data = [
            json_data_match_introduction,
            json_data_stats,
            json_data_odds,
            json_data_recent_matches,
            json_data_card
        ]

        # تعریف لیست برای ذخیره موقعیت‌ها و داده‌های قبلی
        previous_positions = {}
        previous_data = {}

        # تولید هر تصویر به ترتیب و با اطلاعات قبلی
        for i, template_path in enumerate(Config.templates):
            if i == 4:
                # بررسی مقدار فیلد Card و انتخاب تصویر مناسب برای عکس پنجم
                card_result = image_specific_data[i].strip() if isinstance(image_specific_data[i], str) else "none"
                print(f"Card result for game ID {game_id}: {card_result}")  # چاپ مقدار Card برای بررسی
                
                # استفاده از .strip() برای حذف فضاهای اضافی و مقایسه حساس به حروف کوچک و بزرگ
                if card_result == "Win Home Team":
                    template_path = '../assets/home.jpg'
                elif card_result == "Win or Draw Home Team":
                    template_path = '../assets/home-draw.jpg'
                elif card_result == "Win or Draw Away Team":
                    template_path = '../assets/away-draw.jpg'
                elif card_result == "Win Away Team":
                    template_path = '../assets/away.jpg'
                elif card_result == "Win Home or Away Team":
                    template_path = '../assets/home-away.jpg'
                else:
                    print(f"No matching card result for game ID {game_id}. Using default template.")

            try:
                template_image = Image.open(template_path)
                print(f"Opened template: {template_path} for image index {i}")
            except FileNotFoundError:
                print(f"Error: Template file not found at {template_path}")
                continue

            # دریافت موقعیت‌ها برای هر تصویر با استفاده از TemplateManager
            positions = TemplateManager.get_adjusted_positions(i)
            print(f"Positions for image index {i}: {positions}")

            # دریافت داده‌های مربوط به هر تصویر و ترکیب آن‌ها با داده‌های قبلی
            image_data = self._get_data_for_image(image_specific_data[i], i)
            print(f"Image Data for template index {i}: {image_data}")

            # ادغام داده‌های فعلی با داده‌های قبلی
            combined_data = {**previous_data, **image_data}
            combined_positions = {**previous_positions, **positions}

            # رندر تصویر با استفاده از ImageRenderer
            rendered_image = self.renderer.render_image(
                template_image, combined_data, combined_positions, i
            )
            images.append(rendered_image)

            # به‌روزرسانی previous_data و previous_positions برای تصویر بعدی
            previous_data = combined_data
            previous_positions = combined_positions

        return images

    def _get_data_for_image(self, json_data, image_index):
        """
        استخراج داده‌های خاص برای هر تصویر بر اساس اندیس تصویر.
        """
        if image_index == 0:  # برای match-introduction.jpg
            return {
                "home_team_name": json_data.get("home_team_name", ""),
                "home_team_logo": json_data.get("home_team_logo", ""),
                "away_team_name": json_data.get("away_team_name", ""),
                "away_team_logo": json_data.get("away_team_logo", "")
            }
        elif image_index == 1:  # برای stats.jpg
            match_time = json_data.get("time", "")
            return {
                "match_date": json_data.get("date", ""),
                "match_time": f"{match_time} (UTC Time)",
                "match_day": json_data.get("day", "")
            }
        elif image_index == 2:  # برای odds.jpg
            odds_data = json_data.get("odds", [{}])[0]  # دسترسی به اولین عنصر در لیست odds
            return {
                "home_odds": odds_data.get("homeWin", ""),
                "draw_odds": odds_data.get("draw", ""),
                "away_odds": odds_data.get("awayWin", "")
            }
        elif image_index == 3:  # برای recent-matches.jpg
            return {
                "home_team_last_5": json_data.get("home_team", {}).get("last_5_matches", []),
                "away_team_last_5": json_data.get("away_team", {}).get("last_5_matches", [])
            }
        elif image_index == 4:  # برای نتیجه کارت (match_prediction_result)
            return {"Card": json_data} if isinstance(json_data, str) else {}
        return {}
