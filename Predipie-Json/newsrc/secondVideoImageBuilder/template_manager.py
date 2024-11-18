class TemplateManager:
    base_positions = {
        "home_team_logo": (410, 845),
        "home_team_name": (730, 900),
        "away_team_logo": (3220, 845),
        "away_team_name": (2480, 900)
    }

    position_mappings = [
        {**base_positions},  
        {**base_positions, "match_date": (1736, 847), "match_time": (2031, 847), "match_day": (1590, 847)}, 
        {**base_positions, "home_odds": (1298, 1086), "draw_odds": (1870, 1086), "away_odds": (2435, 1086)}, 
        {**base_positions, "home_team_last_5": (1137, 1357), "away_team_last_5": (2350, 1357)}, 
        {**base_positions}  
    ]

    adjusted_y_positions = {
        "home_team_logo": (410, 375),
        "home_team_name": (730, 435),
        "away_team_logo": (3220, 375),
        "away_team_name": (2480, 435)
    }

    fifth_image_positions = {
        "home_team_logo": (410, 340),
        "home_team_name": (730, 400),
        "away_team_logo": (3220, 340),
        "away_team_name": (2660, 400),
        "match_date": (1700, 1307),
        "match_time": (1994, 1307),
        "match_day": (1554, 1307),
        "home_odds": (1275, 1546),
        "draw_odds": (1847, 1546),
        "away_odds": (2413, 1546),
        "home_team_last_5": (1128, 1813),
        "away_team_last_5": (2284, 1813)
    }

    @staticmethod
    def get_adjusted_positions(image_index):

        if image_index >= len(TemplateManager.position_mappings):
            raise ValueError(f"Invalid image_index {image_index}. Must be between 0 and {len(TemplateManager.position_mappings) - 1}")

        if image_index == 4:  
            adjusted_positions = {**TemplateManager.position_mappings[image_index], **TemplateManager.fifth_image_positions}
        elif image_index != 0:  
            adjusted_positions = {**TemplateManager.position_mappings[image_index], **TemplateManager.adjusted_y_positions}
        else:
            adjusted_positions = TemplateManager.position_mappings[image_index]  
        print(f"Adjusted positions for image index {image_index}: {adjusted_positions}")
        return adjusted_positions
