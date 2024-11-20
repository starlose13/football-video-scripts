class TeamAStatus:

    def __init__(self, status: int):
        if 1 <= status <= 7:
            self.status = status
        else:
            raise ValueError("Status must be between 1 and 7 for Team A.")

    def __str__(self):
        return f"Team A Status: Level {self.status}"


class TeamBStatus:

    def __init__(self, status: int):
        if 1 <= status <= 7:
            self.status = status
        else:
            raise ValueError("Status must be between 1 and 7 for Team B.")

    def __str__(self):
        return f"Team B Status: Level {self.status}"


class RankingDifference:
    """
    Represents the ranking difference between two teams with three levels:
    - bigDifference
    - mediumDifference
    - smallDifference
    """
    def __init__(self, rank_team_a: int, rank_team_b: int):
        self.rank_team_a = rank_team_a
        self.rank_team_b = rank_team_b
        self.difference = abs(rank_team_a - rank_team_b)
        self.status = self.evaluate_difference()

    def evaluate_difference(self) -> str:
        """
        Evaluates the ranking difference and returns a description.
        """
        if self.difference > 8:
            return "bigDifference"
        elif 4 < self.difference <= 7:
            return "mediumDifference"
        else:
            return "smallDifference"

    def __str__(self):
        return f"Ranking Difference: {self.status} (Difference: {self.difference})"
