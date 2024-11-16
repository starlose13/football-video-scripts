from base_match_pipeline import BaseMatchPipeline
from typing import List, Dict, Any
from config import BASE_URL , START_AFTER
from json_saver import JsonSaver

class FetchLast5Matches(BaseMatchPipeline):
    def __init__(self, base_url: str):
        super().__init__(base_url)

    def count_results(self, matches: List[str]) -> Dict[str, int]:
        """
        Count the number of wins, losses, and draws in the last 5 matches.
        """
        counts = {"wins": 0, "losses": 0, "draws": 0}
        for match in matches:
            if match.lower() == "w":
                counts["wins"] += 1
            elif match.lower() == "l":
                counts["losses"] += 1
            elif match.lower() == "d":
                counts["draws"] += 1
        return counts

    def get_last5matches(self, start_after: str) -> List[Dict[str, Any]]:
        """
        Fetches the last 5 matches information for recent matches.
        """
        # Retrieve match data
        matches = self.get_matches(start_after)
        
        # Extract last 5 matches data for each team
        last5matches_data = []
        for match in matches:
            home_last5 = match["homeInfo"].get("last5matches", [])
            away_last5 = match["awayInfo"].get("last5matches", [])
            
            match_info = {
                "id": match.get("id"),
                "home_team": {
                    "team_name": match["homeInfo"].get("teamName"),
                    "last_5_matches": home_last5,
                    "results_count": self.count_results(home_last5)
                },
                "away_team": {
                    "team_name": match["awayInfo"].get("teamName"),
                    "last_5_matches": away_last5,
                    "results_count": self.count_results(away_last5)
                }
            }
            last5matches_data.append(match_info)
        saver = JsonSaver()
        saver.save_to_json(last5matches_data, "last5matches_data.json")
        return last5matches_data

# Example usage
if __name__ == "__main__":
    fetch_last5matches = FetchLast5Matches(base_url=BASE_URL)
    last5matches_info = fetch_last5matches.get_last5matches(start_after=START_AFTER)
    for match_info in last5matches_info:
        print(match_info)
