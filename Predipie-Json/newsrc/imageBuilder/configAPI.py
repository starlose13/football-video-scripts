import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Config:
    # تنظیمات دایرکتوری اصلی برای فایل‌ها
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # دایرکتوری خروجی برای ذخیره تصاویر تولید شده
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # دایرکتوری تاریخ امروز برای فایل‌های JSON
    today_date = datetime.today().strftime('%Y-%m-%d')
    json_base_dir = os.path.join(base_dir, f"{today_date}_json_match_output_folder")

    # کلیدهای API از فایل .env
    shotstack_api_key = os.getenv("SHOTSTACK_API_KEY")
    creatify_api_id = os.getenv("CREATIFY_API_ID")
    creatify_api_key = os.getenv("CREATIFY_API_KEY")

    if not shotstack_api_key:
        raise ValueError("SHOTSTACK_API_KEY is missing. Please check your .env file.")
    
    # تنظیم مسیرهای JSON با استفاده از json_base_dir
    json_paths = {
        "match_introduction": os.path.join(json_base_dir, "team_info.json"),
        "stats": os.path.join(json_base_dir, "match_times.json"),
        "odds": os.path.join(json_base_dir, "odds_ranks_data.json"),
        "recent_matches": os.path.join(json_base_dir, "last5matches_data.json"),
        "card_results": os.path.join(json_base_dir, "match_prediction_result.json"),
    }

    # مسیر مطلق دایرکتوری assets
    assets_dir = os.path.abspath(os.path.join(base_dir, "assets"))
    templates = [
        os.path.join(assets_dir, "match-introduction.jpg"),
        os.path.join(assets_dir, "stats.jpg"),
        os.path.join(assets_dir, "odds.jpg"),
        os.path.join(assets_dir, "recent-matches.jpg"),
        os.path.join(assets_dir, "away.jpg")
    ]

    # چاپ مسیرها برای بررسی و عیب‌یابی
    print("Output Directory:", output_dir)
    print("JSON Paths:", json_paths)
    print("Template Paths:", templates)

    # بررسی وجود فایل‌های JSON
    for key, path in json_paths.items():
        if not os.path.exists(path):
            print(f"Error: JSON file '{key}' not found at path: {path}")
        else:
            print(f"Found JSON file '{key}' at path: {path}")

    # بررسی وجود فایل‌های قالب (templates)
    for i, template in enumerate(templates):
        if not os.path.exists(template):
            print(f"Error: Template file {i + 1} not found at path: {template}")
        else:
            print(f"Found template file {i + 1} at path: {template}")
