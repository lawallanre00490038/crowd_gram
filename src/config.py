import os
from dotenv import load_dotenv
import logging


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_IDS = [int(id_) for id_ in os.getenv("ADMIN_IDS", "").split(",") if id_]
CLOUD_STORAGE = os.getenv("CLOUD_STORAGE", "s3")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BASE_URL_V2 = os.getenv("BACKEND_URL_V2", "http://localhost:8000/api/v2")
MONGO_DB_URI = os.getenv("MONGO_DB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "crowd_telegram")

try:
    USE_MONGO_DB = bool(os.getenv("USE_MONGO_DB", "False"))
except: 
    raise ValueError("Please USE_MONGO_DB is supposed to be a boolean")