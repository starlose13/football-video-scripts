import os
import json

class JsonSaver:
    """A utility class to save data to JSON files in a specific folder."""

    def __init__(self, output_folder="json_match_output_folder"):
        # Set the output folder path
        self.output_folder = output_folder
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
