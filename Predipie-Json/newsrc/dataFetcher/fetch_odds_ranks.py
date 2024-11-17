from .base_match_pipeline import BaseMatchPipeline
from config.config import BASE_URL, START_AFTER
from utils.json_saver import JsonSaver

from typing import List, Dict, Any

class FetchOddsRanks(BaseMatchPipeline):
    def __init__(self, base_url: str):
        super().__init__(base_url)

    def get_odds_ranks(self, start_after: str) -> List[Dict[str, Any]]:
        """
        Fetches the odds and rank information for recent matches.
        """
        matches = self.get_matches(start_after)
        
        odds_ranks_data = []
        for match in matches:
            odds_ranks_info = {
                "id": match.get("id"),
                "home_team": match["homeInfo"].get("teamName"),
                "away_team": match["awayInfo"].get("teamName"),
                "home_rank": match["homeInfo"].get("rank"),
                "away_rank": match["awayInfo"].get("rank"),
                "odds": match.get("odds", [])
            }
            odds_ranks_data.append(odds_ranks_info)
        
        saver = JsonSaver()
        saver.save_to_json(odds_ranks_data, "odds_ranks_data.json")
        return odds_ranks_data

if __name__ == "__main__":
    fetch_odds_ranks = FetchOddsRanks(base_url=BASE_URL)
    odds_ranks_info = fetch_odds_ranks.get_odds_ranks(start_after=START_AFTER)
    for odds_rank in odds_ranks_info:
        print(odds_rank)
