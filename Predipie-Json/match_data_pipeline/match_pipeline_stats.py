from base_match_pipeline import BaseMatchPipeline
from match_time_formatter import MatchTimeFormatter

class MatchDataPipelineWithStats(BaseMatchPipeline):
    """Pipeline for processing match data with additional odds and time formatting."""

    def __init__(self, api_url, folder_name='scene3'):
        super().__init__(api_url, folder_name=folder_name)

    def process(self):
        data = self.fetcher.fetch_data()
        time_formatter = MatchTimeFormatter()

        for i, match_data in enumerate(data[:5], start=1):
            match_info = self.process_match_data(match_data)
            
            match_date, match_time_str, match_day = time_formatter.format_full_time(match_data.get('start_time', 'Unknown Time'))
            match_info.update({
                "match_date": match_date,
                "match_time": match_time_str,
                "match_day": match_day
            })

            self.save_match_info(match_info, i)
