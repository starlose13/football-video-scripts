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
        json_data_match_introduction = self.data_loader.get_game_data(game_id).get("match_introduction", {})
        json_data_stats = self.data_loader.get_game_data(game_id).get("stats", {})
        json_data_odds = self.data_loader.get_game_data(game_id).get("odds", {})
        json_data_recent_matches = self.data_loader.get_game_data(game_id).get("recent_matches", {})
        json_data_card = self.data_loader.get_game_data(game_id).get("card", "")

        # داده‌ها برای هر تصویر به ترتیب
        image_specific_data = [
            json_data_match_introduction,
            json_data_stats,
            json_data_odds,
            json_data_recent_matches,
            json_data_card
        ]

        # تعریف متغیرهای انباشته برای نگهداری داده‌ها و موقعیت‌های قبلی
        accumulated_data = {}
        accumulated_positions = {}

        # تولید هر تصویر به ترتیب و با داده‌های انباشته
        for i, template_path in enumerate(Config.templates):
            try:
                template_image = Image.open(template_path)
                print(f"Opened template: {template_path} for image index {i}")
            except FileNotFoundError:
                print(f"Error: Template file not found at {template_path}")
                continue

            # دریافت موقعیت‌های مخصوص برای هر تصویر با استفاده از TemplateManager
            positions = TemplateManager.get_adjusted_positions(i)
            print(f"Positions for image index {i}: {positions}")

            # دریافت داده‌های مربوط به هر تصویر و ترکیب آن‌ها با داده‌های انباشته
            current_image_data = self._get_data_for_image(image_specific_data[i], i)
            print(f"Image Data for template index {i}: {current_image_data}")

            # ادغام داده‌های فعلی با داده‌های انباشته‌شده
            combined_data = {**accumulated_data, **current_image_data}
            combined_positions = {**accumulated_positions, **positions}

            # چاپ داده‌ها و موقعیت‌های ترکیبی برای بررسی
            print(f"Combined Data for image index {i}: {combined_data}")
            print(f"Combined Positions for image index {i}: {combined_positions}")

            # رندر تصویر با استفاده از ImageRenderer
            rendered_image = self.renderer.render_image(
            template_image, combined_data, combined_positions
            )
            images.append(rendered_image)

            # به‌روزرسانی accumulated_data و accumulated_positions برای استفاده در تصویر بعدی
            accumulated_data = combined_data
            accumulated_positions = combined_positions

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
            return {
                "match_date": json_data.get("date", ""),
                "match_time": json_data.get("time", ""),
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
            return {
                "card": json_data  # به طور مستقیم نتیجه را برای تصویر آخر دریافت می‌کنیم
            }
        return {}
