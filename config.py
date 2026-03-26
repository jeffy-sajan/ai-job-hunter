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

# Optional: place your resume PDF at this path for resume-based filtering.
RESUME_PDF_PATH = os.getenv("RESUME_PDF_PATH", "Jeffy_Sajan.pdf")

# Optional comma-separated override for resume skills, useful in GitHub Secrets.
# Example: python,django,sql,react,aws
RESUME_SKILLS_OVERRIDE = os.getenv("RESUME_SKILLS_OVERRIDE", "")

# Only send/store jobs with score >= this threshold.
MIN_MATCH_SCORE = int(os.getenv("MIN_MATCH_SCORE", "10"))

# Load from .env file, fallback to empty string
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Only accept jobs posted within this many days (default 2 days)
POSTED_WITHIN_DAYS = int(os.getenv("POSTED_WITHIN_DAYS", "3"))
