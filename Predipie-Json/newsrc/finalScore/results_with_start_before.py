from dataClassifier.game_result_predictor import GameResultPredictor
from config.config import START_BEFORE
import os

def main():
    output_folder = f"{START_BEFORE}_json_match_output_folder"
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    predictor = GameResultPredictor(start_date=START_BEFORE, output_folder=output_folder)
    results = predictor.predict_game_results()
    print("Game results have been saved successfully.")

if __name__ == "__main__":
    main()
