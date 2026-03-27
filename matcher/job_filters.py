import re
from typing import Dict


ENTRY_KEYWORDS = (
    "intern",
    "internship",
    "trainee",
    "fresher",
    "entry level",
    "entry-level",
    "junior",
    "jr",
    "graduate",
    "associate",
)

# Broader early-career role families suitable for MCA / CS master's graduates.
ROLE_KEYWORDS = (
    # Software / application
    "software developer",
    "software engineer",
    "application developer",
    "web developer",
    "backend",
    "frontend",
    "full stack",
    "mobile developer",
    # QA / testing
    "qa",
    "quality assurance",
    "software tester",
    "test engineer",
    "automation tester",
    "manual tester",
    "sdet",
    # Data / analytics
    "data analyst",
    "business analyst",
    "product analyst",
    "bi analyst",
    "reporting analyst",
    "mis analyst",
    "sql analyst",
    # Cloud / infra / operations
    "devops",
    "site reliability",
    "sre",
    "cloud engineer",
    "cloud support",
    "system administrator",
    "linux administrator",
    "database administrator",
    "dba",
    "network engineer",
    "it support",
    "technical support",
    "support engineer",
    "production support",
    # Security
    "cyber security",
    "cybersecurity",
    "security analyst",
    "soc analyst",
    "ethical hacker",
    "information security",
    # Product / consulting / documentation
    "technical consultant",
    "associate consultant",
    "solution consultant",
    "implementation engineer",
    "technical writer",
    "systems analyst",
    "system analyst",
)


def _parse_experience_years(text: str) -> tuple[int | None, int | None]:
    t = text.lower()

    # Matches ranges like 0-1 years, 0 to 1 yrs, 1-3 years
    m_range = re.search(
        r"(\d+)\s*(?:-|to)\s*(\d+)\s*(?:\+)?\s*(?:years|year|yrs|yr)",
        t,
    )
    if m_range:
        return int(m_range.group(1)), int(m_range.group(2))

    # Matches single forms like 1 year, 2+ years
    m_single = re.search(r"(\d+)\s*(?:\+)?\s*(?:years|year|yrs|yr)", t)
    if m_single:
        val = int(m_single.group(1))
        return val, val

    return None, None


def is_entry_level_job(job: Dict[str, str]) -> bool:
    """True for 0-1 year or clearly freshers/intern roles."""
    text = " ".join(
        [
            str(job.get("title", "")),
            str(job.get("company", "")),
            str(job.get("location", "")),
            str(job.get("summary", "")),
            " ".join(job.get("tags", [])) if isinstance(job.get("tags"), list) else "",
            str(job.get("experience", "")),
        ]
    ).lower()

    min_y, max_y = _parse_experience_years(text)
    if min_y is not None and max_y is not None:
        return min_y <= 1 and max_y <= 1

    # No explicit years available, rely on role intent.
    return any(k in text for k in ENTRY_KEYWORDS)


def get_role_match_count(job: Dict[str, str]) -> int:
    """Count matched MCA/CS role keywords in title/summary/tags."""
    text = " ".join(
        [
            str(job.get("title", "")),
            str(job.get("summary", "")),
            " ".join(job.get("tags", [])) if isinstance(job.get("tags"), list) else "",
        ]
    ).lower()
    return sum(1 for k in ROLE_KEYWORDS if k in text)


def is_cs_masters_eligible_job(job: Dict[str, str]) -> bool:
    """True when role intent matches common MCA/CS master's career paths."""
    return get_role_match_count(job) > 0
