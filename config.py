import os
from dotenv import load_dotenv

load_dotenv()

SKILLS = [
	"python",
	"react",
	"fastapi",
	"graphql",
	"sql",
	"mongodb",
]

# Load from .env file, fallback to empty string
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
