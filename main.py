import os
import glob
import cv2  # OpenCV library for video processing
from PIL import Image  # Pillow library for image processing
from pyktok import specify_browser, save_tiktok
from tqdm import tqdm  # For displaying progress bars

# [32mPrompt the user for the TikTok video URL[0m
video_url = input("[32mPlease enter the TikTok video URL:[0m ").strip()

if not video_url:
    print("[32mNo URL provided. Exiting the program.[0m")
    exit()

# Define directories
script_folder = os.path.dirname(os.path.abspath(__file__))
frame_folder = os.path.join(script_folder, "frames")
raw_data_folder = os.path.join(script_folder, "raw_data")

# [32mClean up old files in specified folders[0m
def clean_folder(folder, extension):
    if os.path.exists(folder):
        files = glob.glob(os.path.join(folder, extension))
        for file in tqdm(files, desc=f"[1mCleaning {folder}[0m", unit="file"):
            os.remove(file)
        if not os.listdir(folder):
            os.rmdir(folder)

print("[32mCleaning up old files...[0m")
clean_folder(frame_folder, "*.pbm")
clean_folder(raw_data_folder, "*.bin")

# Ensure directories exist
os.makedirs(frame_folder, exist_ok=True)
os.makedirs(raw_data_folder, exist_ok=True)

# [32mDownload TikTok video[0m
try:
    print("[32mDownloading TikTok video...[0m")
    specify_browser("chrome")
    save_tiktok(video_url, save_video=True)
    print("[32mTikTok video downloaded successfully.[0m")
except Exception as e:
    print(f"[32mError downloading TikTok video:[0m {e}")
    exit()

# Process MP4 videos in the script folder
mp4_files = glob.glob(os.path.join(script_folder, "*.mp4"))
if not mp4_files:
    print("[32mNo MP4 videos found to process.[0m")
    exit()

for video_path in mp4_files:
    print(f"[32mProcessing video:[0m [1m{os.path.basename(video_path)}[0m")

    try:
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps

        # Start processing 9 seconds from the end if possible
        start_frame = max(0, int((duration - 9) * fps))
        video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        frame_count = 0
        oled_resolution = (128, 64)

        with tqdm(total=total_frames - start_frame, desc="[32mExtracting frames[0m", unit="frame") as pbar:
            while True:
                ret, frame = video.read()
                if not ret:
                    break

                # Prepare the frame for OLED display
                resized_frame = cv2.resize(frame, oled_resolution)
                grayscale_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
                bw_image = Image.fromarray(grayscale_frame).convert("1")

                # Save the PBM image and raw binary data
                frame_base = f"{os.path.splitext(os.path.basename(video_path))[0]}_frame_{frame_count:04d}"
                pbm_path = os.path.join(frame_folder, f"{frame_base}.pbm")
                raw_path = os.path.join(raw_data_folder, f"{frame_base}.bin")

                bw_image.save(pbm_path, "PPM")
                with open(raw_path, "wb") as raw_file:
                    raw_file.write(bw_image.tobytes())

                frame_count += 1
                pbar.update(1)

        video.release()
        print(f"[32mExtracted {frame_count} frames from[0m [1m{os.path.basename(video_path)}[0m.")

    except Exception as e:
        print(f"[32mError processing video {os.path.basename(video_path)}:[0m {e}")
