import librosa
from typing import Literal

def check_audio_file_format(file_path: str, expected_format = Literal['mp3', 'wav', 'flac', 'm4a', None]) -> bool:
    """Check if the audio file format is supported.
    
    Args:
        file_path (str): Path to the audio file.
        expected_format (Literal['mp3', 'wav', 'flac', None]): Expected audio format. If None, any format is accepted.
    Returns:    
        bool: True if the file format is supported, False otherwise.
    """

    supported_formats = ['.mp3', '.wav', '.flac']

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
    import argparse

    parser = argparse.ArgumentParser(description="Check audio file format.")
    parser.add_argument("--file_path", type=str, required=True, help="Path to the audio file")
    parser.add_argument("--expected_format", type=str, choices=['mp3', 'wav', 'flac', 'm4a', None], default=None, help="Expected audio format")

    args = parser.parse_args()

    result = check_audio_file_format(args.file_path, args.expected_format)
    print("Audio file format check passed?" , result)