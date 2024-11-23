# main.py
import json
import os
from .image_generator import ImageGenerator
from .uploader import ShotstackUploader
from .configAPI import ConfigAPI

class ApplicationManager:
    def __init__(self, api_key):
        self.image_generator = ImageGenerator()
        self.uploader = ShotstackUploader(api_key)
        self.source_ids = {}

    def run(self):
        # 1. Load game IDs and generate images
        data = self.image_generator.data_loader.load_data()
        if not data:
            print("No game data available.")
            return

        for game_id, match_info in enumerate(data, start=1):
            print(f"Generating images for game ID: {game_id}")
            self.image_generator.generate_images_for_game(game_id, match_info)

            # Upload the generated images
            self.upload_images(game_id)

        # Save source IDs
        self.save_source_ids()

    def upload_images(self, game_id):
        for i in range(1, 3):  # دو تصویر برای هر بازی
            file_name = f"game_{game_id}_prediction{i}.jpg"
            image_path = os.path.join(ConfigAPI.OUTPUT_FOLDER, file_name)

            if os.path.exists(image_path):
                source_id = self.uploader.upload_image(image_path, file_name)
                if source_id:
                    print(f"Uploaded {file_name} with Source ID: {source_id}")
                    self.source_ids[file_name] = source_id

    def save_source_ids(self):
        source_ids_path = os.path.join(ConfigAPI.OUTPUT_FOLDER, "uploaded_source_ids.json")
        with open(source_ids_path, "w") as json_file:
            json.dump(self.source_ids, json_file, indent=4)
            print(f"Source IDs saved to {source_ids_path}")


if __name__ == "__main__":
    from config.config import SHOTSTACK_API_KEY

    app_manager = ApplicationManager(SHOTSTACK_API_KEY)
    app_manager.run()
