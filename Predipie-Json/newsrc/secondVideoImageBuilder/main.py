import json
import os
from .configAPI import ConfigAPI
from .image_generator import ImageGenerator
from .data_loader import DataLoader
from utils.uploader import ShotstackUploader

def main():
    config = ConfigAPI.get_config("second")
    data_loader = DataLoader(config["json_paths"])
    image_generator = ImageGenerator(data_loader=data_loader)

    uploader = ShotstackUploader()
    game_ids = [game["id"] for game in data_loader.team_info_data]
    source_ids = {}

    for game_id in game_ids:
        print(f"Generating images for game ID: {game_id}")
        game_images = image_generator.generate_images_for_game(game_id)
        
        for i, img in enumerate(game_images):
            file_name = f"game_{game_id}_image_{i+1}.jpg"
            image_path = os.path.join(config["output_dir"], file_name)
            img.save(image_path)
            print(f"Saved image: {image_path}")

            # Upload the image
            source_id = uploader.upload_image(image_path, file_name)
            if source_id:
                print(f"Uploaded {file_name} with Source ID: {source_id}")
                source_ids[file_name] = source_id

    # Save all source IDs to a JSON file
    output_json_path = os.path.join(config["output_dir"], "second_video_uploaded_source_ids.json")
    with open(output_json_path, "w") as json_file:
        json.dump(source_ids, json_file, indent=4)
    print(f"Source IDs saved to {output_json_path}")

if __name__ == "__main__":
    main()
