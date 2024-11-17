import os
import requests
import json
from config import BASE_URL, START_BEFORE

class ApiResultSaver:
    """A class to fetch and save the final scores from the API."""

    def __init__(self, base_url, start_before):
        self.base_url = base_url
        self.start_before = start_before
        self.output_folder = f"{self.start_before}_json_match_output_folder"

    def fetch_final_scores(self):
        """Fetches final scores from the API."""
        try:
            response = requests.get(f"{self.base_url}/predipie/well-known", params={"startAfter": self.start_before})
            response.raise_for_status()
            data = response.json()
            final_scores = []

            # Extract finalScore from scores
            for match in data.get("results", []):
                final_score = match.get("scores", {}).get("finalScore")
                if final_score is not None:
                    final_scores.append({
                        "match_id": match.get("id"),
                        "home_team": match["homeInfo"].get("teamName"),
                        "away_team": match["awayInfo"].get("teamName"),
                        "finalScore": final_score
                    })

            return final_scores

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from API: {e}")
            return []

    def save_to_json(self, data, filename="final_scores.json"):
        """Saves data to a JSON file in the specified output folder."""
        # Create the output folder if it doesn't exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"Created folder: {self.output_folder}")

        # Define the file path
        file_path = os.path.join(self.output_folder, filename)

        # Save data to JSON
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            print(f"Data successfully saved to {file_path}")

    def run(self):
        """Fetches final scores and saves them to a JSON file."""
        final_scores = self.fetch_final_scores()
        if final_scores:
            self.save_to_json(final_scores)
        else:
            print("No final scores to save.")

# Example usage
if __name__ == "__main__":
    saver = ApiResultSaver(BASE_URL, START_BEFORE)
    saver.run()
