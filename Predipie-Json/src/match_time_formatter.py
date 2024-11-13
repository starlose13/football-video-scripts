from datetime import datetime

class MatchTimeFormatter:
    """Formats date and time for match descriptions and additional details."""

    @staticmethod
    def format_full_time(match_time):
        """
        Converts a timestamp string to formatted date, time, and day.
        
        Parameters:
            match_time (str): A timestamp string in the format "%Y-%m-%dT%H:%M:%SZ".

        Returns:
            tuple: Formatted date (YYYY-MM-DD), time (HH:MM AM/PM UTC), and day of the week.
        """
        try:
            match_datetime = datetime.strptime(match_time, "%Y-%m-%dT%H:%M:%SZ")
            match_date = match_datetime.strftime("%Y-%m-%d")
            match_time_str = match_datetime.strftime("%I:%M %p UTC")
            match_day = match_datetime.strftime("%A")
            return match_date, match_time_str, match_day
        except ValueError:
            print(f"Error: Invalid date format for match_time: {match_time}")
            return "Unknown Date", "Unknown Time", "Unknown Day"
