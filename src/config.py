import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_IDS = [int(id_) for id_ in os.getenv("ADMIN_IDS", "").split(",") if id_]
CLOUD_STORAGE = os.getenv("CLOUD_STORAGE", "s3")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")