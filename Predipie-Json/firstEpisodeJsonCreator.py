import requests
import json

# Define the API endpoint
url = 'https://dataprovider.predipie.com/api/v1/ai/test/'

try:
    # Send a GET request to the API
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes

    # Parse the JSON response
    data = response.json()

    # Filter out items based on specific conditions
    filtered_data = []
    unwanted_keys = {
        "id", "provider_match_id", "is_avaiable", "details", "status",
        "state", "match_state", "home_score_regular_time", "away_score_regular_time"
    }
    excluded_teams = {"01916a51-3a31-7db2-830e-0cce901d7bd2", "01916a56-9c67-7fa1-ac8b-51193c9efc4f"}

    for item in data:
        # Only include items that meet the specified conditions
        if item.get('match_state') == 1 and item.get('status') == 'not_started' and item.get('state') == 'not_started':
            # Filter out unwanted fields in each item
            filtered_item = {key: value for key, value in item.items() if key not in unwanted_keys}

            # Process 'team_related_match' to include only the relevant team data
            if 'team_related_match' in item:
                filtered_teams = []
                for team_data in item['team_related_match']:
                    # Filter team data based on excluded teams and necessary fields
                    if (team_data.get("team") not in excluded_teams) or ('rank' in team_data and 'point' in team_data):
                        relevant_team_data = {k: v for k, v in team_data.items() if k in {"team", "five_previous_matches", "rank", "point"}}
                        filtered_teams.append(relevant_team_data)
                
                filtered_item['team_related_match'] = filtered_teams

            # Ensure 'venue' is correctly populated
            if 'venue' in item and item['venue']:
                filtered_item['venue'] = item['venue']
            else:
                filtered_item['venue'] = None  # Explicitly set to None if 'venue' is missing or empty

            filtered_data.append(filtered_item)

    # Define the output file path and save the filtered data to a JSON file
    output_file = 'api_data.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=4)
        print(f"Filtered data successfully saved to {output_file}")
    except IOError as e:
        print(f"Error saving to file {output_file}: {e}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred with the API request: {e}")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON response: {e}")
