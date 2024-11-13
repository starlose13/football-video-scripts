from base_match_pipeline import BaseMatchPipeline

class MatchDataPipeline(BaseMatchPipeline):
    """Pipeline for processing basic match data."""

    def __init__(self, api_url, folder_name='scene2'):
        super().__init__(api_url, folder_name=folder_name)

    def process(self):
        data = self.fetcher.fetch_data()
        
        for i, match_data in enumerate(data[:5], start=1):
            match_info = self.process_match_data(match_data)
            self.save_match_info(match_info, i)


if __name__ == "__main__":
    api_url = 'https://dataprovider.predipie.com/api/v1/ai/test/'
    pipeline = MatchDataPipeline(api_url)
    pipeline.process()
