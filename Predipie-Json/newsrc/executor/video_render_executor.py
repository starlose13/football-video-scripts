import time
from api.creatify_api import CreatifyAPI
from api.shotstack_api import ShotstackAPI
from utils.json_saver import JsonSaver

def main():
    # Get the latest video URL from Creatify
    video_url = CreatifyAPI.get_latest_video_url()
    if video_url:
        # Upload video to Shotstack
        render_id = ShotstackAPI.upload_video(video_url)
        if render_id:
            # Check rendering status periodically
            while True:
                status, final_video_url = ShotstackAPI.check_render_status(render_id)
                if status == "done":
                    print("Render complete. Video URL:", final_video_url)
                    saver = JsonSaver()
                    saver.save_to_json({"shotstack_video_url": final_video_url}, "shotstack_video_url.json")
                    break
                elif status == "failed":
                    print("Render failed.")
                    break
                else:
                    print("Render status:", status)
                    time.sleep(10)  # Wait 10 seconds before checking again
    else:
        print("No valid video URL available from Creatify; cannot proceed with Shotstack rendering.")

if __name__ == "__main__":
    main()
