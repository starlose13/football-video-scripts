from datetime import datetime
from base_match_pipeline import BaseMatchPipeline
from match_time_formatter import MatchTimeFormatter
from data_processor import MatchDataProcessor 
import openai


class MatchDataPipelineWithStats(BaseMatchPipeline):
    """Pipeline for processing match data with additional odds and time formatting."""

    def __init__(self, api_url, folder_name='scene3'):
        super().__init__(api_url, folder_name=folder_name)

        
    def generate_match_description(self, host_team, guest_team, match_time):
        # Format the match time to extract date and time
        match_datetime = datetime.strptime(match_time, "%Y-%m-%dT%H:%M:%SZ")
        time_str = match_datetime.strftime("%I:%M %p").lstrip("0")
        day_str = match_datetime.strftime("%A")
        date_str = match_datetime.strftime("%Y-%m-%d")
        
        # Create a prompt for OpenAI to generate the description
        prompt = (
            f"As if you're a live TV host, build excitement for the football game. This match starts at: {time_str} on {day_str}, {date_str}. "
            f"Keep it upbeat, clear, and full of energy to captivate the audience, and ensure it’s under 22 words. "
            "Use only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon."
        )

        # Call the ChatGPT API to generate the description
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant helping to create dynamic football match descriptions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50
        )
        generated_script = response['choices'][0]['message']['content'].strip()
        return generated_script

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
            
            # Generate the description using the ChatGPT API
            host_team = match_data.get('home', {}).get('name', 'Unknown Host Team')
            guest_team = match_data.get('away', {}).get('name', 'Unknown Guest Team')
            match_time = match_data.get('start_time', 'Unknown Time')
            match_description = self.generate_match_description(host_team, guest_team, match_time)
            
            processor = MatchDataProcessor(match_description)  
            word_count = processor.calculate_word_count()
            reading_time = processor.calculate_reading_time()
            
            # Update match info with description and reading time details
            match_info.update({
                "description": match_description,
                "word_count": word_count,
                "reading_time": reading_time
            })

            self.save_match_info(match_info, i)
