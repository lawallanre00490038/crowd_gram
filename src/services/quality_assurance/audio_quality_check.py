import json
import time
import boto3
import json
import librosa 
import argparse
import numpy as np
import noisereduce as nr
from pydub import AudioSegment


import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def current_time_millis():
    '''Get the milliseconds of the current time'''
    return int(time.time() * 1000)

def upload_file_to_s3(file_path, bucket_name, s3_folder=""):
    """
    Uploads a file to an S3 bucket with a unique filename using the current timestamp in milliseconds.

    Args:
        file_path (str): Path to the local file.
        bucket_name (str): Target S3 bucket name.
        s3_folder (str): Optional folder path in S3 bucket.

    Returns:
        str: Full S3 key (object path) of the uploaded file.
    """
    s3 = boto3.client('s3')

    unique_name = f"task_audio-{current_time_millis()}.mp3"

    # Combine folder and filename
    s3_key = f"{s3_folder}/{unique_name}"

    try:
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"Uploaded to s3://{bucket_name}/{s3_key}")
        return s3_key
    except Exception as e:
        print(f"Upload failed: {e}")
        return None

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
        prop_decrease=0.7,
        n_fft=512,
        win_length=512,
        hop_length=128
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

def get_analysis(data, sr):
    '''Get Analysis of the Audio'''
    noise_power = cal_noise_floor(data, sr = sr)
    signal_power = cal_signal_power(data)

    snr_value = signal_power - noise_power

    silence_percentage = cal_silence_percentage(data, noise_power)

    return {"snr": float(snr_value),
            "silence": float(silence_percentage),
            "noise_power": float(noise_power),
            "signal_power": float(signal_power)}


def analyze_audio(data, sr, try_enhance = 2, min_snr_value = 40, min_snr_value_edit = 30, min_speech_level = -10, max_speech_level = -30, min_noise_level = -40):

    # Parameters on admin pannel 
    # min_snr_value
    # min_snr_value_edit
    # min_speech_level
    # max_speech_level
    # min_noise_level
     
    analysis = get_analysis(data, sr)
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
            analysis = get_analysis(data, sr)

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


def main(file_path, min_snr_value=40, 
         min_snr_value_edit=30, 
         min_speech_level=-10, 
         max_speech_level=-30, 
         min_noise_level=-40, 
         bucket_name="name_bucket",  
         bucket_path="path_bucket"): 

    data, sr = librosa.load(file_path, sr=None)

    data, result = analyze_audio(data, sr, 
                                 min_snr_value=min_snr_value, 
                                 min_snr_value_edit=min_snr_value_edit, 
                                 min_speech_level=min_speech_level, 
                                 max_speech_level=max_speech_level, 
                                 min_noise_level=min_noise_level)

    file_name = f"audio.mp3"
    save_librosa_audio_as_mp3(data, sr, file_name)


    s3_key = upload_file_to_s3(file_name, 
                                bucket_name=bucket_name, 
                                s3_folder=bucket_path)
    # s3_key = "Hello"
    return json.dumps({
      "snr": float(result["snr"]),
      "silence": float(result["silence"]),
      "noise_power": float(result["noise_power"]),
      "signal_power": float(result["signal_power"]),
      "message": result["message"],
      "s3_key": s3_key
     })


if __name__ == "__main__":
    import sys

    parser = argparse.ArgumentParser(description="Analyze audio quality and upload to S3")
    parser.add_argument("files", nargs='+', help="Path(s) to the audio file(s)")

    parser.add_argument("--min_snr_value", type=float, default=40, help="Minimum SNR value")
    parser.add_argument("--min_snr_value_edit", type=float, default=30, help="Minimum SNR edit value")
    parser.add_argument("--min_speech_level", type=float, default=-10, help="Minimum speech level (dB)")
    parser.add_argument("--max_speech_level", type=float, default=-30, help="Maximum speech level (dB)")
    parser.add_argument("--min_noise_level", type=float, default=-40, help="Minimum noise level (dB)")
    parser.add_argument("--bucket_name", type=str, default="name_bucket", help="S3 bucket name")
    parser.add_argument("--bucket_path", type=str, default="path_bucket", help="S3 bucket path")

    args = parser.parse_args()

    results = []
    for file_path in args.files:
        result = main(file_path,
                      min_snr_value=args.min_snr_value,
                      min_snr_value_edit=args.min_snr_value_edit,
                      min_speech_level=args.min_speech_level,
                      max_speech_level=args.max_speech_level,
                      min_noise_level=args.min_noise_level,
                      bucket_name=args.bucket_name,
                      bucket_path=args.bucket_path)
        results.append(json.loads(result))

    print(json.dumps(results, indent=2))
