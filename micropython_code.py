from machine import I2C, Pin
from sh1106 import SH1106_I2C
import framebuf
import os
import time

# OLED display dimensions
WIDTH = 128
HEIGHT = 64

# Initialize I2C and OLED display
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=200000)
oled = SH1106_I2C(WIDTH, HEIGHT, i2c)
oled.rotate(True)
oled.fill(0)
oled.text("PBM Viewer", 0, 0)
oled.show()

def read_pbm(file_path):
    """
    Reads a P4 PBM (binary) file and extracts bitmap data.
    Returns the width, height, and raw bitmap data.
    """
    with open(file_path, "rb") as f:
        # Read the header
        header = f.readline().strip()
        if header != b"P4":
            raise ValueError("Invalid PBM file. Expected P4 format.")
        
        # Read dimensions
        while True:
            line = f.readline().strip()
            if not line.startswith(b"#"):  # Skip comments
                dimensions = line
                break
        width, height = map(int, dimensions.split())

        # Read bitmap data
        raw_data = f.read()
        return width, height, raw_data

# Directory containing PBM files
frame_folder = "/frames"

try:
    # List all PBM files in the frame folder
    pbm_files = [f for f in os.listdir(frame_folder) if f.endswith(".pbm")]
    if not pbm_files:
        raise FileNotFoundError("No PBM files found in the frames folder.")

    current_frame = [0]  # Use a mutable list for the current frame
    total_frames = len(pbm_files)

    def display_frame():
        try:
            pbm_file = pbm_files[current_frame[0]]
            file_path = frame_folder + "/" + pbm_file

            # Read the PBM file
            width, height, bitmap_data = read_pbm(file_path)

            # Validate dimensions
            if width != WIDTH or height != HEIGHT:
                raise ValueError(f"PBM dimensions ({width}x{height}) do not match OLED ({WIDTH}x{HEIGHT})")

            # Create a framebuffer from the bitmap data
            fb = framebuf.FrameBuffer(bytearray(bitmap_data), WIDTH, HEIGHT, framebuf.MONO_HLSB)

            # Display the PBM image on the OLED without clearing
            oled.blit(fb, 0, 0)
            oled.show()

            print(f"Displayed PBM file: {pbm_file}")

            # Move to the next frame
            current_frame[0] = (current_frame[0] + 1) % total_frames
        except Exception as e:
            oled.fill(0)
            oled.text("Error!", 0, 0)
            oled.text(str(e), 0, 10)
            oled.show()
            print(f"Error: {e}")

    # Display frames at 30Hz (approximately 33ms per frame)
    while True:
        start_time = time.ticks_ms()
        display_frame()
        elapsed_time = time.ticks_ms() - start_time
        if elapsed_time < 33:
            time.sleep_ms(33 - elapsed_time)

except Exception as e:
    oled.fill(0)
    oled.text("Error!", 0, 0)
    oled.text(str(e), 0, 10)
    oled.show()
    print(f"Error: {e}")
