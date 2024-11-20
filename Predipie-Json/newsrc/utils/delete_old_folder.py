import os
import shutil
from datetime import datetime, timedelta

def delete_old_folders(base_folder="json_match_output_folder"):

    # Calculate the date for two days ago
    two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    
    for folder_name in os.listdir():
        if folder_name.startswith(two_days_ago) and os.path.isdir(folder_name):
            try:
                # Delete the folder
                shutil.rmtree(folder_name)
                print(f"Deleted folder: {folder_name}")
            except Exception as e:
                print(f"Error deleting folder {folder_name}: {e}")

# Example usage
if __name__ == "__main__":
    delete_old_folders()
