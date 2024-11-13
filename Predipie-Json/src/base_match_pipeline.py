from data_fetcher import DataFetcher
from description_generator import MatchDescriptionGenerator
from data_processor import MatchDataProcessor
from file_saver import MatchFileSaver

class BaseMatchPipeline:
    """Base class to handle common operations in match data pipelines."""

    def __init__(self, api_url, folder_name='scene2'):
        self.api_url = api_url
        self.fetcher = DataFetcher(api_url)
        self.generator = MatchDescriptionGenerator()
        self.saver = MatchFileSaver(folder_name)

    def extract_team_info(self, team_data, team_type="home"):
        """Extracts team information such as name, logo, and country."""
        return {
            "name": team_data.get('name', f'Unknown {team_type.capitalize()} Team'),
            "logo": team_data.get('logo', 'No Logo Available'),
            "country": team_data.get('country', {}).get('name', 'Unknown Country')
        }

    def process_match_data(self, match_data):
        """Process general match data, including description generation and reading time calculation."""
        # Extract host and guest team info
        host_team = self.extract_team_info(match_data.get('home', {}), "home")
        guest_team = self.extract_team_info(match_data.get('away', {}), "away")

        # Generate description and calculate reading metrics
        match_description = self.generator.generate_description(
            1, host_team["name"], guest_team["name"]
        )
        processor = MatchDataProcessor(match_description)
        word_count = processor.calculate_word_count()
        reading_time = processor.calculate_reading_time()

        return {
            "description": match_description,
            "word_count": word_count,
            "reading_time": reading_time,
            "home_team": host_team,
            "away_team": guest_team
        }

    def save_match_info(self, match_info, index):
        """Save match information to file."""
        self.saver.save_to_file(match_info, index)
