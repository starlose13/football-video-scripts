# from base_match_pipeline import BaseMatchPipeline
# from data_processor import MatchDataProcessor
# import openai
# import requests
# import logging

# class MatchDataPipelinePrediction(BaseMatchPipeline):
#     """Pipeline for processing match data and generating predictions."""

#     def __init__(self, api_url, folder_name='scene6'):
#         super().__init__(api_url, folder_name=folder_name)

#     def fetch_data(self):
#         response = requests.get(self.api_url)
#         if response.status_code != 200:
#             raise Exception(f"Failed to fetch data from API: {response.status_code}")
#         return response.json()

#     def generate_match_result_with_openai(self, a_team_name, b_team_name, home_team_name, away_team_name, prediction_result):
#         condition_text, card = self.get_condition_and_card(a_team_name, b_team_name, home_team_name, away_team_name, prediction_result)
#         prompt = (
#             f"{condition_text}. Write this dynamically for football fans, keeping it very brief—under 25 words! "
#             "Use punctuation like dot, comma, exclamation mark, question mark, and semicolon."
#         )

#         response = openai.ChatCompletion.create(
#             model="gpt-4-turbo",
#             messages=[
#                 {"role": "system", "content": "You are an AI assistant generating football match result summaries."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=100
#         )

#         generated_script = response['choices'][0]['message']['content'].strip()
#         return generated_script, card

#     def get_condition_and_card(self, a_team_name, b_team_name, home_team_name, away_team_name, prediction_result):
#         if prediction_result == "A win or draw":
#             if a_team_name == home_team_name:
#                 return f"My AI analysis suggests {a_team_name} will win or draw", "Win or Draw Home Team"
#             elif a_team_name == away_team_name:
#                 return f"My AI analysis suggests {a_team_name} will win or draw", "Win or Draw Away Team"
#         elif prediction_result == "A or B win":
#             return f"My AI analysis suggests either {a_team_name} or {b_team_name} will win", "Win Home or Away Team"
#         elif prediction_result == "A win":
#             if a_team_name == home_team_name:
#                 return f"My AI analysis suggests {a_team_name} will win", "Win Home Team"
#             elif a_team_name == away_team_name:
#                 return f"My AI analysis suggests {a_team_name} will win", "Win Away Team"
#         return "No specific result is found for this prediction", "none"

#     def process(self):
#         data = self.fetch_data()
#         for i, match_data in enumerate(data[:5], start=1):
#             match_info = self.process_match_data(match_data)
#             prediction_result, row_number = self.generate_prediction(match_info)
#             prompt_text, card_choice = self.generate_match_result_with_openai(
#                 match_info['a_team_name'], match_info['b_team_name'], match_info['home_team'], match_info['away_team'], prediction_result
#             )
            
#             processor = MatchDataProcessor(prompt_text)
#             word_count = processor.calculate_word_count()
#             reading_time = processor.calculate_reading_time()
            
#             match_info.update({
#                 "description": prompt_text,
#                 "word_count": word_count,
#                 "reading_time": reading_time,
#                 "card": card_choice
#             })
#             self.save_match_info(match_info, i)

#     def generate_prediction(self, match_info):
#         a_team = self.classify_a_team(match_info['a_team_odds'])
#         b_team = self.classify_b_team(match_info['b_team_odds'])
#         a_recent_g = self.classify_a_points(self.calculate_points(match_info['team_a_last_5']))
#         b_recent_g = self.classify_b_points(self.calculate_points(match_info['team_b_last_5']))
#         rank_diff = self.calculate_rank_difference(match_info['team_a_rank'], match_info['team_b_rank'])
#         return self.generate_result(a_team, b_team, a_recent_g, b_recent_g, rank_diff)

# # Run the pipeline
# if __name__ == "__main__":
#     api_url = 'https://dataprovider.predipie.com/api/v1/ai/test/'
#     pipeline = MatchDataPipelinePrediction(api_url)
#     pipeline.process()
