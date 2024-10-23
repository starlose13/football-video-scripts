from PIL import Image, ImageDraw, ImageFont


def generate_match_image(match_data, match_number):
    img = Image.open("./assets/match-template.png")
    draw = ImageDraw.Draw(img)

    font_path = "arial.ttf"
    font_team = ImageFont.truetype(font_path, 32)
    font_league = ImageFont.truetype(font_path, 30)
    font_details = ImageFont.truetype(font_path, 32)

    home_team_name = match_data['home_team']
    away_team_name = match_data['away_team']
    league = match_data['league']
    stadium = match_data['stadium']
    day = match_data['day']
    time = match_data['time']

    draw.text((320, 615), home_team_name, fill="white", font=font_team)
    draw.text((img.width - 630, 615), away_team_name, fill="white", font=font_team)
    draw.text((img.width - 1140, 425), league, fill="white", font=font_league)
    draw.text((img.width - 1140, 845), f"{day} {time}", fill="white", font=font_details)
    draw.text((img.width - 1140, 950), stadium, fill="white", font=font_details)

    output_path = f"output_{home_team_name}_vs_{away_team_name}.png"
    img.save(output_path)
    print(f"Generated image for match {match_number} at {output_path}")
    return output_path  # Return the local image path