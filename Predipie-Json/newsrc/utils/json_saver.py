import os
import json
from datetime import datetime

class JsonSaver:
    """A utility class to save data to JSON files in a specific folder."""

    def __init__(self, base_folder="json_match_output_folder"):
        # Get today's date in the format YYYY-MM-DD
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Set the output folder path with today's date as prefix
        self.output_folder = os.path.join(today_date + "_" + base_folder)
        
        # Create the output folder if it does not exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def save_to_json(self, data, filename):
        """Saves the given data to a JSON file inside the output folder."""
        
        # Create the full file path
        filepath = os.path.join(self.output_folder, filename)
        
        # Save the data to JSON
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)
        
        print(f"Data successfully saved to {filepath}")
