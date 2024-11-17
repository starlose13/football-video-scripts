from dataFetcher.fetch_odds_ranks import FetchOddsRanks
from dataFetcher.fetch_last_five_matches import FetchLast5Matches
from config.config import BASE_URL, START_AFTER
from .team_status import RankingDifference

class TeamComparison:
    """
    Compares two teams based on their odds, last 5 matches,
    assigns them as Team A and Team B, calculates their recent points,
    and evaluates ranking difference.
    """
    def __init__(self, api_url: str = BASE_URL, start_after: str = START_AFTER):
        self.api_url = api_url
        self.start_after = start_after
        self.fetch_odds = FetchOddsRanks(base_url=self.api_url)
        self.fetch_last5matches = FetchLast5Matches(base_url=self.api_url)
    
    def determine_teams(self):
        """
        Determines Team A and Team B based on odds and returns their information,
        including the points from their last 5 matches and ranking difference.
        """
        # دریافت داده‌های احتمالات بازی‌ها
        odds_data = self.fetch_odds.get_odds_ranks(start_after=self.start_after)
        
        teams_info = []
        for match in odds_data:
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

                # دریافت پنج بازی اخیر هر تیم
                last5matches_data = self.fetch_last5matches.get_last5matches(start_after=self.start_after)
                
                # پیدا کردن پنج بازی اخیر تیم الف
                a_team_last5 = next((team["home_team"]["last_5_matches"] for team in last5matches_data 
                                     if team["home_team"]["team_name"] == a_team_name), [])
                
                # پیدا کردن پنج بازی اخیر تیم ب
                b_team_last5 = next((team["away_team"]["last_5_matches"] for team in last5matches_data 
                                     if team["away_team"]["team_name"] == b_team_name), [])

                # محاسبه امتیاز 5 بازی اخیر
                a_team_points = self.calculate_points(a_team_last5)
                b_team_points = self.calculate_points(b_team_last5)

                # محاسبه اختلاف رتبه تیم‌ها
                if a_rank is not None and b_rank is not None:
                    ranking_difference = RankingDifference(rank_team_a=a_rank, rank_team_b=b_rank)
                    rank_diff_status = ranking_difference.status
                else:
                    rank_diff_status = "Unknown Ranking Difference"

                # ساختاردهی اطلاعات تیم‌ها
                team_info = {
                    "Team A": {"name": a_team_name, "odds": a_odds, "last5_points": a_team_points, "rank": a_rank},
                    "Team B": {"name": b_team_name, "odds": b_odds, "last5_points": b_team_points, "rank": b_rank},
                    "Ranking Difference": rank_diff_status
                }
                teams_info.append(team_info)

        return teams_info

    def calculate_points(self, last5matches):
        """
        Calculates the total points for the last 5 matches.
        win = 3 points, draw = 1 point, lose = 0 points.
        """
        points = 0
        for match in last5matches:
            if match.lower() == 'w':
                points += 3
            elif match.lower() == 'd':
                points += 1
            # lose gives 0 points, so we don't need to add anything for 'l'
        return points

# Example usage
if __name__ == "__main__":
    team_comparator = TeamComparison()
    team_comparison_results = team_comparator.determine_teams()
    
    for result in team_comparison_results:
        print(result)
