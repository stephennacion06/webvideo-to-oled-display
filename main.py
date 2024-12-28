import os
import glob
from pyktok import specify_browser, save_tiktok

# Step 1: Specify the browser for cookie extraction
specify_browser("chrome")  # Use your installed browser (e.g., "firefox", "edge", "chrome")

# Step 2: Define the TikTok video URL
video_url = "https://www.tiktok.com/@fredericogenciana18/video/7421187183911898388"

# Step 3: Define the destination folder
output_folder = "downloads"

# Step 4: Delete existing MP4 files in the folder
os.makedirs(output_folder, exist_ok=True)  # Ensure the folder exists
mp4_files = glob.glob(os.path.join(output_folder, "*.mp4"))  # Find all MP4 files in the folder

for file in mp4_files:
    try:
        os.remove(file)
        print(f"Deleted: {file}")
    except Exception as e:
        print(f"Error deleting file {file}: {e}")

# Step 5: Download the video
try:
    output_filepath = os.path.join(output_folder, "tiktok_video.mp4")  # Specify the filename
    save_tiktok(video_url, save_video=True, metadata_fn='', browser_name=None)
    print(f"Video downloaded successfully! Saved at {output_filepath}")
except Exception as e:
    print(f"An error occurred: {e}")
