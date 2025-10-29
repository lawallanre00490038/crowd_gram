import boto3
import time


def upload_media(file):
    # Upload to cloud storage (e.g., S3)
    return "media_id"


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
        logger.info(f"Uploaded to s3://{bucket_name}/{s3_key}")
        return s3_key
    except Exception as e:
        logger.info(f"Upload failed: {e}")
        return None
