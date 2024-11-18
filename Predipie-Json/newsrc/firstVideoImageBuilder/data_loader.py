# data_loader.py
import json
import os

class DataLoader:
    def __init__(self, data_folder):
        self.data_folder = data_folder

    def load_json(self, filename):
        file_path = os.path.join(self.data_folder, filename)
        if not os.path.exists(file_path):
            print(f"File {file_path} not found.")
            return {}
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {file_path}")
            return {}
