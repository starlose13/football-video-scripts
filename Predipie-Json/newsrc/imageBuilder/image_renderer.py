from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import requests

class ImageRenderer:
    def __init__(self):
        self.icon_size = (60, 60)
        self.win_icon = Image.open('../assets/win.png').resize(self.icon_size)
        self.draw_icon = Image.open('../assets/draw.png').resize(self.icon_size)
        self.lose_icon = Image.open('../assets/lose.png').resize(self.icon_size)
    
    @staticmethod
    def load_font(font_path, font_size):
        try:
            return ImageFont.truetype(font_path, font_size)
        except IOError:
            print("Custom font not found, using default font.")
            return ImageFont.load_default()
    
    def draw_text(self, draw, position, text, font, color="white"):
        draw.text(position, text, fill=color, font=font)

    def paste_icon(self, image, icon, position):
        image.paste(icon, position, icon)

    def render_image(self, image, data, positions, font_path="Roboto-Bold.ttf"):
        draw = ImageDraw.Draw(image)
        
        # بارگذاری فونت‌های با اندازه‌های مختلف
        default_font = self.load_font(font_path, 80)
        small_font = self.load_font(font_path, 30)
        medium_font = self.load_font(font_path, 55)
        
        for key, pos in positions.items():
            if key in data:
                print(f"Drawing {key} at {pos} with data: {data[key]}")  # چاپ اطلاعات برای بررسی
                if "logo" in key:
                    logo_url = data[key]
                    try:
                        response = requests.get(logo_url)
                        logo = Image.open(BytesIO(response.content)).resize((200, 200))
                        image.paste(logo, pos, logo)
                    except Exception as e:
                        print(f"Could not load logo from {logo_url}: {e}")
                elif key in ["home_team_last_5", "away_team_last_5"]:
                    # رسم آیکون‌های نتایج بازی‌های اخیر
                    recent_matches = data[key]
                    icon_spacing = 70  # فاصله بین آیکون‌ها
                    x_offset = pos[0]
                    
                    for result in recent_matches:
                        if result == 'W':
                            icon = self.win_icon
                        elif result == 'D':
                            icon = self.draw_icon
                        elif result == 'L':
                            icon = self.lose_icon
                        else:
                            continue
                        
                        # رسم آیکون و بروز رسانی موقعیت x
                        self.paste_icon(image, icon, (x_offset, pos[1]))
                        x_offset += icon_spacing
                else:
                    # انتخاب فونت براساس کلید
                    font = (
                        small_font if key in ["match_date", "match_time", "match_day"]
                        else medium_font if key in ["home_odds", "draw_odds", "away_odds"]
                        else default_font
                    )
                    # رسم متن
                    self.draw_text(draw, pos, str(data[key]), font)

        return image
