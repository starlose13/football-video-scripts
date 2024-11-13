from data_fetcher import DataFetcher
from description_generator import MatchDescriptionGenerator
from data_processor import MatchDataProcessor
from file_saver import MatchFileSaver

class MatchDataPipeline:
    """Main class to run the entire match data processing pipeline"""
    
    def __init__(self, api_url):
        self.fetcher = DataFetcher(api_url)
        self.generator = MatchDescriptionGenerator()
        self.saver = MatchFileSaver()

    def process_match_data(self):
        data = self.fetcher.fetch_data()
        
        for i, item in enumerate(data[:5], start=1):
            host_team = item.get('home', {}).get('name', 'Unknown Host Team')
            guest_team = item.get('away', {}).get('name', 'Unknown Guest Team')
            host_team_logo = item.get('home', {}).get('logo', 'No Logo Available')
            guest_team_logo = item.get('away', {}).get('logo', 'No Logo Available')
            host_team_country = item.get('home', {}).get('country', {}).get('name', 'Unknown Country')
            guest_team_country = item.get('away', {}).get('country', {}).get('name', 'Unknown Country')
            
            description = self.generator.generate_description(i, host_team, guest_team)
            processor = MatchDataProcessor(description)
            word_count = processor.calculate_word_count()
            reading_time = processor.calculate_reading_time()

            match_info = {
                "description": description,
                "word_count": word_count,
                "reading_time": reading_time,
                "home_team": {
                    "name": host_team,
                    "logo": host_team_logo,
                    "country": host_team_country
                },
                "away_team": {
                    "name": guest_team,
                    "logo": guest_team_logo,
                    "country": guest_team_country
                }
            }

            self.saver.save_to_file(match_info, i)


# Run the match data pipeline
if __name__ == "__main__":
    api_url = 'https://dataprovider.predipie.com/api/v1/ai/test/'
    pipeline = MatchDataPipeline(api_url)
    pipeline.process_match_data()
