from datetime import datetime
import time
from dotenv import load_dotenv
import openai
from typing import Dict, Any, List
import json
import os
from utils.json_saver import JsonSaver
from dataFetcher.fetch_last_five_matches import FetchLast5Matches
from dataFetcher.fetch_match_stats import FetchMatchTime
from dataFetcher.fetch_odds_ranks import FetchOddsRanks
from dataFetcher.fetch_team_info import FetchTeamInfo
from utils.reading_time_consumer import MatchDataProcessor
from config.config import BASE_URL, START_AFTER, START_BEFORE, PROGRAM_NAME
from dataClassifier.game_result_predictor import GameResultPredictor
from utils.program_counter import increment_program_number, get_program_number
from openai.error import RateLimitError
from finalScore.results_with_start_before import ScoreCalculator

load_dotenv()

class GeneratePrompts:
    correct_predictions_count = 0  
    def __init__(self, api_key: str):
        openai.api_key = api_key
    def openai_request_with_retry(self, model, messages, max_tokens, retries=5):
        delay = 2  
        for attempt in range(retries):
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens
                )
                return response
            except RateLimitError:
                print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  
        print("Max retries reached. Could not complete the request.")
        return None
    
    def extract_scores(self, score: str) -> Dict[str, int]:
        try:
            home_score, away_score = map(int, score.split("-"))
            return {"home_score": home_score, "away_score": away_score}
        except ValueError:
            print(f"Invalid score format: {score}")
            return {"home_score": 0, "away_score": 0}
        
    def parse_timestamp(self, timestamp: str) -> Dict[str, str]:
        match_datetime = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        date_str = match_datetime.strftime("%Y-%m-%d")
        day_str = match_datetime.strftime("%A")
        time_str = match_datetime.strftime("%I:%M %p").lstrip("0")
        return {"date": date_str, "day": day_str, "time": time_str}

    def load_json_file(self, filename: str) -> List[Dict[str, Any]]:
        filepath = os.path.join(self.data_folder, filename)
        with open(filepath, 'r') as file:
            return json.load(file)
   
