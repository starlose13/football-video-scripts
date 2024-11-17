from .base_match_pipeline import BaseMatchPipeline
from typing import List, Dict, Any
from config.config import BASE_URL , START_AFTER
from utils.json_saver import JsonSaver

class FetchTeamInfo(BaseMatchPipeline):
    def __init__(self, base_url: str):
        super().__init__(base_url)

    def get_team_info(self, start_after: str) -> List[Dict[str, Any]]:
        """
        Fetches the team names and logos for recent matches.
        """
        # Retrieve match data
        matches = self.get_matches(start_after)
        
        # Extract team information (names and logos)
        team_info_list = []
        for match in matches:
            team_info = {
                "id": match.get("id"),
                "home_team_name": match["homeInfo"].get("teamName"),
                "home_team_logo": match["homeInfo"].get("logoUrl"),
                "away_team_name": match["awayInfo"].get("teamName"),
                "away_team_logo": match["awayInfo"].get("logoUrl"),
            }
            team_info_list.append(team_info)
        saver = JsonSaver()
        saver.save_to_json(team_info_list, "team_info.json")
        return team_info_list

# Example usage
if __name__ == "__main__":
    fetch_team_info = FetchTeamInfo(base_url=BASE_URL)
    team_info = fetch_team_info.get_team_info(start_after=START_AFTER)
    for info in team_info:
        print(info)
