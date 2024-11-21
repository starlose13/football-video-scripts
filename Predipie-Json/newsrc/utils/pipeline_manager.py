import os
import json
from utils.uploader import ShotstackUploader

class PipelineManager:
    def __init__(self, config, image_generator, data_loader=None):
        self.config = config
        self.image_generator = image_generator
        self.data_loader = data_loader
        self.uploader = ShotstackUploader()

    def generate_and_upload_images(self):
        if self.data_loader:
            game_ids = [game["id"] for game in self.data_loader.team_info_data]
            print(f"Game IDs loaded: {game_ids}")
        else:
            game_ids = [None]  # For single-template videos (e.g., "first")

        source_ids = {}

        for game_id in game_ids:
            print(f"Generating images for game ID: {game_id}")
            game_images = self.image_generator.generate_images_for_game(game_id) if game_id else self.image_generator.generate_images()

            for i, img in enumerate(game_images):
                file_name = f"game_{game_id}_image_{i+1}.jpg" if game_id else f"image_{i+1}.jpg"
                image_path = os.path.join(self.config["output_dir"], file_name)
                img.save(image_path)
                print(f"Saved image: {image_path}")

                # Upload the image
                source_id = self.uploader.upload_image(image_path, file_name)
                if source_id:
                    print(f"Uploaded {file_name} with Source ID: {source_id}")
                    source_ids[file_name] = source_id

        # Save source IDs to a JSON file
        source_ids_path = os.path.join(self.config["output_dir"], "uploaded_source_ids.json")
        with open(source_ids_path, "w") as json_file:
            json.dump(source_ids, json_file, indent=4)
            print(f"Source IDs saved to {source_ids_path}")
