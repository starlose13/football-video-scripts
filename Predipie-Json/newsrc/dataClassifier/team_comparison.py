from dataFetcher.fetch_odds_ranks import FetchOddsRanks
from dataFetcher.fetch_last_five_matches import FetchLast5Matches
from config.config import BASE_URL, START_AFTER
from .team_status import RankingDifference

class TeamComparison:

    def __init__(self, api_url: str = BASE_URL, start_date: str = START_AFTER):
        self.api_url = api_url
        self.start_date = start_date
        self.fetch_odds = FetchOddsRanks(base_url=self.api_url)
        self.fetch_last5matches = FetchLast5Matches(base_url=self.api_url)
    
    def determine_teams(self, start_date=None):

        date_to_use = start_date or self.start_date
        odds_data = self.fetch_odds.get_odds_ranks(start_after=date_to_use)
        
        teams_info = []
        for match in odds_data:
            match_id = match.get("id")
            home_team_name = match["home_team"]
            away_team_name = match["away_team"]
            home_odds = match["odds"][0].get("homeWin", None)
            away_odds = match["odds"][0].get("awayWin", None)
            home_rank = int(match["home_rank"]) if match["home_rank"] is not None else None
            away_rank = int(match["away_rank"]) if match["away_rank"] is not None else None
            
            if home_odds is not None and away_odds is not None:
                if home_odds < away_odds:
                    a_team_name = home_team_name
                    b_team_name = away_team_name
                    a_odds = home_odds
                    b_odds = away_odds
                    a_rank = home_rank
                    b_rank = away_rank
                else:
                    a_team_name = away_team_name
                    b_team_name = home_team_name
                    a_odds = away_odds
                    b_odds = home_odds
                    a_rank = away_rank
                    b_rank = home_rank

                last5matches_data = self.fetch_last5matches.get_last5matches(start_after=date_to_use)
                
                a_team_last5 = next((team["home_team"]["last_5_matches"] for team in last5matches_data 
                                     if team["home_team"]["team_name"] == a_team_name), [])
                
                b_team_last5 = next((team["away_team"]["last_5_matches"] for team in last5matches_data 
                                     if team["away_team"]["team_name"] == b_team_name), [])

                a_team_points = self.calculate_points(a_team_last5)
                b_team_points = self.calculate_points(b_team_last5)

                if a_rank is not None and b_rank is not None:
                    ranking_difference = RankingDifference(rank_team_a=a_rank, rank_team_b=b_rank)
                    rank_diff_status = ranking_difference.status
                else:
                    rank_diff_status = "Unknown Ranking Difference"

                team_info = {
                    "id": match_id,
                    "Team A": {"name": a_team_name, "odds": a_odds, "last5_points": a_team_points, "rank": a_rank},
                    "Team B": {"name": b_team_name, "odds": b_odds, "last5_points": b_team_points, "rank": b_rank},
                    "Ranking Difference": rank_diff_status,
                    "Home Team Name" : home_team_name
                }
                teams_info.append(team_info)

        return teams_info

    def calculate_points(self, last5matches):

        points = 0
        for match in last5matches:
            if match.lower() == 'w':
                points += 3
            elif match.lower() == 'd':
                points += 1
        return points
