import os
import json

class MatchFileSaver:
    """Saves match data into JSON files with customizable options."""
    
    def __init__(self, folder_name='scene2', file_format='json'):
        self.folder_name = folder_name
        self.file_format = file_format.lower()
        os.makedirs(self.folder_name, exist_ok=True)

    def save_to_file(self, match_info, match_index):
        """Saves match data to a file with the specified format."""
        if self.file_format not in ['json', 'txt']:
            raise ValueError("Unsupported file format. Please use 'json' or 'txt'.")

        output_file = os.path.join(self.folder_name, f'match_{match_index}.{self.file_format}')
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                if self.file_format == 'json':
                    json.dump(match_info, f, ensure_ascii=False, indent=4)
                elif self.file_format == 'txt':
                    f.write(str(match_info))
            print(f"Match {match_index} data saved to {output_file}")
        except IOError as e:
            print(f"File save error: {e}")
