# main.py
import os
from .image_generator import ImageGenerator
from config.config import START_BEFORE

def main():
    data_folder = f"{START_BEFORE}_json_match_output_folder"
    template_path = os.path.join("assets", "first_video", "1st_match-prediction.jpg")
    output_folder = os.path.join(data_folder, "images")

    image_generator = ImageGenerator(data_folder, template_path, output_folder)
    image_generator.generate_images()

if __name__ == "__main__":
    main()
