import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def classify_a_points(a_points):

    if not isinstance(a_points, (int, float)) or a_points < 0:
        logging.error(f"Invalid points: {a_points}. Points must be a non-negative number.")
        return "Unknown Group"

    if 13 <= a_points <= 15:
        group = "ARecentG1"
    elif 11 <= a_points <= 12:
        group = "ARecentG2"
    elif 9 <= a_points <= 10:
        group = "ARecentG3"
    elif 7 <= a_points <= 8:
        group = "ARecentG4"
    elif 5 <= a_points <= 6:
        group = "ARecentG5"
    elif 3 <= a_points <= 4:
        group = "ARecentG6"
    else:
        group = "ARecentG7"

    logging.info(f"Classified {a_points} points into group: {group}")
    return group

def classify_b_points(b_points):

    if not isinstance(b_points, (int, float)) or b_points < 0:
        logging.error(f"Invalid points: {b_points}. Points must be a non-negative number.")
        return "Unknown Group"

    if 13 <= b_points <= 15:
        group = "BRecentG1"
    elif 11 <= b_points <= 12:
        group = "BRecentG2"
    elif 9 <= b_points <= 10:
        group = "BRecentG3"
    elif 7 <= b_points <= 8:
        group = "BRecentG4"
    elif 5 <= b_points <= 6:
        group = "BRecentG5"
    elif 3 <= b_points <= 4:
        group = "BRecentG6"
    else:
        group = "BRecentG7"

    logging.info(f"Classified {b_points} points into group: {group}")
    return group
