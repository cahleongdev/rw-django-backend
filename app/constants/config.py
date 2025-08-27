import os

from dotenv import load_dotenv

load_dotenv()

DATABSE_SEED_DATA_PATH = os.getenv("DATABSE_SEED_DATA_PATH", "./app/seeds/")
NOTIFICATION_TABLE_NAME = os.getenv("NOTIFICATION_TABLE_NAME", "notifications")
