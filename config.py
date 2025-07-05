from dotenv import load_dotenv
import os

load_dotenv()  # 👈 Must be called before os.getenv

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
APP_URL = "https://pintrest-saved-updater-production.up.railway.app"  # 👈 your deployed domain
