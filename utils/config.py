import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_URL = os.getenv("SHEET_URL")
GOOGLE_KEY_FILE = os.getenv("GOOGLE_KEY_FILE")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

channel_id_str = os.getenv("CHANNEL_ID", "")
# Should pick the first one if multiple are provided, or use as is
if "," in channel_id_str:
    CHANNEL_ID = channel_id_str.split(",")[0].strip()
else:
    CHANNEL_ID = channel_id_str.strip()

print(f"DEBUG: Loaded CHANNEL_ID='{CHANNEL_ID}'")
