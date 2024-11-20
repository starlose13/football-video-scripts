from .base_match_pipeline import BaseMatchPipeline
from datetime import datetime
from typing import List, Dict, Any
from config.config import BASE_URL , START_AFTER
from utils.json_saver import JsonSaver

class FetchMatchTime(BaseMatchPipeline):
    def __init__(self, base_url: str):
        super().__init__(base_url)

    def get_match_times(self, start_after: str) -> List[Dict[str, Any]]:

        matches = self.get_matches(start_after)
        
        match_times = []
        for match in matches:
            start_timestamp = match.get("startTimestamp")
            if start_timestamp:
                match_datetime = datetime.fromisoformat(start_timestamp.replace("Z", "+00:00"))
                
                hour = str(int(match_datetime.strftime("%I")))  # Remove leading zero from hour
                minute = match_datetime.minute
                am_pm = match_datetime.strftime("%p").lower()  # AM/PM in lowercase
                
                if minute == 0:
                    formatted_time = f"{hour} {am_pm}"
                else:
                    formatted_time = f"{hour}:{minute} {am_pm}"
                
                time_info = {
                    "id": match.get("id"),
                    "home_team": match["homeInfo"].get("teamName"),
                    "away_team": match["awayInfo"].get("teamName"),
                    "date": match_datetime.date().isoformat(),
                    "day": match_datetime.strftime("%A"),
                    "time": formatted_time
                }
                match_times.append(time_info)
        saver = JsonSaver()
        saver.save_to_json(match_times, "match_times.json")
        return match_times

if __name__ == "__main__":
    fetch_match_time = FetchMatchTime(base_url=BASE_URL)
    match_times = fetch_match_time.get_match_times(start_after=START_AFTER)
    for match_time in match_times:
        print(match_time)
