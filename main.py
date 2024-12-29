import os
import glob
import cv2  # OpenCV library for video processing
from PIL import Image  # Pillow library for palette-based images
from pyktok import specify_browser, save_tiktok

# Step 1: Define the folder containing main.py
script_folder = os.path.dirname(os.path.abspath(__file__))  # Get the folder of main.py
frame_folder = os.path.join(script_folder, "frames")        # Folder to store extracted frames
raw_data_folder = os.path.join(script_folder, "raw_data")   # Folder to store raw binary data

# Step 2: Define the TikTok video URL
video_url = "https://www.tiktok.com/@chllxedits/video/7452726325628128520?is_from_webapp=1&sender_device=pc&web_id=7453276693018314256"  # Define TikTok URL

# Step 3: Clean up all previous files before starting
print("Cleaning up previous files...")

# Delete all PBM and raw files in the frames and raw_data folders
for folder, extension in [(frame_folder, "*.pbm"), (raw_data_folder, "*.bin")]:
    if os.path.exists(folder):
        files = glob.glob(os.path.join(folder, extension))
        for file in files:
            try:
                os.remove(file)
                print(f"Deleted file: {file}")
            except Exception as e:
                print(f"Error deleting file {file}: {e}")

        # Delete the folder if empty
        if not os.listdir(folder):
            os.rmdir(folder)
            print(f"Deleted empty folder: {folder}")

print("Cleanup complete.")

# Step 4: Ensure the frame and raw_data folders exist
os.makedirs(frame_folder, exist_ok=True)
os.makedirs(raw_data_folder, exist_ok=True)

# Step 5: Download the TikTok video
try:
    # Download the video
    specify_browser("chrome")  # Specify the browser for cookie extraction
    save_tiktok(video_url, save_video=True, metadata_fn='', browser_name=None)
    print("Downloaded TikTok video successfully!")
except Exception as e:
    print(f"An error occurred during TikTok video download: {e}")

# Step 6: Process any .mp4 files in the directory
mp4_files = glob.glob(os.path.join(script_folder, "*.mp4"))
if not mp4_files:
    print("No .mp4 files found in the folder.")
else:
    for video_filepath in mp4_files:
        print(f"Processing video: {video_filepath}")

        try:
            # Open the video file
            video = cv2.VideoCapture(video_filepath)

            # Get video properties
            fps = video.get(cv2.CAP_PROP_FPS)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            start_time = max(0, duration - 9)  # Start 9 seconds from the end
            start_frame = int(start_time * fps)

            # OLED resolution
            oled_width = 128
            oled_height = 64

            frame_count = 0
            video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)  # Set to start frame

            while True:
                ret, frame = video.read()
                if not ret:
                    break

                # Resize the frame to fit OLED resolution
                resized_frame = cv2.resize(frame, (oled_width, oled_height))

                # Convert to grayscale
                grayscale_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

                # Convert to indexed color (1-bit palette)
                pil_image = Image.fromarray(grayscale_frame)
                bw_image = pil_image.convert("1")  # Convert to black and white (1-bit)

                # Save the frame as a PBM image
                pbm_path = os.path.join(frame_folder, f"{os.path.splitext(os.path.basename(video_filepath))[0]}_frame_{frame_count:04d}.pbm")
                bw_image.save(pbm_path, "PPM")
                print(f"Saved frame as PBM: {pbm_path}")

                # Save the raw binary data
                raw_path = os.path.join(raw_data_folder, f"{os.path.splitext(os.path.basename(video_filepath))[0]}_frame_{frame_count:04d}.bin")
                with open(raw_path, 'wb') as raw_file:
                    raw_file.write(bw_image.tobytes())
                print(f"Saved raw binary data: {raw_path}")

                frame_count += 1

            video.release()
            print(f"Extracted {frame_count} frames from {video_filepath} and resized them for OLED.")
        except Exception as e:
            print(f"An error occurred while processing {video_filepath}: {e}")
