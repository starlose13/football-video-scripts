import json
import os
from config.config import START_BEFORE , BASE_URL
from dataFetcher.base_match_pipeline import BaseMatchPipeline 

class ScoreCalculator(BaseMatchPipeline):
    def __init__(self, base_url: str, start_after: str):
        super().__init__(base_url)
        self.start_after = START_BEFORE
        self.file_path = os.path.join(f"{START_BEFORE}_json_match_output_folder", "match_prediction_result.json")

    def calculate_score(self, match_id: str) -> str:
        """
        Calculate the final score for a given match_id.
        """
        return self.get_final_score(match_id=match_id, start_after=self.start_after)

    def update_scores_in_file(self):
        """
        Update scores in the match_prediction_result.json file by adding a score field.
        """
        # Check if the file exists
        if not os.path.exists(self.file_path):
            print(f"Error: File {self.file_path} not found.")
            return

        # Load the current JSON data
        with open(self.file_path, "r") as file:
            data = json.load(file)

        # Update each entry with the score
        for entry in data:
            match_id = entry["id"]
            score = self.calculate_score(match_id)
            entry["Score"] = score
            print(f"Updated score for match_id {match_id}: {score}")

        # Save the updated data back to the file
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)
            print(f"File {self.file_path} updated successfully with scores.")

# Example usage
if __name__ == "__main__":
    base_url = BASE_URL 
    score_calculator = ScoreCalculator(base_url, START_BEFORE)
    score_calculator.update_scores_in_file()
