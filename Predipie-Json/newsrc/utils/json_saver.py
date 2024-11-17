import os
import json
from datetime import datetime

class JsonSaver:
    """A utility class to save data to JSON files in a specific folder."""

    def __init__(self, base_folder="json_match_output_folder"):
        # Get today's date in the format YYYY-MM-DD
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Set the default output folder path with today's date as prefix
        self.default_output_folder = os.path.join(today_date + "_" + base_folder)
        
        # Create the default output folder if it does not exist
        if not os.path.exists(self.default_output_folder):
            os.makedirs(self.default_output_folder)

    def save_to_json(self, data, filename, custom_folder=None):
        """
        Saves the given data to a JSON file inside the specified output folder.
        
        Parameters:
            data (dict): The data to save in JSON format.
            filename (str): The name of the JSON file.
            custom_folder (str, optional): A custom folder path for saving the file.
        """
        # Use the custom folder if provided; otherwise, use the default folder
        output_folder = custom_folder if custom_folder else self.default_output_folder
        
        # Create the custom folder if it does not exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Create the full file path
        filepath = os.path.join(output_folder, filename)
        
        # Save the data to JSON
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)
        
        print(f"Data successfully saved to {filepath}")