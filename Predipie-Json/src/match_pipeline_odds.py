from base_match_pipeline import BaseMatchPipeline
from data_processor import MatchDataProcessor 
import openai

class MatchDataPipelineWithOdds(BaseMatchPipeline):
    """Pipeline for processing match data with dynamic odds descriptions."""
    
    def __init__(self, api_url, folder_name='scene4'):
        super().__init__(api_url, folder_name=folder_name)
    
    def generate_description_with_odds(self, host_team, guest_team, home_odds, guest_odds, draw_odds):
        """Generates a description of match odds using the ChatGPT API."""
        prompt = (
            f"[Generate a concise and complete description for football match odds, using only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon. "
            f"Provide only the odds information directly, without introducing the teams or match. State each type of odds clearly and avoid abbreviations or parentheses. Keep it under 45 words.] "
            f"The home team, {host_team}, has odds of winning at {home_odds}. The away team, {guest_team}, has odds of winning at {guest_odds}. The odds for a draw are {draw_odds}."
        )
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping to create dynamic football match descriptions with odds information."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            return response['choices'][0]['message']['content'].strip()
        except openai.error.OpenAIError as e:
            print(f"OpenAI API error: {e}")
            return "Description generation with odds failed."
    
    def process(self):
        """Fetches data, generates descriptions with odds, and saves them."""
        data = self.fetcher.fetch_data()
        
        for i, match_data in enumerate(data[:5], start=1):
            host_team = match_data.get('home', {}).get('name', 'Unknown Host Team')
            guest_team = match_data.get('away', {}).get('name', 'Unknown Guest Team')
            home_odds = match_data.get('odds', {}).get('home', 'N/A')
            guest_odds = match_data.get('odds', {}).get('away', 'N/A')
            draw_odds = match_data.get('odds', {}).get('draw', 'N/A')
            
            # Generate the description with odds
            match_description = self.generate_description_with_odds(host_team, guest_team, home_odds, guest_odds, draw_odds)
            
            # Process reading time and word count
            processor = MatchDataProcessor(match_description)  # استفاده مستقیم از MatchDataProcessor
            word_count = processor.calculate_word_count()
            reading_time = processor.calculate_reading_time()

            # Format data for saving
            match_info = {
                "description": match_description,
                "odds": {
                    "home": home_odds,
                    "draw": draw_odds,
                    "away": guest_odds
                },
                "word_count": word_count,
                "reading_time": reading_time
            }

            # Save match info for scene4
            self.save_match_info(match_info, i)
