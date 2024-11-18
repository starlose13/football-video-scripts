import os
from .configAPI import Config
from .image_generator import ImageGenerator
from .data_loader import DataLoader

def main():
    # اطمینان از اینکه پوشه خروجی وجود دارد
    os.makedirs(Config.output_dir, exist_ok=True)
    
    # ایجاد نمونه از کلاس‌های مورد نیاز
    image_generator = ImageGenerator()
    data_loader = DataLoader(Config.json_paths)
    
    # بارگذاری لیست بازی‌ها از فایل JSON برای دریافت id بازی‌ها
    game_ids = [game["id"] for game in data_loader.team_info_data]  # استخراج id هر بازی
    print(f"Game IDs loaded: {game_ids}")

    # پردازش و ایجاد تصاویر برای هر بازی
    for game_id in game_ids:
        print(f"Generating images for game ID: {game_id}")
        game_images = image_generator.generate_images_for_game(game_id)
        
        # ذخیره هر تصویر در پوشه خروجی
        for i, img in enumerate(game_images):
            file_name = f"game_{game_id}_image_{i+1}.jpg"
            image_path = os.path.join(Config.output_dir, file_name)
            img.save(image_path)
            print(f"Saved image: {image_path}")

if __name__ == "__main__":
    main()
