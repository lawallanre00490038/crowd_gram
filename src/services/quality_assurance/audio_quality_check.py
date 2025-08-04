import librosa 
from typing import Tuple, Dict
import numpy as np
import numpy as np
import noisereduce as nr
from pydub import AudioSegment
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


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

def reduce_noise(data, sr):
    '''Reduce the amount of noise in the Audio'''
    enhanced = nr.reduce_noise(
        y=data,
        sr=sr,
        stationary=False,
        time_constant_s = 3.5,  # 3.5
        freq_mask_smooth_hz = 300.0,  # 2000.0
        time_mask_smooth_ms = 100.0,  # 100.0
        thresh_n_mult_nonstationary = 0.5 # 1.0
    ) 

    return enhanced
def cal_signal_power(data):
    '''Calculate the signal power'''
    rms = librosa.feature.rms(y = data, frame_length=len(data), center=False) 

    # Convert RMS to dB
    rms_db = librosa.amplitude_to_db(rms)

    signal_power = np.mean(rms_db)

    return signal_power

def cal_noise_floor(data, sr):
    '''Calculate the noise power'''
    rms = librosa.feature.rms(y=data, frame_length= int(sr * 0.5), center=False)

    # Convert RMS to dB
    rms_db = librosa.amplitude_to_db(rms)

    noise_floor = np.min(rms_db)

    return noise_floor

def cal_silence_percentage(data, noise_floor):
    '''Calculate the noise percentage'''
    silence_threshold = librosa.db_to_amplitude(noise_floor - 5)

    silent_samples = np.sum(data < silence_threshold)

    total_samples = len(data)

    # Calculate percentage of silence
    silence_percentage = (silent_samples / total_samples) * 100

    return silence_percentage

def analyze_audio(data, sr):
    '''Get Analysis of the Audio'''
    noise_power = cal_noise_floor(data, sr = sr)
    signal_power = cal_signal_power(data)

    snr_value = signal_power - noise_power

    silence_percentage = cal_silence_percentage(data, noise_power)

    return {"snr": float(snr_value),
            "silence": float(silence_percentage),
            "noise_power": float(noise_power),
            "signal_power": float(signal_power)}


def check_audio_quality(
    data: np.ndarray,
    sr: int,
    try_enhance: int = 2,
    min_snr_value: float = 40,
    min_snr_value_edit: float = 30,
    min_speech_level: float = -10,
    max_speech_level: float = -30,
    min_noise_level: float = -40
) -> Tuple[np.ndarray, Dict[str, float | str]]:
    
    """
    Evaluates the quality of an audio signal and attempts enhancement if necessary.

    Parameters:
    -----------
    data : np.ndarray
        The audio waveform data.
    sr : int
        The sample rate of the audio signal.
    try_enhance : int, optional
        Number of noise reduction attempts if SNR is near acceptable (default: 2).
    min_snr_value : float, optional
        Minimum acceptable Signal-to-Noise Ratio (SNR) for approval (default: 40).
    min_snr_value_edit : float, optional
        Lower SNR threshold that triggers enhancement attempts (default: 30).
    min_speech_level : float, optional
        Minimum acceptable speech level in dB (default: -10).
    max_speech_level : float, optional
        Maximum acceptable speech level in dB (default: -30).
    min_noise_level : float, optional
        Maximum acceptable background noise level in dB (default: -40).

    Returns:
    --------
    Tuple[np.ndarray, Dict[str, float | str]]
        - The (possibly enhanced) audio data.
        - A dictionary with signal analysis results including:
          'signal_power', 'noise_power', 'snr', and 'message'.
    """
         
    analysis = analyze_audio(data, sr)
    
    message = ""
    if analysis['signal_power'] > max_speech_level:
        message = "Move your phone away from your mouth a little"
    elif analysis['signal_power'] < min_speech_level:
        message = "Please speak louder."
    elif analysis['noise_power'] > min_noise_level:
        message = "There is noise where you are."
    elif analysis['snr'] >= min_snr_value:
        message = "Approved"
    elif (analysis['snr'] >= min_snr_value_edit) and (analysis['snr'] < min_snr_value):
        for _ in range(try_enhance):
            data = reduce_noise(data, sr)
            analysis = analyze_audio(data, sr)

            if analysis['snr'] >= min_snr_value:
                break

        if analysis['snr'] >= min_snr_value:
            message = "Approved"
        elif (analysis['snr'] >= min_snr_value_edit) and (analysis['snr'] < min_snr_value):
            message = f"Almost there—speak a bit louder and clearer. SNR {analysis['snr']}"
        else:
            message = f"The Audio is noisy, please record where there is less noise. SNR {analysis['snr']}"
    else:
        message = f"The Audio is noisy, please record where there is less noise. SNR {analysis['snr']}"

    analysis['message'] = message
    return data, analysis

if __name__ == "__main__":
    import os
    import sys 
    import argparse

    parser = argparse.ArgumentParser(description="Audio Quality Check")
    parser.add_argument("file_path", type=str, help="Path to the audio file")
    parser.add_argument("--try_enhance", type=int, default=2, help="Number of noise reduction attempts")
    parser.add_argument("--min_snr_value", type=float, default=40, help="Minimum acceptable SNR value")
    parser.add_argument("--min_snr_value_edit", type=float, default=20, help="Lower SNR threshold for enhancement")
    parser.add_argument("--min_speech_level", type=float, default=-40, help="Minimum acceptable speech level in dB")
    parser.add_argument("--max_speech_level", type=float, default=-15, help="Maximum acceptable speech level in dB")
    parser.add_argument("--min_noise_level", type=float, default=-40, help="Maximum acceptable noise level in dB") 

    args = parser.parse_args()
    file_path = args.file_path

    if not file_path:
        print("Please provide a valid audio file path.")
        sys.exit(1)   

    try:
        y, sr = librosa.load(file_path, sr=None)
        enhanced_audio, analysis = check_audio_quality(data = y, sr=sr,
                                                       try_enhance=args.try_enhance, min_snr_value=args.min_snr_value,
                                                       min_snr_value_edit=args.min_snr_value_edit,
                                                       min_speech_level=args.min_speech_level,
                                                       max_speech_level=args.max_speech_level,
                                                       min_noise_level=args.min_noise_level)
        print(f"Analysis Results: {analysis}")
        os.path.split(file_path)
        output_path = file_path.replace(".wav", "_enhanced.mp3")
        print(f"Saving enhanced audio to {output_path}")
        save_librosa_audio_as_mp3(enhanced_audio, sr, output_path)

    except Exception as e:
        print(f"Error processing audio file: {e}")
        sys.exit(1)