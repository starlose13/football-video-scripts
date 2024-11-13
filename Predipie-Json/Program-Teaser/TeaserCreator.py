import json
import copy

# Define the dynamic values in Python
background_color = "#ffffff"
soundtrack_src = "https://templates.shotstack.io/basic/asset/audio/music/unminus/please-wait.mp3"
soundtrack_effect = "fadeOut"

video_src = "https://shotstack-ingest-api-v1-sources.s3.ap-southeast-2.amazonaws.com/zfe0a140fc/zzy9g4kl-4cs6-z73f-ljmn-3xwjbt3mwa2b/source.mov"
video_start = 0
video_length = 16
video_opacity = 0.6

text_content = "PrediPie"
text_color = "#e31116"
text_size = 200
text_start = 8.11
text_length = 7.89
text_effect = "zoomIn"
# image https://shotstack-ingest-api-v1-sources.s3.ap-southeast-2.amazonaws.com/4c7kem3rad/zzz01jcg-hb84j-h4c5z-k6cnd-zw6mbq/source.png
# vertical logo : https://shotstack-ingest-api-v1-sources.s3.ap-southeast-2.amazonaws.com/4c7kem3rad/zzz01jcg-hde4s-jm1vk-hajzv-wnjdxt/source.png
# horizontal logo : https://shotstack-ingest-api-v1-sources.s3.ap-southeast-2.amazonaws.com/4c7kem3rad/zzz01jcg-henxb-5r7wb-17ch7-r90v3j/source.png
merge_vertical_image = "https://shotstack-ingest-api-v1-sources.s3.ap-southeast-2.amazonaws.com/zfe0a140fc/zzy9g59m-1xqn-tx3b-pbqi-1ejhet0xh2wx/source.jpg"
merge_horizontal_image = "https://shotstack-ingest-api-v1-sources.s3.ap-southeast-2.amazonaws.com/zfe0a140fc/zzy9g74h-0xnr-km3q-cugf-4ohd2v4povfg/source.jpg"
merge_primary_image = "https://shotstack-ingest-api-v1-sources.s3.ap-southeast-2.amazonaws.com/4c7kem3rad/zzz01jcg-hb84j-h4c5z-k6cnd-zw6mbq/source.png"

# Load the JSON template
with open('TeaserTemplate.json', 'r') as template_file:
    json_data = json.load(template_file)

# Function to update the JSON data with dynamic values
def update_json_data(data):
    # Update general settings
    data["timeline"]["background"] = background_color
    data["timeline"]["soundtrack"]["src"] = soundtrack_src
    data["timeline"]["soundtrack"]["effect"] = soundtrack_effect

    # Update video clip details
    video_clip = data["timeline"]["tracks"][0]["clips"][0]
    video_clip["asset"]["src"] = video_src
    video_clip["start"] = video_start
    video_clip["length"] = video_length
    video_clip["opacity"] = video_opacity

    # Update text clip details
    text_clip = data["timeline"]["tracks"][1]["clips"][0]
    text_clip["asset"]["text"] = text_content
    text_clip["asset"]["font"]["color"] = text_color
    text_clip["asset"]["font"]["size"] = text_size
    text_clip["start"] = text_start
    text_clip["length"] = text_length
    text_clip["effect"] = text_effect

    # Update merge placeholders
    #data["merge"][0]["replace"] = merge_vertical_image
    #data["merge"][1]["replace"] = merge_horizontal_image
    data["merge"][2]["replace"] = merge_primary_image

    return data

# Create a modified copy of the JSON data
updated_json_data = update_json_data(copy.deepcopy(json_data))

# Save the modified JSON to a new file
output_file_path = "dynamic_output.json"
with open(output_file_path, 'w') as output_file:
    json.dump(updated_json_data, output_file, indent=4)

print(f"Dynamic JSON file created successfully at {output_file_path}")
