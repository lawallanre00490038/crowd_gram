import librosa
from typing import Literal

def check_audio_file_format(file_path: str, expected_format = Literal['mp3', 'wav', 'flac', '.m4a', '.ogg', '.aac', None]) -> bool:
    """Check if the audio file format is supported.
    
    Args:
        file_path (str): Path to the audio file.
        expected_format (Literal['mp3', 'wav', 'flac', None]): Expected audio format. If None, any format is accepted.
    Returns:    
        bool: True if the file format is supported, False otherwise.
    """

    supported_formats = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac']

    if any(file_path.lower().endswith(ext) for ext in supported_formats):
        if expected_format is None:
            return True
        return file_path.lower().endswith(f".{expected_format}")
    else:
        if expected_format is None:
            return False
        # Check if the file has the expected format
        return file_path.lower().endswith(f".{expected_format}")
    
def check_audio_file_length(file_path: str, min_length: float = 0.5, max_length: float = 60.0) -> bool:
    """Check if the audio file length is within the specified range.
    
    Args:
        file_path (str): Path to the audio file.
        min_length (float): Minimum length in seconds.
        max_length (float): Maximum length in seconds.
    
    Returns:
        bool: True if the audio length is within the range, False otherwise.
    """
    try:
        duration = librosa.get_duration(filename=file_path)
        return min_length <= duration <= max_length
    except Exception as e:
        print(f"Error checking audio length: {e}")
        return False
    
def check_audio_sample_rate(file_path: str, expected_sample_rate: int = 16000) -> bool:
    """Check if the audio sample rate matches the expected sample rate.
    
    Args:
        file_path (str): Path to the audio file.
        expected_sample_rate (int): Expected sample rate in Hz.
    
    Returns:
        bool: True if the sample rate matches, False otherwise.
    """
    try:
        y, sr = librosa.load(file_path, sr=None)
        return sr == expected_sample_rate
    except Exception as e:
        print(f"Error checking audio sample rate: {e}")
        return False
    
def check_audio_bit_depth(file_path: str, expected_bit_depth: int = 16) -> bool:
    """Check if the audio bit depth matches the expected bit depth.
    
    Args:
        file_path (str): Path to the audio file.
        expected_bit_depth (int): Expected bit depth (e.g., 16 for 16-bit PCM).
    
    Returns:
        bool: True if the bit depth matches, False otherwise.
    """
    try:
        y, sr = librosa.load(file_path, sr=None)
        if y.dtype == 'float32':
            return expected_bit_depth == 32
        elif y.dtype == 'int16':
            return expected_bit_depth == 16
        else:
            return False
    except Exception as e:
        print(f"Error checking audio bit depth: {e}")
        return False
    

if __name__ == "__main__":
    import os
    import sys
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    tests = {
        "1": "Check audio file format",
        "2": "Check audio file length",
        "3": "Check audio sample rate",
        "4": "Check audio bit depth"
    }

    print("Available tests:")
    for key, val in tests.items():
        print(f"{key}. {val}")

    choice = input("\nSelect a test by entering the corresponding number: ").strip()

    if choice not in tests:
        print("Invalid selection.")
        sys.exit(1)

    file_path = input("Enter the path to the audio file: ").strip()
    if not os.path.exists(file_path):
        print("File not found.")
        sys.exit(1)

    if choice == "1":
        expected_format = input("Enter expected format (mp3, wav, flac, m4a, ogg, aac) or leave blank for any: ").strip().lower()
        expected_format = expected_format if expected_format in ['mp3', 'wav', 'flac', 'm4a', 'ogg', 'aac'] else None
        result = check_audio_file_format(file_path, expected_format)

    elif choice == "2":
        try:
            min_length = float(input("Enter minimum length in seconds (default 0.5): ") or 0.5)
            max_length = float(input("Enter maximum length in seconds (default 60.0): ") or 60.0)
        except ValueError:
            print("Invalid number entered.")
            sys.exit(1)

        logger.info(f"Checking audio file length between {min_length} and {max_length} seconds.")
        result = check_audio_file_length(file_path, min_length, max_length)

    elif choice == "3":
        try:
            expected_sr = int(input("Enter expected sample rate (default 16000): ") or 16000)
        except ValueError:
            print("Invalid number entered.")
            sys.exit(1)
        result = check_audio_sample_rate(file_path, expected_sr)

    elif choice == "4":
        try:
            expected_bd = int(input("Enter expected bit depth (16 or 32, default 16): ") or 16)
        except ValueError:
            print("Invalid number entered.")
            sys.exit(1)
        result = check_audio_bit_depth(file_path, expected_bd)

    print(f"\nResult: {'PASS ✅' if result else 'FAIL ❌'}")