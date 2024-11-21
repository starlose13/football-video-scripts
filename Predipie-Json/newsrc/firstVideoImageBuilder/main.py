import json
from .image_generator import ImageGenerator
from utils.uploader import ShotstackUploader
from .configAPI import ConfigAPI
import os
def main():
    config = ConfigAPI.get_config("first")
    image_generator = ImageGenerator(template_path=config["template_path"])
    image_generator.generate_images()

    uploader = ShotstackUploader()
    uploader.upload_images_in_folder(
        config["output_dir"], 
        os.path.join(config["output_dir"], "first_video_uploaded_source_ids.json")
    )

    uploaded_source_ids_path = os.path.join(config["output_dir"], "first_video_uploaded_source_ids.json")
    if os.path.exists(uploaded_source_ids_path):
        with open(uploaded_source_ids_path, "r") as f:
            source_ids = json.load(f)
            print(f"Uploaded Source IDs: {source_ids}")
    else:
        print("No source IDs were generated.")


if __name__ == "__main__":
    main()
