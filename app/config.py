from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")
CLIENT_BOT_TOKEN = os.environ.get("CLIENT_BOT_TOKEN")