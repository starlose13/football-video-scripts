import os
import json
from datetime import datetime
from config.config import START_BEFORE,START_AFTER

class JsonSaver:

    def __init__(self, base_folder="json_match_output_folder"):
        today_date = START_AFTER
        
        self.default_output_folder = os.path.join(f"{today_date}_{base_folder}")
        
        if not os.path.exists(self.default_output_folder):
            os.makedirs(self.default_output_folder)

    def save_to_json(self, data, filename, custom_folder=None):

        output_folder = custom_folder if custom_folder else self.default_output_folder
        
        # Create the output folder if it does not exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        filepath = os.path.join(output_folder, filename)
        
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)
        
        print(f"Data successfully saved to {filepath}")
