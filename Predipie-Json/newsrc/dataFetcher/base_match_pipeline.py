import requests
from typing import List, Dict, Any
from config.config import BASE_URL , START_AFTER,START_BEFORE

class BaseMatchPipeline:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def fetch_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Fetch data from the given endpoint with optional parameters.
        """
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return {}

    def get_recent_matches(self, start_after: str) -> List[Dict[str, Any]]:
        """
        Get recent matches from the API.
        """
        return self.fetch_data("predipie/well-known", params={"startAfter": start_after}).get("results", [])    

    def classify_match_data(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify the raw match data into structured format.
        """
        classified_data = {
            "id": match_data.get("id"),
            "provider_matchId": match_data.get("provider_matchId"),
            "difficulty": match_data.get("difficulty"),
            "provider": match_data.get("provider"),
            "startTimestamp": match_data.get("startTimestamp"),
            "status": match_data.get("status"),
            "state": match_data.get("state"),
            
            "homeInfo": {
                "id": match_data["homeInfo"].get("id"),
                "rank": match_data["homeInfo"].get("rank"),
                "point": match_data["homeInfo"].get("point"),
                "logoUrl": match_data["homeInfo"].get("logoUrl"),
                "website": match_data["homeInfo"].get("website"),
                "teamName": match_data["homeInfo"].get("teamName"),
                "shortName": match_data["homeInfo"].get("shortName"),
                "marketValue": match_data["homeInfo"].get("marketValue"),
                "last5matches": match_data["homeInfo"].get("last5matches"),
                "totalPlayers": match_data["homeInfo"].get("totalPlayers"),
                "foreignPlayers": match_data["homeInfo"].get("foreignPlayers"),
                "foundationTime": match_data["homeInfo"].get("foundationTime"), 
                "nationalPlayers": match_data["homeInfo"].get("nationalPlayers"),
            },
            
            "awayInfo": {
                "id": match_data["awayInfo"].get("id"),
                "rank": match_data["awayInfo"].get("rank"),
                "point": match_data["awayInfo"].get("point"),
                "logoUrl": match_data["awayInfo"].get("logoUrl"),
                "website": match_data["awayInfo"].get("website"),
                "teamName": match_data["awayInfo"].get("teamName"),
                "shortName": match_data["awayInfo"].get("shortName"),
                "marketValue": match_data["awayInfo"].get("marketValue"),
                "last5matches": match_data["awayInfo"].get("last5matches"),
                "totalPlayers": match_data["awayInfo"].get("totalPlayers"),
                "foreignPlayers": match_data["awayInfo"].get("foreignPlayers"),
                "foundationTime": match_data["awayInfo"].get("foundationTime"),
                "nationalPlayers": match_data["awayInfo"].get("nationalPlayers"),
            },
            
            "info": {
                "wind": match_data["info"].get("wind"),
                "weather": match_data["info"].get("weather"),
                "humidity": match_data["info"].get("humidity"),
                "pressure": match_data["info"].get("pressure"),
                "venue": match_data["info"]["venue"].get("name"),
            },
           
            "scores": {
                "home": {
                    "corners": match_data["scores"]["home"].get("corners"),
                    "redCards": match_data["scores"]["home"].get("redCards"),
                    "yellowCards": match_data["scores"]["home"].get("yellowCards"),
                    "halftimeScore": match_data["scores"]["home"].get("halftimeScore"),
                    "overtimeScore": match_data["scores"]["home"].get("overtimeScore"),
                    "regularTimeScore": match_data["scores"]["home"].get("regularTimeScore"),
                    "penaltyShootoutScore": match_data["scores"]["home"].get("penaltyShootoutScore"),
                },
                "away": {
                    "corners": match_data["scores"]["away"].get("corners"),
                    "redCards": match_data["scores"]["away"].get("redCards"),
                    "yellowCards": match_data["scores"]["away"].get("yellowCards"),
                    "halftimeScore": match_data["scores"]["away"].get("halftimeScore"),
                    "overtimeScore": match_data["scores"]["away"].get("overtimeScore"),
                    "regularTimeScore": match_data["scores"]["away"].get("regularTimeScore"),
                    "penaltyShootoutScore": match_data["scores"]["away"].get("penaltyShootoutScore"),
                },
                "finalScore": match_data["scores"].get("finalScore"),
            },
            
            # "headToHead": match_data.get("headToHead", []),
            
            "odds": [
                {
                    "draw": odd.get("draw"),
                    "score": odd.get("score"),
                    "awayWin": odd.get("awayWin"),
                    "homeWin": odd.get("homeWin"),
                    "isSealed": odd.get("isSealed"),
                    "matchTime": odd.get("matchTime"),
                    "changeTime": odd.get("changeTime"),
                    "matchStatus": odd.get("matchStatus"),
                }
                for odd in match_data.get("odds", [])
            ],
            
            "tier": [
                {
                    "tier": tier_info.get("tier"),
                    "zone": tier_info.get("zone"),
                }
                for tier_info in match_data.get("tier", [])
            ],
            
            "wellKnown": match_data.get("wellKnown"),
            "createdAt": match_data.get("createdAt"),
            "updatedAt": match_data.get("updatedAt"),
            "deletedAt": match_data.get("deletedAt"),
        }

        return classified_data
    
    def get_match_info(self, match_id: str) -> Dict[str, str]:
        """
        Retrieve the logos, names of the home and away teams, and match start time for a given match_id.
        """
        matches = self.get_matches(start_after=START_AFTER)
        for match in matches:
            if match.get("id") == match_id:
                return {
                    "home_team_name": match["homeInfo"]["teamName"],
                    "home_team_logo": match["homeInfo"]["logoUrl"],
                    "away_team_name": match["awayInfo"]["teamName"],
                    "away_team_logo": match["awayInfo"]["logoUrl"],
                    "startTimestamp": match["startTimestamp"]
                }
        return {
            "home_team_name": "N/A",
            "home_team_logo": "N/A",
            "away_team_name": "N/A",
            "away_team_logo": "N/A",
            "startTimestamp": "N/A"
        }

    def get_matches(self, start_after: str) -> List[Dict[str, Any]]:
        """
        Get and classify matches data.
        """
        raw_matches = self.get_recent_matches(start_after)
        return [self.classify_match_data(match) for match in raw_matches]
    
    def get_final_score(self, match_id: str, start_after: str) -> str:
        """
        Retrieve the final score for a specific match by match_id.
        """
        start_after = START_BEFORE
        matches = self.get_matches(start_after)
        for match in matches:
            if match.get("id") == match_id:
                return match.get("scores", {}).get("finalScore", "N/A")
        return "N/A"

    
if __name__ == "__main__":
    base_pipeline = BaseMatchPipeline(base_url=BASE_URL)
    matches = base_pipeline.get_matches(start_after=START_AFTER)
    for match in matches:
        print(match)