#################################################################################################################
###################################### FIRST VIDEO STARTED HERE #################################################
#################################################################################################################

    def generate_first_video_intro_with_openai(self , program_number: int) -> Dict[str, Any]:
        prompt = (
            f"Imagine you are a football program host introducing todays episode. "
            f"Start with: 'Hi {PROGRAM_NAME} fans!' "
            f"Welcome to episode {program_number}! "
            f"In this episode, we will review the results of yesterdays matches and see how accurate our predictions were. "
            f"Keep the tone lively, professional, and engaging. Make it concise—under 50 words with a confident and energetic delivery! "
            f"Output should be less than 35 words.Use only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon."
            f"Important: Do not use apostrophes in the output."
        )
        response = self.openai_request_with_retry(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant generating a dynamic introduction for a football program segment about reviewing match predictions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=80
        )
        generated_intro = response['choices'][0]['message']['content'].strip()
        generated_intro = (
                generated_intro.replace("’", "'")
                .replace("‘", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("—", "-")
            )
        processor = MatchDataProcessor(generated_intro)
        reading_time = processor.calculate_reading_time()

        return {"prompt": generated_intro, "reading_time": reading_time}

    def generate_final_score_prompt(self, match_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prompts = []
        for match in match_data:
            home_team = match.get("home_team_name", "N/A")
            away_team = match.get("away_team_name", "N/A")
            start_timestamp = match.get("startTimestamp", "N/A")
            score = match.get("Score", "N/A")
            
            parsed_timestamp = self.parse_timestamp(start_timestamp)
            extracted_scores = self.extract_scores(score)

            if extracted_scores['home_score'] > extracted_scores['away_score']:
                result_sentence = f"{home_team} triumphed with a score of {extracted_scores['home_score']}-{extracted_scores['away_score']} over {away_team}."
            elif extracted_scores['home_score'] < extracted_scores['away_score']:
                result_sentence = f"{away_team} emerged victorious with a score of {extracted_scores['away_score']}-{extracted_scores['home_score']} against {home_team}."
            else:
                result_sentence = f"The match between {home_team} and {away_team} concluded in a thrilling draw, with a final score of {extracted_scores['home_score']}-{extracted_scores['away_score']}."

            prompt = (
                f"As part of our sports coverage, here is a quick recap of the match between {home_team} and {away_team}. "
                f"The game took place on {parsed_timestamp['day']} at {parsed_timestamp['time']}. "
                f"{result_sentence} "
                f"Lets see what we have predicted."
                f"Output should be less than 30 words. Use only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon."
                f"Important: Do not use apostrophes in the output."
            )

            # Request OpenAI to refine the narration
            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant generating sportscaster-style narrations for football match results."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )

            # Process the generated narration
            generated_final_score = response['choices'][0]['message']['content'].strip()
            generated_final_score = (
                generated_final_score.replace("’", "'")
                .replace("‘", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("—", "-")
            )

            processor = MatchDataProcessor(generated_final_score)
            reading_time = processor.calculate_reading_time()

            # Append results
            prompts.append({
                "prompt": generated_final_score,
                "reading_time": reading_time
            })

        return prompts

        
    def generate_prediction_evaluation_prompt(self, match_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prompts = []
        for match in match_data:
            # Extract necessary data
            card_value = match.get("Card", "N/A")
            score = match.get("Score", "N/A")
            extracted_scores = self.extract_scores(score)
            home_score = extracted_scores.get("home_score", 0)
            away_score = extracted_scores.get("away_score", 0)

            # Determine if the prediction was correct
            prediction_correct = True
            if card_value == "Win Home or Away Team":
                prediction_correct = home_score != away_score
            elif card_value == "Win Away Team":
                prediction_correct = away_score > home_score
            elif card_value == "Win Home Team":
                prediction_correct = home_score > away_score
            elif card_value == "Win or Draw Home Team":
                prediction_correct = home_score >= away_score
            elif card_value == "Win or Draw Away Team":
                prediction_correct = away_score >= home_score
            elif card_value == "Draw":
                prediction_correct = home_score == away_score

            if prediction_correct:
                self.correct_predictions_count += 1

            # Generate a dynamic and diverse prompt
            prompt = (
                f"As a sports commentator, analyze the prediction based on: "
                f"- Predicted Outcome: {card_value}"
                f"- Prediction Status: {'Correct' if prediction_correct else 'Incorrect'}]"
                f"Write an exciting commentary to reflect the result. Use simple punctuation (e.g., '-', '.', ',') "
                f"and avoid typographic substitutions like fancy dashes or quotes. For correct predictions, "
                f"celebrate with enthusiasm and creativity (e.g., 'Spot on!' or 'What a call!'). For incorrect ones, express "
                f"humor, sportsmanship, or optimism (e.g., 'Close but not quite,' or 'Next time for sure!'). "
                f"Keep the output concise, under 45 words."
            )

            # Generate commentary using OpenAI
            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI sports commentator providing dynamic and engaging evaluations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            # Replace any fancy characters with simple ones
            generated_commentary = response["choices"][0]["message"]["content"].strip()
            generated_commentary = (
                generated_commentary.replace("’", "'")
                .replace("‘", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("—", "-")
            )

            # Calculate reading time
            processor = MatchDataProcessor(generated_commentary)
            reading_time = processor.calculate_reading_time()

            # Append result to prompts list
            prompts.append({
                "prompt": generated_commentary,
                "evaluation": "correct" if prediction_correct else "incorrect",
                "reading_time": reading_time
            })

        return prompts


                    
        
    def generate_first_video_closing_with_openai(self, correct_predictions_count: int, program_number: int) -> Dict[str, Any]:
        # Calculate success rate
        success_rate = int((correct_predictions_count / len(game_results)) * 100)
        # Generate dynamic closing prompt based on success rate
        if success_rate > 70:
            prompt = (
                f"Congratulations to us! Yesterday, we nailed it with an impressive success rate about {success_rate} percent ! "
                f"Now, let us go to my colleague and see which games are being predicted today. Zoobin, what do you have for us?"
                f"Output should be less than 50 words.Use only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon."
                f" Important: Do not use apostrophes in the output."
            )
        else:
            prompt = (
                f"Our success rate yesterday was {success_rate}%. While it wasn not our best, we are ready to bounce back stronger! "
                f"Now, let us go to my colleague and see which games are being predicted today. Zoobin, what do you have for us? we hope so today we have better predictions."
                f"Output should be less than 50 words.Use only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon."                
                f" Important: Do not use apostrophes in the output."
            )

        # Send prompt to OpenAI
        response = self.openai_request_with_retry(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant generating an engaging and dynamic closing narration for a sports program."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60
        )
        generated_closing = response['choices'][0]['message']['content'].strip()
        generated_closing = (
                generated_closing.replace("’", "'")
                .replace("‘", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("—", "-")
            )
        processor = MatchDataProcessor(generated_closing)
        reading_time = processor.calculate_reading_time()

        return {"prompt": generated_closing, "reading_time": reading_time}


#################################################################################################################
######################################FIRST VIDEO ENDED HERE#####################################################
#################################################################################################################

                                                #####

#################################################################################################################
######################################SECOND VIDEO STARTED HERE##################################################
#################################################################################################################

    def generate_second_video_intro_with_openai(self) -> Dict[str, Any]:
        prompt = (
            f"Start with: 'Hi {PROGRAM_NAME}! ' Tonight, we are bringing you some fantastic lineup of top matches for you. "
            f"Keep it upbeat, friendly, and super energetic. Make it concise—under 40 words with a punchy, engaging tone! "
            f"Use only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon. "
            f"Important: Do not mention any game statistics, player names, or game history information in the output."
        )
        response = self.openai_request_with_retry(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant generating an introductory narration for a sports program."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60
        )
        generated_intro = response['choices'][0]['message']['content'].strip()
        generated_intro = (
                generated_intro.replace("’", "'")
                .replace("‘", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("—", "-")
            )
        processor = MatchDataProcessor(generated_intro)
        reading_time = processor.calculate_reading_time()
        
        return {"prompt": generated_intro, "reading_time": reading_time}
    
    def prompt_for_team_info(self, team_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prompts = []
        for i, team_info in enumerate(team_data, start=1):
            home_team_name = team_info.get("home_team_name", "Unknown Home Team")
            away_team_name = team_info.get("away_team_name", "Unknown Away Team")

            if i == 1:
                intro = f"Let's start with the first match: {home_team_name} versus {away_team_name}."
            elif i in [2, 3, 4]:
                ordinal = {2: "second", 3: "third", 4: "fourth"}[i]
                intro = f"Let's continue with the {ordinal} match: {home_team_name} against {away_team_name}."
            else:  
                intro = f"And the last match: {home_team_name} versus {away_team_name}."
    
            prompt = (
                f"{intro} Create a brief, dynamic match description under 80 characters, using only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon. "
                f"Important: Do not mention any game statistics, player names, or game history information."
            )

            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant creating dynamic descriptions based on team info."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=80
            )
            
            generated_script = response['choices'][0]['message']['content'].strip()
            generated_script = (
                generated_script.replace("’", "'")
                .replace("‘", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("—", "-")
            )

            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()
            
            prompts.append({
                "prompt": generated_script,
                "home_team_name": home_team_name,
                "away_team_name": away_team_name,
                "reading_time": reading_time
            })
            
        return prompts
    
    def prompt_for_match_stats(self, match_stats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prompts = []
        for stats in match_stats:
            home_team = stats.get("home_team", "Unknown Home Team")
            away_team = stats.get("away_team", "Unknown Away Team")
            start_timestamp = stats.get("startTimestamp", "")
            
            if start_timestamp:
                match_datetime = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
                time_str = match_datetime.strftime("%I:%M %p").lstrip("0")
                day_str = match_datetime.strftime("%A")
                date_str = match_datetime.strftime("%Y-%m-%d")
            else:
                time_str = "Unknown Time"
                day_str = "Unknown Day"
                date_str = "Unknown Date"


            prompt = (
                f"As if you're a live TV host, build excitement for the game of football between {home_team} and {away_team}. "
                f"This match starts at: {time_str} on {day_str}, {date_str}. "
                "Keep it upbeat, clear, and full of energy to captivate the audience. "
                "Also, make it concise and under 22 words. "
                "Remember: only use these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon."
            )

            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping to create dynamic football match descriptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            
            generated_script = response['choices'][0]['message']['content'].strip()
            generated_script = (
                generated_script.replace("’", "'")
                .replace("‘", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("—", "-")
            )
            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()

            prompts.append({
                "prompt": generated_script,
                "home_team": home_team,
                "away_team": away_team,
                "date": date_str,
                "day": day_str,
                "time": time_str,
                "reading_time": reading_time
            })
            
        return prompts

    def prompt_for_odds(self, odds_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prompts = []
        for odds in odds_data:
            home_team = odds.get("home_team", "Unknown Home Team")
            away_team = odds.get("away_team", "Unknown Away Team")
            
            if odds.get("odds"):
                home_odds = odds["odds"][0].get("homeWin", "N/A")
                draw_odds = odds["odds"][0].get("draw", "N/A")
                away_odds = odds["odds"][0].get("awayWin", "N/A")
            else:
                home_odds = "N/A"
                draw_odds = "N/A"
                away_odds = "N/A"
        
            prompt = (
                f"[Generate a concise and complete description for football match odds, using only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon. "
                f"Provide only the odds information directly, without introducing the teams or match. State each type of odds clearly and avoid abbreviations or parentheses. Keep it under 45 words.] "
                f"The home team, {home_team}, has odds of winning at {home_odds}. The away team, {away_team}, has odds of winning at {away_odds}. The odds for a draw are {draw_odds}."
            )

            # Generate response from OpenAI
            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping to create dynamic football match descriptions with odds information."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            
            generated_script = response['choices'][0]['message']['content'].strip()
            generated_script = (
                generated_script.replace("’", "'")
                .replace("‘", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("—", "-")
            )
            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()

            prompts.append({
                "prompt": generated_script,
                "home_team": home_team,
                "away_team": away_team,
                "home_odds": home_odds,
                "draw_odds": draw_odds,
                "away_odds": away_odds,
                "reading_time": reading_time
            })
            
        return prompts


    def prompt_for_last5matches(self, matches_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prompts = []
        for match_info in matches_data:
            home_team = match_info["home_team"]["team_name"]
            guest_team = match_info["away_team"]["team_name"]
            home_results = match_info["home_team"]["last_5_matches"]
            guest_results = match_info["away_team"]["last_5_matches"]

            home_wins = match_info["home_team"]["results_count"]["wins"]
            home_draws = match_info["home_team"]["results_count"]["draws"]
            home_losses = match_info["home_team"]["results_count"]["losses"]

            guest_wins = match_info["away_team"]["results_count"]["wins"]
            guest_draws = match_info["away_team"]["results_count"]["draws"]
            guest_losses = match_info["away_team"]["results_count"]["losses"]

            prompt = (
                f"[Generate a concise description of each team’s recent form, using full words for clarity and avoiding abbreviations like 'W', 'D', or 'L'. "
                f"Focus on readability. Limit to 200 characters. Use only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon.] "
                f"The {home_team} recent form shows {home_results} (Wins: {home_wins}, Draws: {home_draws}, Losses: {home_losses}), "
                f"while the {guest_team} has recorded {guest_results} (Wins: {guest_wins}, Draws: {guest_draws}, Losses: {guest_losses})."
            )

            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping to create dynamic football match descriptions with recent form information."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            
            generated_script = response['choices'][0]['message']['content'].strip()
            generated_script = (
                generated_script.replace("’", "'")
                .replace("‘", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("—", "-")
            )
            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()

            prompts.append({"prompt": generated_script, "reading_time": reading_time})
            
        return prompts


    def prompt_for_match_result(self, match_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prompts = []
        for result in match_results:
            home_team_name = result["home_team_name"]
            away_team_name = result["away_team_name"]
            card = result["Card"]

            if card == "Win Home Team":
                condition_text = f"My analysis predicts the {home_team_name} will win this match."
            elif card == "Win Away Team":
                condition_text = f"My analysis predicts the {away_team_name} will win this match."
            elif card == "Win or Draw Home Team":
                condition_text = f"The prediction suggests that the {home_team_name} will win or at least secure a draw."
            elif card == "Win or Draw Away Team":
                condition_text = f"The prediction suggests that the {away_team_name} will win or at least secure a draw."
            elif card == "Win Home or Away Team":
                condition_text = f"The prediction suggests that either the {home_team_name} or the {away_team_name} will claim victory."
            else:
                condition_text = "No specific prediction is available for this match."

            prompt = (
                f"{condition_text} Keep it concise and engaging—under 25 words! "
                "Use these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon. "
                "Avoid mentioning betting or related terminology."
            )

            response = self.openai_request_with_retry(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant generating dynamic and engaging football match result predictions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )

            generated_script = response['choices'][0]['message']['content'].strip()
            generated_script = (
                generated_script.replace("’", "'")
                .replace("‘", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("—", "-")
            )
            processor = MatchDataProcessor(generated_script)
            reading_time = processor.calculate_reading_time()

            prompts.append({"prompt": generated_script, "card": card, "reading_time": reading_time})

        return prompts


    def generate_second_video_closing_with_openai(self, program_number: int) -> Dict[str, Any]:

        prompt = (
            f"Wrap up Episode {program_number} with a friendly closing: 'Just a reminder, I'm only an AI, this isn’t financial advice!' "
            f"Encourage viewers to tune in daily, join the {PROGRAM_NAME} community, and get ready for Episode {program_number + 1} tomorrow. "
            f"End with: 'don't trade your life for entertainment! Goodbye!' "
            f"Keep it complete and under 40 words. Use these punctuation marks frequently: dot, comma, exclamation mark, question mark, and semicolon. Don't use dash or underscore."
        )
        response = self.openai_request_with_retry(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant generating a friendly closing statement for a sports program."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        generated_closing = response['choices'][0]['message']['content'].strip()
        generated_closing = (
                generated_closing.replace("’", "'")
                .replace("‘", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("—", "-")
            )
        processor = MatchDataProcessor(generated_closing)
        reading_time = processor.calculate_reading_time()
        
        return {"prompt": generated_closing, "reading_time": reading_time}
    
#################################################################################################################
######################################SECOND VIDEO ENDED HERE####################################################
#################################################################################################################

    def generate_first_video_narration(
        self,
        intro_result: Dict[str, Any],
        final_score_result: List[Dict[str, Any]],
        evaluation_result: List[Dict[str, Any]],
        closing_result: Dict[str, Any]
    ) -> Dict[str, str]:
        # Add the intro
        narration_text = intro_result["prompt"] 

        # Process each match
        for i in range(len(final_score_result)):
            # Add match narration
            narration_text += final_score_result[i]["prompt"] 
            narration_text += "So, what did we predict for this match?"
            
            # Add prediction evaluation
            if evaluation_result[i]["evaluation"] == "correct":
                narration_text += "Yes, we got it right! " + evaluation_result[i]["prompt"] 
            else:
                narration_text += "Oh no, we missed it! Unfortunately, our prediction was incorrect. " + evaluation_result[i]["prompt"] 
            
            # Add transition phrase for all matches except the last one
            if i < len(final_score_result) - 1:
                narration_text += "Alright, let's move on to the next match."

        # Add the closing statement
        narration_text +=  closing_result["prompt"]

        return {"narration": narration_text}



    def generate_second_video_narration(
        self,
        intro_result: Dict[str, Any],
        team_info_result: List[Dict[str, Any]],
        match_stats_result: List[Dict[str, Any]],
        odds_result: List[Dict[str, Any]],
        last5matches_result: List[Dict[str, Any]],
        match_result_prompts: List[Dict[str, Any]],
        closing_result: Dict[str, Any]
    ) -> Dict[str, str]:

        narration_text = intro_result["prompt"] 

        for i in range(len(team_info_result)):
            narration_text += (
                team_info_result[i]["prompt"] +
                match_stats_result[i]["prompt"] +
                odds_result[i]["prompt"] +
                last5matches_result[i]["prompt"] + 
                match_result_prompts[i]["prompt"]
            )

        narration_text += closing_result["prompt"]

        return {"narration": narration_text}
    
if __name__ == "__main__":
    openai.api_key = os.getenv('OPENAI_API_KEY')
    api_key = openai.api_key
    prompt_generator = GeneratePrompts(api_key=api_key)
    json_saver = JsonSaver()
    today_date = START_AFTER
    yesterday_date = START_BEFORE
    # Increase program number
    increment_program_number()
    program_number = get_program_number()
    prompt_folder = os.path.join(today_date + "_json_match_output_folder", "prompts")
    narration_folder = os.path.join(today_date + "_json_match_output_folder", "narrations")

    # Fetch data
    fetch_last5matches = FetchLast5Matches(base_url=BASE_URL)
    fetch_match_stats = FetchMatchTime(base_url=BASE_URL)
    fetch_odds = FetchOddsRanks(base_url=BASE_URL)
    fetch_team_info = FetchTeamInfo(base_url=BASE_URL)
    game_result_predictor = GameResultPredictor()
    fetch_final_score = ScoreCalculator(base_url=BASE_URL,start_after=START_BEFORE)
    
    game_results = game_result_predictor.predict_game_results()

    ##################################### GENERATE PROMPTS OF FIRST VIDEO  #####################################
    ############################################################################################################
    fetch_final_score.update_scores_in_file()
    score_output_folder = os.path.join(START_AFTER + "_json_match_output_folder", "final_score_prompt_output_folder")
    evaluation_output_folder = os.path.join(START_AFTER + "_json_match_output_folder", "evaluation_prompt_output_folder")
    final_score_data_path = os.path.join(yesterday_date + "_json_match_output_folder", "match_prediction_result.json")
    if os.path.exists(final_score_data_path):
        with open(final_score_data_path, 'r', encoding="utf-8") as file:
            final_score_data = json.load(file)
    else:
        print(f"Error: File {final_score_data_path} not found.")
        final_score_data = []
    final_score_result = prompt_generator.generate_final_score_prompt(final_score_data)
    json_saver.save_to_json(final_score_result, "final_score_prompt.json",custom_folder=score_output_folder)

    evaluation_result = prompt_generator.generate_prediction_evaluation_prompt(final_score_data)
    json_saver.save_to_json(evaluation_result, "evaluation_prompt.json",custom_folder=evaluation_output_folder)


    first_intro_result = prompt_generator.generate_first_video_intro_with_openai(program_number=program_number)
    json_saver.save_to_json(first_intro_result, "first_intro_prompt.json",custom_folder=prompt_folder)

    first_closing_result = prompt_generator.generate_first_video_closing_with_openai(correct_predictions_count=prompt_generator.correct_predictions_count,program_number=program_number)
    json_saver.save_to_json(first_closing_result, "first_closing_prompt.json",custom_folder=prompt_folder)

    
    first_video_result = prompt_generator.generate_first_video_narration(
        intro_result= first_intro_result,
        final_score_result= final_score_result,
        evaluation_result= evaluation_result,
        closing_result = first_closing_result,
    )
    json_saver.save_to_json(first_video_result, "first_video_narration.json", custom_folder=narration_folder)

    ##################################### GENERATE PROMPTS OF SECOND VIDEO  #####################################
    #############################################################################################################
    last5matches_data = fetch_last5matches.get_last5matches(start_after=START_AFTER)
    match_stats_data = fetch_match_stats.get_match_times(start_after=START_AFTER)
    odds_data = fetch_odds.get_odds_ranks(start_after=START_AFTER)
    team_info_data = fetch_team_info.get_team_info(start_after=START_AFTER)
    second_intro_result = prompt_generator.generate_second_video_intro_with_openai()
    json_saver.save_to_json(second_intro_result, "second_intro_prompt.json",custom_folder=prompt_folder)

    second_closing_result = prompt_generator.generate_second_video_closing_with_openai(program_number=program_number)
    json_saver.save_to_json(second_closing_result, "second_closing_prompt.json",custom_folder=prompt_folder)

    last5matches_result = prompt_generator.prompt_for_last5matches(last5matches_data)
    json_saver.save_to_json(last5matches_result, "last5matches_prompt.json",custom_folder=prompt_folder)

    match_stats_result = prompt_generator.prompt_for_match_stats(match_stats_data)
    json_saver.save_to_json(match_stats_result, "match_stats_prompt.json",custom_folder=prompt_folder)

    odds_result = prompt_generator.prompt_for_odds(odds_data)
    json_saver.save_to_json(odds_result, "odds_prompt.json",custom_folder=prompt_folder)

    team_info_result = prompt_generator.prompt_for_team_info(team_info_data)
    json_saver.save_to_json(team_info_result, "team_info_prompt.json",custom_folder=prompt_folder)

    match_result_prompt = prompt_generator.prompt_for_match_result(game_results)
    json_saver.save_to_json(match_result_prompt, "match_result_prompt.json",custom_folder=prompt_folder)

    second_video_result = prompt_generator.generate_second_video_narration(
        intro_result= second_intro_result,
        team_info_result= team_info_result,
        match_stats_result= match_stats_result,
        odds_result= odds_result,
        last5matches_result= last5matches_result,
        match_result_prompts = match_result_prompt,
        closing_result= second_closing_result
    )
    json_saver.save_to_json(second_video_result, "second_video_narration.json", custom_folder=narration_folder)
