import subprocess
import time

# List of scripts to run in order
scripts = [
    "secondEpisodeJsonCreator.py",
    "thirdEpisodeJsonCreator.py",
    "fourthEpisodeJsonCreator.py",
    "fifthEpisodeJsonCreator.py",
    "sixEpisodeJsonCreator.py",
    "oneFileAvatarAudioCreator.py",
    "ImageSequenceFiller.py",
    "upload-video-on-creatify.py",
    "FeedAIVideo.py"
]

# Function to run a script and retry if it fails
def run_script(script_name, retry_interval=10):
    while True:
        try:
            print(f"Running {script_name}...")
            subprocess.run(["python", script_name], check=True)
            print(f"{script_name} completed successfully.")
            break  # Exit loop if the script ran successfully
        except subprocess.CalledProcessError:
            print(f"Error in {script_name}. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)

# Run each script in sequence
for i, script in enumerate(scripts):
    run_script(script)
    
    # Special 15-minute wait between the seventh and eighth script
    if i == 6:  # After ImageSequenceFiller.py
        print("Waiting 45 minutes before running the next script...")
        time.sleep(45 * 60)

print("All scripts completed successfully.")
