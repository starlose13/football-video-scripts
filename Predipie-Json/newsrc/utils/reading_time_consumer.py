class MatchDataProcessor:
    
    def __init__(self, description, reading_speed=3.10, pause_times=None):
        self.description = description
        self.reading_speed = reading_speed
        self.pause_times = pause_times or {
            ',': 0.21,
            '.': 0.21,
            '!': 0.18,
            '?': 0.18,
            ';': 0.17,
        }

    def calculate_word_count(self):
        return len(self.description.split())

    def calculate_reading_time(self):
        pause_time = sum(self.description.count(p) * self.pause_times.get(p, 0) for p in self.pause_times)
        word_count = self.calculate_word_count()
        return round((word_count / self.reading_speed) + pause_time, 2)
