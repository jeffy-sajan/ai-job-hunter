import os
import re
from typing import Iterable, List

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - optional dependency import guard
    PdfReader = None


KNOWN_TECH_SKILLS = [
    "python",
    "django",
    "flask",
    "fastapi",
    "react",
    "node",
    "nodejs",
    "javascript",
    "typescript",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "redis",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "git",
    "linux",
    "html",
    "css",
    "graphql",
    "rest",
    "pandas",
    "numpy",
    "machine learning",
    "ai",
]


def extract_text_from_pdf(pdf_path: str) -> str:
    if not pdf_path or not os.path.exists(pdf_path):
        return ""
    if PdfReader is None:
        return ""

    try:
        reader = PdfReader(pdf_path)
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts)
    except Exception:
        return ""


def build_resume_skill_list(pdf_path: str, fallback_skills: Iterable[str]) -> List[str]:
    """Build skill list from resume PDF; fallback to configured skills."""
    fallback = [s.strip().lower() for s in fallback_skills if s and s.strip()]
    resume_text = extract_text_from_pdf(pdf_path).lower()

    if not resume_text:
        return fallback

    detected = []
    for skill in KNOWN_TECH_SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, resume_text):
            detected.append(skill.lower())

    # Include fallback skills explicitly if resume mentions them.
    for skill in fallback:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, resume_text) and skill not in detected:
            detected.append(skill)

    return detected if detected else fallback
