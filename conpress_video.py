import os
import subprocess
from loguru import logger

# Paths
input_folder = 'videos'
output_folder = 'compressed'

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through videos
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f"compressed_{filename}")

        logger.info(f"Compressing: {filename}")

        # FFmpeg command
        command = [
            'ffmpeg',
            '-i', input_path,
            '-vcodec', 'libx264',
            '-crf', '28',  # Adjust this value if needed
            '-preset', 'slow',
            '-acodec', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            output_path
        ]

        # Run command
        subprocess.run(command, check=True)

logger.info("✅ Compression complete! Check 'compressed/' folder.")
