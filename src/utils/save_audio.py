import numpy as np
from pydub import AudioSegment


def save_librosa_audio_as_mp3(y, sr, output_path, bitrate="256k"):
    """
    Save audio loaded with librosa (y, sr) as an MP3 file.

    Args:
        y (np.ndarray): Audio time series.
        sr (int): Sampling rate.
        output_path (str): Path to save MP3 file.
        bitrate (str): Bitrate for MP3 file (default: '192k').
    """
    # Normalize to 16-bit PCM and convert to bytes
    audio_int16 = np.int16(y / np.max(np.abs(y)) * 32767)
    audio_bytes = audio_int16.tobytes()

    # Create an in-memory WAV file
    wav_audio = AudioSegment(
        data=audio_bytes,
        sample_width=2,       # 16-bit PCM
        frame_rate=sr,
        channels=1 if y.ndim == 1 else y.shape[0]
    )
    wav_audio.export(output_path, format="mp3", bitrate=bitrate)
