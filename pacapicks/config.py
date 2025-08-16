from dotenv import load_dotenv
import os

load_dotenv(override=True)

# Configuration for Alpaca and OpenAI
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_HEADERS = {
	"APCA-API-KEY-ID": ALPACA_API_KEY,
	"APCA-API-SECRET-KEY": ALPACA_SECRET_KEY}
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

APP_BASE_URL = os.getenv("APP_BASE_URL")
# placeholder for config.py
