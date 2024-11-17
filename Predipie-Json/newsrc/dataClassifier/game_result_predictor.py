import logging
from .team_comparison import TeamComparison
from .team_classification_points_based import classify_a_points, classify_b_points
from .team_classification_odds_based import classify_a_team, classify_b_team
from utils.json_saver import JsonSaver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
class GameResultPredictor:
    def generate_result(self,a_team, b_team, a_recent_g, b_recent_g, rank_diff):

            # Rows 1-17 (A2 as A team)
            if a_team == "A1":
                return "A win", 1
            # Rows for A2
            elif a_team == "A2" and a_recent_g == "ARecentG1":
                return "A win", 2
            elif a_team == "A2" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG7":
                return "A win", 3
            elif a_team == "A2" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG6":
                return "A win", 4
            elif a_team == "A2" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG5":
                return "A win", 5
            elif a_team == "A2" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG4":
                return "A win", 6
            elif a_team == "A2" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG3":
                return "A win or draw", 7
            elif a_team == "A2" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG2":
                return "A win or draw", 8
            elif a_team == "A2" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG1":
                return "A win or draw", 9
            elif a_team == "A2" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG7":
                return "A win", 10
            elif a_team == "A2" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG6":
                return "A win", 11
            elif a_team == "A2" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG5":
                return "A win", 12
            elif a_team == "A2" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG4":
                return "A win or draw", 13
            elif a_team == "A2" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG3":
                return "A win or draw", 14
            elif a_team == "A2" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG2":
                return "A win or draw", 15
            elif a_team == "A2" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG1":
                return "A win or draw", 16
            elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG7":
                return "A win", 17
            elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "bigDifference":
                return "A win", 18
            elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "mediumDifference":
                return "A win", 19
            elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "smallDifference":
                return "A win or draw", 20
            elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG5" :
                return "A win or draw", 21
            elif a_team == "A2" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG4" and rank_diff == "smallDifference":
                return "A win or draw", 22
            elif a_team == "A2" and a_recent_g == "ARecentG5":
                return "A win or draw", 23
            elif a_team == "A2" and a_recent_g == "ARecentG6":
                return "A win or draw", 24
            elif a_team == "A2" and a_recent_g == "ARecentG7":
                return "A win or draw", 25
            elif a_team == "A3":
                return "A win or draw", 26  
            elif a_team == "A4":
                return "A win or draw", 27
            elif a_team == "A5" and b_team == "B7" and a_recent_g == "ARecentG1":
                return "A win or draw", 28
            elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG1":
                return "A win or draw", 29
            elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG2":
                return "A win or draw", 30
            elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG3":
                return "A win or draw", 31
            elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG7":
                return "A win or draw", 32
            elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6":
                return "A win or draw", 33
            elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG5":
                return "A win or draw", 34
            elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG4" and rank_diff == "bigDifference":
                return "A win or draw", 35
            elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG4" and rank_diff == "mediumDifference":
                return "A or B win", 36
            elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG4" and rank_diff == "smallDifference":
                return "A or B win", 37

            # Rows 38-44 (A5 and A6 with B7)
            elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG5":
                return "A or B win", 38
            elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG6":
                return "A or B win", 39
            elif a_team == "A5" and b_team == "B6" and a_recent_g == "ARecentG7":
                return "A or B win", 40
            elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG7":
                return "A win or draw", 41
            elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG6":
                return "A win or draw", 42
            elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG5":
                return "A win or draw", 43
            elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG4":
                return "A win or draw", 44

            # Rows 45-57 (Rank differences and A7 as A team)
            elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "bigDifference":
                return "A win or draw", 45
            elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "mediumDifference":
                return "A or B win", 46
            elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "smallDifference":
                return "A or B win", 47
            elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG2":
                return "A or B win", 48
            elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG3":
                return "A or B win", 49
            elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG4":
                return "A or B win", 50
            elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG5":
                return "A or B win", 51
            elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG6":
                return "A win or draw", 52
            elif a_team == "A6" and b_team == "B7" and a_recent_g == "ARecentG7":
                return "A or B win", 53
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG7":
                return "A win or draw", 54
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG6":
                return "A win or draw", 55
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG5":
                return "A win or draw", 56
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG4":
                return "A win or draw", 57
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "bigDifference":
                return "A win or draw", 58
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "mediumDifference":
                return "A or B win", 59
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "smallDifference":
                return "A or B win", 60
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG2" and rank_diff == "bigDifference":
                return "A win or draw", 61
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG2" and rank_diff == "mediumDifference":
                return "A or B win", 62
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG2" and rank_diff == "smallDifference":
                return "A or B win", 63
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG1" :
                return "A or B win", 64
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG7" :
                return "A win or draw", 65
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG6" :
                return "A win or draw", 66
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG5" :
                return "A win or draw", 67
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG4" and rank_diff == "bigDifference":
                return "A win or draw", 68
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG4" and rank_diff == "mediumDifference":
                return "A or B win", 69
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG4" and rank_diff == "smallDifference":
                return "A or B win", 70
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG3":
                return "A or B win", 71
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG2":
                return "A or B win", 72
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG1":
                return "A or B win", 73
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG7" :
                return "A win or draw", 74
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG6" :
                return "A win or draw", 75
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG5" and rank_diff == "bigDifference":
                return "A win or draw", 76
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG5" and rank_diff == "mediumDifference":
                return "A or B win", 77
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG5" and rank_diff == "smallDifference":
                return "A or B win", 78
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG4":
                return "A or B win", 79
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG3":
                return "A or B win", 80
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG2" :
                return "A or B win", 81
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG3" and b_recent_g == "BRecentG1" :
                return "A or B win", 82
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG7" :
                return "A win or draw", 83
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "bigDifference":
                return "A win or draw", 84
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "mediumDifference":
                return "A or B win", 85
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG6" and rank_diff == "smallDifference":
                return "A or B win", 86
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG5":
                return "A or B win", 87
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG4" :
                return "A or B win", 88
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG3" :
                return "A or B win", 89
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG2":
                return "A or B win", 90
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG4" and b_recent_g == "BRecentG1":
                return "A or B win", 91
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG7":
                return "A or B win", 92
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG6":
                return "A or B win", 93
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG5":
                return "A or B win", 94
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG4":
                return "A or B win", 95
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG3":
                return "A or B win", 96
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG2" and rank_diff == "bigDifference":
                return "A or B win", 97
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG2" and rank_diff == "mediumDifference":
                return "A or B win", 98
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG2" and rank_diff == "smallDifference":
                return "B win or Draw", 99
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG5" and b_recent_g == "BRecentG1":
                return "B win or Draw", 100
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG7" :
                return "A or B win", 101
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG6":
                return "A or B win", 102
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG5":
                return "A or B win", 103
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG4":
                return "A or B win", 104
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG3":
                return "A or B win", 105
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG2" and rank_diff == "bigDifference":
                return "A or B win", 106
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG2" and rank_diff == "mediumDifference":
                return "B win or draw", 107
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG2" and rank_diff == "smallDifference":
                return "B win or draw", 108
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG6" and b_recent_g == "BRecentG1" :
                return "B win or draw", 109
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG7" :
                return "B win or draw", 110
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG6":
                return "A or B win", 111
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG5":
                return "A or B win", 112
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG4" and rank_diff == "bigDifference":
                return "A or B win", 113
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG4" and rank_diff == "mediumDifference":
                return "B win or draw", 114
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG4" and rank_diff == "smallDifference":
                return "B win or draw", 115
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG3" :
                return "B win or draw", 116
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG2" :
                return "B win or draw", 117
            elif a_team == "A6" and b_team == "B6" and a_recent_g == "ARecentG7" and b_recent_g == "BRecentG1" :
                return "B win or draw", 118
            elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG7":
                return "A win or draw", 119
            elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG6":
                return "A win or draw", 120
            elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG5":
                return "A win or draw", 121
            elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG4" and rank_diff == "bigDifference":
                return "A win or draw", 122
            elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG4" and rank_diff == "mediumDifference":
                return "A win or draw", 123
            elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG4" and rank_diff == "smallDifference":
                return "A or B win", 124
            elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "bigDifference" :
                return "A win or draw", 125
            elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "mediumDifference":
                return "A or B win", 126
            elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG3" and rank_diff == "smallDifference":
                return "A or B win", 127
            elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG2" :
                return "A or B win", 128
            elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG1" and b_recent_g == "BRecentG1" :
                return "A or B win", 129
            elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG1" :
                return "A or B win", 130
            elif a_team == "A7" and b_team == "B7" and a_recent_g == "ARecentG2" and b_recent_g == "BRecentG2" :
                return "A or B win", 131
            elif a_team == "A7" and b_team == "B7"  :
                return "A win or draw", 132
            else :
                logging.warning(f"No result found for the combination: {a_team}, {b_team}, {a_recent_g}, {b_recent_g}, {rank_diff}")
                # Default condition if no match is found
                return "No result found", None


    def predict_game_results(self):
        """
        Predicts game results based on team odds, recent performance, 
        and ranking differences.
        """
        # Create an instance of TeamComparison to get team information
        team_comparator = TeamComparison()
        team_comparison_results = team_comparator.determine_teams()

        results = []
        for team_info in team_comparison_results:
            # Classify each team's odds and recent performance
            a_team_class = classify_a_team(team_info["Team A"]["odds"])
            b_team_class = classify_b_team(team_info["Team B"]["odds"])
            a_recent_group = classify_a_points(team_info["Team A"]["last5_points"])
            b_recent_group = classify_b_points(team_info["Team B"]["last5_points"])
            rank_diff_status = team_info["Ranking Difference"]
            # Generate the game result based on the classifications
            result, rule_number = self.generate_result(a_team_class, b_team_class, a_recent_group, b_recent_group, rank_diff_status)
            
            # Append the result with details for each team
            results.append({
                "Team A": team_info["Team A"]["name"],
                "Team B": team_info["Team B"]["name"],
                "Result": result,
                "Rule Applied": rule_number
            })
            saver = JsonSaver()
            saver.save_to_json(results, "match_prediction_result.json")

        return results

if __name__ == "__main__":
    predictor = GameResultPredictor()
    game_results = predictor.predict_game_results()
    for result in game_results:
        print(result)