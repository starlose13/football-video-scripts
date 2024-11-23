from .configAPI import Config
from .data_loader import DataLoader
from .template_manager import TemplateManager
from .image_renderer import ImageRenderer
from PIL import Image
import os

class ImageGenerator:
    def __init__(self):
        self.data_loader = DataLoader(Config.json_paths)
        self.renderer = ImageRenderer()

    def generate_images_for_game(self, game_id):
        images = []

        game_data = self.data_loader.get_game_data(game_id)
        
        json_data_match_introduction = game_data.get("match_introduction", {})
        json_data_stats = game_data.get("stats", {})
        json_data_odds = game_data.get("odds", {})
        json_data_recent_matches = game_data.get("recent_matches", {})
        json_data_card = game_data.get("card", {})

        image_specific_data = [
            json_data_match_introduction,
            json_data_stats,
            json_data_odds,
            json_data_recent_matches,
            json_data_card
        ]

        previous_positions = {}
        previous_data = {}

        for i, template_path in enumerate(Config.templates):
            if i == 4:
                card_result = json_data_card if isinstance(json_data_card, str) else json_data_card.get("Card", "none")
                print(f"Card result for game ID {game_id}: {card_result}")

                template_path = self._get_template_path_by_card(card_result)
                print(f"Template selected for Card '{card_result}': {template_path}")

            try:
                template_image = Image.open(template_path)
                print(f"Opened template: {template_path} for image index {i}")
            except FileNotFoundError:
                print(f"Error: Template file not found at {template_path}")
                continue

            positions = TemplateManager.get_adjusted_positions(i)
            print(f"Positions for image index {i}: {positions}")

            image_data = self._get_data_for_image(image_specific_data[i], i)
            print(f"Image Data for template index {i}: {image_data}")

            combined_data = {**previous_data, **image_data}
            combined_positions = {**previous_positions, **positions}

            rendered_image = self.renderer.render_image(
                template_image, combined_data, combined_positions, i
            )
            images.append(rendered_image)

            previous_data = combined_data
            previous_positions = combined_positions

        return images

    def _get_data_for_image(self, json_data, image_index):

        if image_index == 0:  
            return {
                "home_team_name": json_data.get("home_team_name", ""),
                "home_team_logo": json_data.get("home_team_logo", ""),
                "away_team_name": json_data.get("away_team_name", ""),
                "away_team_logo": json_data.get("away_team_logo", "")
            }
        elif image_index == 1:  
            match_time = json_data.get("time", "")
            return {
                "match_date": json_data.get("date", ""),
                "match_time": f"{match_time} (UTC Time)",
                "match_day": json_data.get("day", "")
            }
        elif image_index == 2:  
            odds_data = json_data.get("odds", [{}])[0] 
            return {
                "home_odds": odds_data.get("homeWin", ""),
                "draw_odds": odds_data.get("draw", ""),
                "away_odds": odds_data.get("awayWin", "")
            }
        elif image_index == 3:  
            return {
                "home_team_last_5": json_data.get("home_team", {}).get("last_5_matches", []),
                "away_team_last_5": json_data.get("away_team", {}).get("last_5_matches", [])
            }
        elif image_index == 4:  
            return {"Card": json_data} if isinstance(json_data, str) else {}
        return {}

    def _get_template_path_by_card(self, card_result):

        card_templates = {
            "Win Home Team": os.path.join(Config.assets_dir, 'home.jpg'),
            "Win or Draw Home Team": os.path.join(Config.assets_dir, 'home-draw.jpg'),
            "Win or Draw Away Team": os.path.join(Config.assets_dir, 'draw-away.jpg'),
            "Win Away Team": os.path.join(Config.assets_dir, 'away.jpg'),
            "Win Home or Away Team": os.path.join(Config.assets_dir, 'home-away.jpg')
        }
        return card_templates.get(card_result.strip(), Config.templates[4])  