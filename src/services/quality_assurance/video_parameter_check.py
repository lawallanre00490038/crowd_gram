import cv2
from typing import Literal

def check_video_file_format(file_path: str, expected_format: Literal['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', None] = None) -> bool:
    """Check if the video file format is supported.
    
    Args:
        file_path (str): Path to the video file.
        expected_format (Literal['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', None]): 
            Expected video format. If None, any supported format is accepted.
    
    Returns:    
        bool: True if the file format is supported or matches expected_format, False otherwise.
    """

    supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']

    file_path = file_path.lower()

    if any(file_path.endswith(ext) for ext in supported_formats):
        if expected_format is None:
            return True
        return file_path.endswith(f".{expected_format}")
    else:
        if expected_format is None:
            return False
        return file_path.endswith(f".{expected_format}")

def check_video_file_length(file_path: str, min_length: float = 0.5, max_length: float = 600.0) -> bool:
    """Check if the video file length is within the specified range using OpenCV.
    
    Args:
        file_path (str): Path to the video file.
        min_length (float): Minimum length in seconds.
        max_length (float): Maximum length in seconds.
    
    Returns:
        bool: True if the video length is within the range, False otherwise.
    """
    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            print(f"Error: Unable to open video file: {file_path}")
            return False

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        if fps == 0:
            print("Error: FPS is zero, can't calculate duration.")
            return False

        duration = frame_count / fps
        cap.release()

        return min_length <= duration <= max_length
    except Exception as e:
        print(f"Error checking video length: {e}")
        return False
    
def check_video_frame_rate(file_path: str, expected_frame_rate: float = 30.0) -> bool:
    """Check if the video frame rate matches the expected frame rate.
    
    Args:
        file_path (str): Path to the video file.
        expected_frame_rate (float): Expected frame rate (e.g., 30.0 for 30 FPS).
    
    Returns:
        bool: True if the frame rate matches, False otherwise.
    """
    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            print(f"Error: Unable to open video file: {file_path}")
            return False

        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()

        # Allow for small rounding errors in FPS detection
        return abs(fps - expected_frame_rate) < 0.5
    except Exception as e:
        print(f"Error checking video frame rate: {e}")
        return False
    
def check_video_bit_depth(file_path: str, expected_bit_depth: int = 8) -> bool:
    """Check if the video bit depth (per channel) matches the expected bit depth.
    
    Args:
        file_path (str): Path to the video file.
        expected_bit_depth (int): Expected bit depth (commonly 8 or 10).
    
    Returns:
        bool: True if the bit depth matches, False otherwise.
    """
    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            print(f"Error: Unable to open video file: {file_path}")
            return False

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("Error: Couldn't read a frame.")
            return False

        # Check dtype of the frame array
        if frame.dtype == 'uint8':
            return expected_bit_depth == 8
        elif frame.dtype == 'uint16':
            return expected_bit_depth == 10 or expected_bit_depth == 16  # Approximate match
        else:
            print(f"Unrecognized dtype: {frame.dtype}")
            return False
    except Exception as e:
        print(f"Error checking video bit depth: {e}")
        return False
    