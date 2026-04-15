import os
from dotenv import load_dotenv

load_dotenv()


def _split_csv_env(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name, "")
    if raw.strip():
        return [item.strip() for item in raw.split(",") if item.strip()]
    return default


SKILLS = [
    "software development",
    "web development",
    "backend",
    "frontend",
    "full stack",
    "qa testing",
    "data analysis",
    "sql",
    "devops",
    "cloud",
    "cybersecurity",
    "technical support",
]

# Broad CS/MCA-friendly keywords used by search-based scrapers.
JOB_SEARCH_KEYWORDS = _split_csv_env(
    "JOB_SEARCH_KEYWORDS",
    [
        "software developer fresher",
        "software engineer entry level",
        "qa tester fresher",
        "data analyst fresher",
        "devops engineer junior",
        "cyber security analyst fresher",
        "technical support engineer fresher",
    ],
)
JOB_SEARCH_LOCATION = os.getenv("JOB_SEARCH_LOCATION", "India")

# Keep these sources strongly represented.
INFOPARK_MAX_PAGES = int(os.getenv("INFOPARK_MAX_PAGES", "2"))
TECHNOPARK_MAX_PAGES = int(os.getenv("TECHNOPARK_MAX_PAGES", "3"))

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
