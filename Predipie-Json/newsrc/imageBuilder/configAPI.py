import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Config:
    # تنظیمات دایرکتوری خروجی
    output_dir = os.path.abspath("C:/Users/Mehrdad/tempPredi/football-video-scripts/Predipie-Json/newsrc/output")
    os.makedirs(output_dir, exist_ok=True)
    
    # کلیدهای API از فایل .env
    shotstack_api_key = os.getenv("SHOTSTACK_API_KEY")
    creatify_api_id = os.getenv("CREATIFY_API_ID")
    creatify_api_key = os.getenv("CREATIFY_API_KEY")
    
    if not shotstack_api_key:
        raise ValueError("SHOTSTACK_API_KEY is missing. Please check your .env file.")
    
    # مسیرهای مستقیم برای فایل‌های JSON
    json_paths = {
        "match_introduction": r"C:\Users\Mehrdad\tempPredi\football-video-scripts\Predipie-Json\newsrc\2024-11-18_json_match_output_folder\team_info.json",
        "stats": r"C:\Users\Mehrdad\tempPredi\football-video-scripts\Predipie-Json\newsrc\2024-11-18_json_match_output_folder\match_times.json",
        "odds": r"C:\Users\Mehrdad\tempPredi\football-video-scripts\Predipie-Json\newsrc\2024-11-18_json_match_output_folder\odds_ranks_data.json",
        "recent_matches": r"C:\Users\Mehrdad\tempPredi\football-video-scripts\Predipie-Json\newsrc\2024-11-18_json_match_output_folder\last5matches_data.json",
        "card_results": r"C:\Users\Mehrdad\tempPredi\football-video-scripts\Predipie-Json\newsrc\2024-11-18_json_match_output_folder\match_prediction_result.json"
    }

    # مسیرهای مستقیم برای فایل‌های قالب (templates)
    templates = [
        r'C:\Users\Mehrdad\tempPredi\football-video-scripts\Predipie-Json\newsrc\assets\match-introduction.jpg',
        r'C:\Users\Mehrdad\tempPredi\football-video-scripts\Predipie-Json\newsrc\assets\stats.jpg',
        r'C:\Users\Mehrdad\tempPredi\football-video-scripts\Predipie-Json\newsrc\assets\odds.jpg',
        r'C:\Users\Mehrdad\tempPredi\football-video-scripts\Predipie-Json\newsrc\assets\recent-matches.jpg',
        r'C:\Users\Mehrdad\tempPredi\football-video-scripts\Predipie-Json\newsrc\assets\away.jpg'
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
            print(f"Error: Template file {i+1} not found at path: {template}")
        else:
            print(f"Found template file {i+1} at path: {template}")
