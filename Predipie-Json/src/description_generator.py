import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

class MatchDescriptionGenerator:
    """Generates match description using the ChatGPT API"""
    
    def __init__(self, model="gpt-4-turbo", max_tokens=50):
        self.model = model
        self.max_tokens = max_tokens
        self.system_message = "You are an AI assistant helping to create dynamic football video scripts."

    def generate_description(self, i, host_team, guest_team):
        """Generates a description for a specific match based on team names and order."""
        intro = self._get_intro(i, host_team, guest_team)
        prompt = (
            f"{intro} Create a brief, dynamic match description under 80 characters, "
            f"using only these punctuation marks: dot, comma, exclamation mark, question mark, and semicolon. "
            "Important: Do not mention any game statistics, player names, or game history information."
        )

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens
            )
            return response['choices'][0]['message']['content'].strip()
        except openai.error.OpenAIError as e:
            print(f"OpenAI API error: {e}")
            return "Description generation failed."

    def _get_intro(self, i, host_team, guest_team):
        """Determines the introduction phrase based on match order."""
        if i == 1:
            return f"Let's start with the first match: {host_team} versus {guest_team}."
        elif i in [2, 3, 4]:
            ordinal = {2: "second", 3: "third", 4: "fourth"}[i]
            return f"Let's continue with the {ordinal} match: {host_team} against {guest_team}."
        else:
            return f"And the last match: {host_team} versus {guest_team}."
