# template_manager.py
from PIL import Image, ImageDraw, ImageFont
import os

class TemplateManager:
    def __init__(self, template_path):
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")
        self.image = Image.open(template_path).convert("RGBA")

    def add_text(self, text, position, font_path="arial.ttf", font_size=24, color=(255, 255, 255)):
        draw = ImageDraw.Draw(self.image)
        font = ImageFont.truetype(font_path, font_size)
        draw.text(position, text, font=font, fill=color)

    def add_image(self, logo, position, size):
        if isinstance(logo, str):  # if the logo is a URL or local path
            logo_image = Image.open(logo).convert("RGBA").resize(size)
        elif isinstance(logo, Image.Image):
            logo_image = logo.convert("RGBA").resize(size)
        else:
            print("Invalid logo format")
            return
        self.image.paste(logo_image, position, logo_image)

    def save_image(self, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.image.convert("RGB").save(output_path)
