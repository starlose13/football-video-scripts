from base_match_pipeline import BaseMatchPipeline
from data_processor import MatchDataProcessor  # اطمینان از وارد کردن کلاس پردازش داده
import openai

class MatchDataPipelineWithRecentForm(BaseMatchPipeline):
    """Pipeline for processing match data with recent form descriptions."""
    
    def __init__(self, api_url, folder_name='scene5'):
        super().__init__(api_url, folder_name=folder_name)
    
    def generate_description_with_recent_form(self, host_team, guest_team, host_results, host_wins, host_draws, host_losses, guest_results, guest_wins, guest_draws, guest_losses):
        """Generates a description of match recent form using the ChatGPT API."""
        prompt = (
            f"[Generate a concise description of each team’s recent form, using full words for clarity and avoiding abbreviations like 'W', 'D', or 'L'. "
            f"Focus on readability. Limit to 200 characters. Use only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon.] "
            f"The {host_team} recent form shows {host_results} (Wins: {host_wins}, Draws: {host_draws}, Losses: {host_losses}), "
            f"while the {guest_team} has recorded {guest_results} (Wins: {guest_wins}, Draws: {guest_draws}, Losses: {guest_losses})."
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping to create dynamic football match descriptions with recent form information."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            return response['choices'][0]['message']['content'].strip()
        except openai.error.OpenAIError as e:
            print(f"OpenAI API error: {e}")
            return "Description generation with recent form failed."
    
    def process(self):
        """Fetches data, generates descriptions with recent form, and saves them."""
        data = self.fetcher.fetch_data()
        
        for i, match_data in enumerate(data[:5], start=1):
            host_team = match_data.get('home', {}).get('name', 'Unknown Host Team')
            guest_team = match_data.get('away', {}).get('name', 'Unknown Guest Team')
            
            # Extract recent form details for home and away teams
            host_results = match_data.get('team_related_match', [{}])[0].get('five_previous_matches', [])
            host_wins = host_results.count('w')
            host_draws = host_results.count('d')
            host_losses = host_results.count('l')

            guest_results = match_data.get('team_related_match', [{}])[1].get('five_previous_matches', [])
            guest_wins = guest_results.count('w')
            guest_draws = guest_results.count('d')
            guest_losses = guest_results.count('l')
            
            # Generate the description with recent form
            match_description = self.generate_description_with_recent_form(
                host_team, guest_team, host_results, host_wins, host_draws, host_losses,
                guest_results, guest_wins, guest_draws, guest_losses
            )
            
            # Process reading time and word count
            processor = MatchDataProcessor(match_description)
            word_count = processor.calculate_word_count()
            reading_time = processor.calculate_reading_time()

            # Format data for saving
            match_info = {
                "description": match_description,
                "recent_form": {
                    "home_team": {
                        "last_5_matches": host_results,
                        "wins": host_wins,
                        "draws": host_draws,
                        "losses": host_losses
                    },
                    "away_team": {
                        "last_5_matches": guest_results,
                        "wins": guest_wins,
                        "draws": guest_draws,
                        "losses": guest_losses
                    }
                },
                "word_count": word_count,
                "reading_time": reading_time
            }

            # Save match info for scene5
            self.save_match_info(match_info, i)
