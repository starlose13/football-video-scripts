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

    def render_image(self, image, data, positions, image_index, font_path="Roboto-Bold.ttf"):
        draw = ImageDraw.Draw(image)
        
        # تنظیم اندازه فونت‌ها بر اساس تصویر مورد نظر
        if image_index == 4:
            # کوچک‌تر کردن اندازه فونت برای نام تیم‌ها در عکس پنجم
            team_name_font = self.load_font(font_path, 60)
        else:
            team_name_font = self.load_font(font_path, 80)

        stats_font = self.load_font(font_path, 30)
        odds_font = self.load_font(font_path, 55)
        
        for key, pos in positions.items():
            if key in data:
                print(f"Drawing {key} at {pos} with data: {data[key]}")
                
                if "logo" in key:
                    # Fetch and paste team logos with RGBA conversion to avoid transparency mask issues
                    response = requests.get(data[key])
                    logo = Image.open(BytesIO(response.content))

                    # Ensure logo is in RGBA mode
                    if logo.mode != "RGBA":
                        logo = logo.convert("RGBA")
                    
                    logo = logo.resize((200, 200))
                    image.paste(logo, pos, logo)
                
                elif key in ["home_team_last_5", "away_team_last_5"]:
                    # Handle recent matches icons
                    recent_matches = data[key]
                    icon_spacing = 70
                    x_offset = pos[0]
                    
                    for result in recent_matches:
                        # Match W, L, D regardless of case
                        result = result.upper()
                        if result == 'W':
                            icon = self.win_icon
                        elif result == 'D':
                            icon = self.draw_icon
                        elif result == 'L':
                            icon = self.lose_icon
                        else:
                            continue  # Skip if not 'W', 'L', or 'D'
                        
                        # Paste the icon and update x position
                        image.paste(icon, (x_offset, pos[1]), icon)
                        x_offset += icon_spacing
                
                else:
                    # انتخاب فونت بر اساس نوع داده
                    if key in ["match_date", "match_time", "match_day"]:
                        font = stats_font
                    elif key in ["home_odds", "draw_odds", "away_odds"]:
                        font = odds_font
                    elif "team_name" in key:
                        font = team_name_font
                    else:
                        font = self.load_font(font_path, 80)  # فونت پیش‌فرض

                    # رسم متن روی تصویر
                    text_value = str(data[key])
                    self.draw_text(draw, pos, text_value, font)
        
        return image
