import json

# Paths to the scene and template files
scene_dir_template = './scene{scene_num}/match_{match_num}.json'
assemble_video_path = 'jsonTemplateShotStackAPI.json'

# Load the assemble-video JSON file
with open(assemble_video_path, 'r') as assemble_file:
    assemble_data = json.load(assemble_file)

# Function to get reading_time from scene files
def get_reading_time(scene_num, match_num):
    scene_file_path = scene_dir_template.format(scene_num=scene_num, match_num=match_num)
    try:
        with open(scene_file_path, 'r') as scene_file:
            scene_data = json.load(scene_file)
            return scene_data.get('reading_time')
    except FileNotFoundError:
        print(f"Warning: {scene_file_path} not found.")
        return None

# Function to update lengths and calculate start times in assemble_data
def update_lengths_and_starts():
    image_index = 0  # Start with IMAGE_0
    previous_start = 0  # Initial start time for IMAGE_0
    previous_length = 0  # Initial length for IMAGE_0
    
    # Get the reading time for IMAGE_1 (first image in sequence) to calculate IMAGE_0 length
    reading_time_image_1 = get_reading_time(2, 1)  # match_1, scene2 for IMAGE_1
    length_image_0 = reading_time_image_1 - 0.01 if reading_time_image_1 else 0

    # Locate IMAGE_0 in JSON and set its start and length
    for track in assemble_data['timeline']['tracks']:
        for clip in track['clips']:
            if clip['asset']['src'] == "{{ IMAGE_0 }}":
                clip['start'] = previous_start  # start of IMAGE_0
                clip['length'] = length_image_0  # length of IMAGE_0
                print(f"Updated IMAGE_0 - start: {clip['start']}, length: {clip['length']}")
                previous_start = length_image_0  # Update start for IMAGE_1
                previous_length = length_image_0  # Update length for IMAGE_1 start calculation
                image_index += 1
                break  # Move to IMAGE_1 after updating IMAGE_0

    # Start from IMAGE_1 and continue for IMAGE_1 to IMAGE_26 as before
    for match_num in range(1, 6):  # match_1 to match_5
        for scene_num in range(2, 7):  # scene2 to scene6
            reading_time = get_reading_time(scene_num, match_num)
            if reading_time is not None:
                # Locate the clip with src "{{ IMAGE_X }}" in the JSON data
                for track in assemble_data['timeline']['tracks']:
                    for clip in track['clips']:
                        if clip['asset']['src'] == f"{{{{ IMAGE_{image_index} }}}}":
                            # Update 'length' with 'reading_time'
                            clip['length'] = reading_time
                            # Calculate and update 'start' based on previous clip's start and length
                            clip['start'] = previous_start
                            print(f"Updated IMAGE_{image_index} - start: {clip['start']}, length: {clip['length']}")
                            # Update previous start and length for next iteration
                            previous_start += reading_time  # Update start for the next IMAGE_X
                            previous_length = reading_time
                            image_index += 1
                            break  # Move to the next IMAGE_X after updating

# Run the update function
update_lengths_and_starts()

# Save the updated JSON to a new file
with open('assemble-video-updated.json', 'w') as output_file:
    json.dump(assemble_data, output_file, indent=4)

print("Updated assemble-video-updated.json with start and length for each IMAGE_X.")
