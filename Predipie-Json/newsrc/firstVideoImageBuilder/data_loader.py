import json
import os
from .configAPI import ConfigAPI

class DataLoader:
    def __init__(self):
        self.file_path = ConfigAPI.JSON_FILE

    def load_data(self):
        if not os.path.exists(self.file_path):
            print(f"Error: File {self.file_path} not found.")
            return []
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {self.file_path}")
            return []