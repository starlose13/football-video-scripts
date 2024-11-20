import logging
from .team_status import TeamAStatus, TeamBStatus

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def classify_a_team(a_odds):

    if not isinstance(a_odds, (int, float)) or a_odds < 0:
        logging.error(f"Invalid odds: {a_odds}. Odds must be a non-negative number.")
        return "Unknown Classification"

    # Determine status level based on odds
    if a_odds <= 1.30:
        a_status = TeamAStatus(1)
    elif 1.31 <= a_odds <= 1.50:
        a_status = TeamAStatus(2)
    elif 1.51 <= a_odds <= 1.80:
        a_status = TeamAStatus(3)
    elif 1.81 <= a_odds <= 2.00:
        a_status = TeamAStatus(4)
    elif 2.01 <= a_odds <= 2.30:
        a_status = TeamAStatus(5)
    elif 2.31 <= a_odds <= 2.80:
        a_status = TeamAStatus(6)
    else:
        a_status = TeamAStatus(7)

    # Log the classification result
    classification = f"A{a_status.status}"
    logging.info(f"Odds {a_odds} classified as: {classification}")
    return classification


def classify_b_team(b_odds):

    if not isinstance(b_odds, (int, float)) or b_odds < 0:
        logging.error(f"Invalid odds: {b_odds}. Odds must be a non-negative number.")
        return "Unknown Classification"

    # Determine status level based on odds
    if b_odds <= 1.30:
        b_status = TeamBStatus(1)
    elif 1.31 <= b_odds <= 1.50:
        b_status = TeamBStatus(2)
    elif 1.51 <= b_odds <= 1.80:
        b_status = TeamBStatus(3)
    elif 1.81 <= b_odds <= 2.00:
        b_status = TeamBStatus(4)
    elif 2.01 <= b_odds <= 2.30:
        b_status = TeamBStatus(5)
    elif 2.31 <= b_odds <= 2.80:
        b_status = TeamBStatus(6)
    else:
        b_status = TeamBStatus(7)

    classification = f"B{b_status.status}"
    logging.info(f"Odds {b_odds} classified as: {classification}")
    return classification
