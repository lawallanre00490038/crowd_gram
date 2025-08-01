import os
import cv2
import json
import librosa
import tempfile
from typing import Optional

from moviepy import VideoFileClip, AudioFileClip
from img_quality_checks import is_blurry_frame, frame_entropy, calculate_niqe_score_frame
from audio_quality_check import check_audio_quality, save_librosa_audio_as_mp3

def extract_audio_from_video(video_path: str, output_format: str = "wav") -> str:
    """Extract audio from video and save as WAV or other format for processing."""
    clip = VideoFileClip(video_path)
    temp_audio_file = tempfile.NamedTemporaryFile(suffix=f".{output_format}", delete=False)
    clip.audio.write_audiofile(temp_audio_file.name, codec='pcm_s16le')  # WAV with 16-bit PCM
    return temp_audio_file.name

def replace_audio_in_video(video_path: str, new_audio_path: str, output_video_path: str):
    """
    Replace the audio in the video with the given new audio file.

    Args:
        video_path (str): Path to the original video.
        new_audio_path (str): Path to the enhanced audio file.
        output_video_path (str): Path to save the final video with new audio.
    """
    video_clip = VideoFileClip(video_path)
    new_audio_clip = AudioFileClip(new_audio_path)

    # Set new audio
    final_video = video_clip.set_audio(new_audio_clip)

    # Export video with new audio
    final_video.write_videofile(output_video_path, codec='libx264', audio_codec='aac', threads=4)

def check_video_audio_quality(
    file_path: str,
    min_snr_value: float = 40,
    min_snr_value_edit: float = 30,
    min_speech_level: float = -10,
    max_speech_level: float = -30,
    min_noise_level: float = -40,
    replace_audio: bool = True,
    output_video_path: Optional[str] = "output_video.mp4"
) -> str:
    """
    Analyze and improve audio quality from a video or audio file.
    If it's a video and `replace_audio=True`, replaces the original audio with enhanced version.

    Args:
        file_path (str): Path to video or audio file.
        min_snr_value (float): Minimum required SNR to approve.
        min_snr_value_edit (float): Acceptable SNR after enhancement.
        min_speech_level (float): Minimum speech power in dB.
        max_speech_level (float): Maximum speech power in dB.
        min_noise_level (float): Maximum allowed noise power in dB.
        replace_audio (bool): Whether to output a video with enhanced audio.
        output_video_path (Optional[str]): Destination for final video file.

    Returns:
        str: JSON string of the analysis and output path (if applicable).
    """
    
    is_video = file_path.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))

    # Step 1: Extract audio from video if needed
    if is_video:
        audio_path = extract_audio_from_video(file_path)
    else:
        audio_path = file_path

    # Step 2: Load audio
    data, sr = librosa.load(audio_path, sr=None)

    # Step 3: Analyze and possibly enhance audio
    data, result = check_audio_quality(data, sr,
                                 min_snr_value=min_snr_value,
                                 min_snr_value_edit=min_snr_value_edit,
                                 min_speech_level=min_speech_level,
                                 max_speech_level=max_speech_level,
                                 min_noise_level=min_noise_level)

    # Step 4: Save enhanced audio to file
    enhanced_audio_path = "enhanced_audio.mp3"
    save_librosa_audio_as_mp3(data, sr, enhanced_audio_path)

    # Step 5: Replace video audio
    if is_video and replace_audio:
        replace_audio_in_video(file_path, enhanced_audio_path, output_video_path)
        result["output_video_path"] = output_video_path

    # Step 6: Clean up extracted audio if temp
    if is_video and os.path.exists(audio_path):
        os.remove(audio_path)

    # Step 7: Return structured JSON response
    return json.dumps({
        "snr": float(result["snr"]),
        "silence": float(result["silence"]),
        "noise_power": float(result["noise_power"]),
        "signal_power": float(result["signal_power"]),
        "message": result["message"],
        "output_video": result.get("output_video_path", None)
    }, indent=2)

def run_video_quality_checks_with_average(video_path, blur_thresh=100.0, max_frames=100):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    frame_count = 0
    results = []

    sum_blurry = 0
    sum_entropy = 0.0
    sum_niqe = 0.0

    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        blurry = is_blurry_frame(frame, threshold=blur_thresh)
        ent = frame_entropy(frame)
        niqe = calculate_niqe_score_frame(frame)

        results.append({
            "frame": frame_count,
            "blurry": blurry,
            "entropy": ent,
            "niqe_score": niqe
        })

        sum_blurry += int(blurry)    # convert bool to int for averaging
        sum_entropy += ent
        sum_niqe += niqe

        frame_count += 1

    cap.release()

    avg_blurry = sum_blurry / frame_count if frame_count else 0
    avg_entropy = sum_entropy / frame_count if frame_count else 0
    avg_niqe = sum_niqe / frame_count if frame_count else 0

    return results, {
        "average_blurry": avg_blurry,
        "average_entropy": avg_entropy,
        "average_niqe_score": avg_niqe,
        "frames_processed": frame_count
    }