import librosa
import logging
from typing import Literal, List, Optional, Union
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AudioCheckResult(BaseModel):
    is_valid: bool
    errors: List[str] = []

class TaskParameterModel(BaseModel):
    min_duration: float  # or int, depending on your data type
    max_duration: float  # or int
    language: str
    expected_format: str = "oga"
    sample_rate: int = 42000
    bit_depth: int = 32
    try_enhance: Optional[int] = None  # Optional, default to None if not provided

def check_audio_file_format(
    file_path: str, 
    expected_format: Union[Literal['mp3', 'wav', 'flac', 'm4a', 'ogg', 'aac', 'oga'], None] = None
) -> dict:
    """
    Check if the audio file format is supported and matches the expected format.

    Args:
        file_path (str): Path to the audio file.
        expected_format (Literal or None): Expected audio format without dot. 
            If None, any supported format is accepted.

    Returns:
        dict: {
            'is_valid': bool,
            'actual_format': str or None
        }
    """
    supported_formats = ['mp3', 'wav', 'flac', 'm4a', 'ogg', 'aac', 'oga']

    # Extract actual extension without leading dot, lowercase
    actual_ext = file_path.lower().split('.')[-1] if '.' in file_path else None

    # Check if format is supported
    is_supported = actual_ext in supported_formats

    if not is_supported:
        return {
            'is_valid': False,
            'actual_format': actual_ext
        }

    # If expected_format is None, accept any supported format
    if expected_format is None:
        return {
            'is_valid': True,
            'actual_format': actual_ext
        }

    # Check if actual format matches expected
    is_valid = actual_ext == expected_format.lower()

    return {
        'is_valid': is_valid,
        'actual_format': actual_ext
    }


def check_audio_file_length(file_path: str, min_length: float = 0.5, max_length: float = 60.0) -> dict:
    """
    Check if the audio file length is within the specified range.

    Args:
        file_path (str): Path to the audio file.
        min_length (float): Minimum length in seconds.
        max_length (float): Maximum length in seconds.

    Returns:
        dict: {
            'is_valid': bool,
            'actual_length': float or None
        }
    """
    try:
        y, sr = librosa.load(file_path, sr=None)  # Load the audio file to check its length
        duration = librosa.get_duration(y=y, sr=sr)  # Get the duration in seconds

        logger.info(f"Checking audio file length for {file_path} between {min_length} and {max_length} seconds. Actual length: {duration} seconds.")

        is_valid = min_length <= duration <= max_length
        return {'is_valid': is_valid, 'actual_length': duration}
    except Exception as e:
        print(f"Error checking audio length: {e}")
        return {'is_valid': False, 'actual_length': None}

def check_audio_sample_rate(file_path: str, expected_sample_rate: int = 16000) -> dict:
    """
    Check if the audio sample rate matches the expected sample rate.

    Args:
        file_path (str): Path to the audio file.
        expected_sample_rate (int): Expected sample rate in Hz.

    Returns:
        dict: {
            'is_valid': bool,
            'actual_sample_rate': int or None
        }
    """
    try:
        y, sr = librosa.load(file_path, sr=None)
        is_valid = sr == expected_sample_rate
        return {'is_valid': is_valid, 'actual_sample_rate': sr}
    except Exception as e:
        print(f"Error checking sample rate: {e}")
        return {'is_valid': False, 'actual_sample_rate': None}


def check_audio_bit_depth(file_path: str, expected_bit_depth: int = 16) -> dict:
    """
    Check if the audio bit depth matches the expected bit depth.

    Args:
        file_path (str): Path to the audio file.
        expected_bit_depth (int): Expected bit depth (e.g., 16 for 16-bit PCM).

    Returns:
        dict: {
            'is_valid': bool,
            'actual_bit_depth': int or None
        }
    """
    try:
        y, sr = librosa.load(file_path, sr=None)

        # Map numpy dtype to bit depth
        dtype_to_bit_depth = {
            'float32': 32,
            'float64': 64,
            'int16': 16,
            'int32': 32,
        }

        # librosa loads audio as float32 by default, so we may need to infer differently
        actual_dtype = y.dtype.name

        # Get bit depth from dtype
        actual_bit_depth = dtype_to_bit_depth.get(actual_dtype, None)

        # Since librosa normalizes PCM data to float32, bit depth detection may not be precise
        # You might want to use other libraries like soundfile to get bit depth accurately
        is_valid = (actual_bit_depth == expected_bit_depth)

        return {'is_valid': is_valid, 'actual_bit_depth': actual_bit_depth}

    except Exception as e:
        print(f"Error checking audio bit depth: {e}")
        return {'is_valid': False, 'actual_bit_depth': None}

def check_audio_parameter(path: str, parameters: TaskParameterModel) -> AudioCheckResult:
    no_error = True
    errors = []

    file_length_result = check_audio_file_length(
        file_path=path, 
        min_length=parameters.min_duration, 
        max_length=parameters.max_duration
    )

    if not file_length_result['is_valid']:
        no_error = False
        errors.append(
            f"Audio length error: expected between {parameters.min_duration} and {parameters.max_duration}, "
            f"but got {file_length_result['actual_length']}."
        )

    file_format_result = check_audio_file_format(
        file_path=path, 
        expected_format=parameters.expected_format
    )
    if not file_format_result['is_valid']:
        no_error = False
        errors.append(
            f"Audio format error: expected '{parameters.expected_format}', "
            f"but got '{file_format_result['actual_format']}'."
        )

    sample_rate_result = check_audio_sample_rate(
        file_path=path, 
        expected_sample_rate=parameters.sample_rate  # fixed from your code, was mistakenly parameters.expected_format
    )
    if not sample_rate_result['is_valid']:
        no_error = False
        errors.append(
            f"Sample rate error: expected {parameters.sample_rate} Hz, "
            f"but got {sample_rate_result['actual_sample_rate']} Hz."
        )

    audio_bit_depth_result = check_audio_bit_depth(
        file_path=path, 
        expected_bit_depth=parameters.bit_depth  # assuming your parameter name is bit_rate not bit_depth
    )
    if not audio_bit_depth_result['is_valid']:
        no_error = False
        errors.append(
            f"Bit depth error: expected {parameters.bit_depth} bits, "
            f"but got {audio_bit_depth_result['actual_bit_depth']} bits."
        )

    return AudioCheckResult(
        is_valid=no_error,
        errors=errors,
    )
   

if __name__ == "__main__":
    import os
    import sys
    import logging

    logging.basicConfig(level=logging.INFO)

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