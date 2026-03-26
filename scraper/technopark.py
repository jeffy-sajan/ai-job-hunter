import re
from typing import Dict, List
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE = "https://technopark.in"


def _title_from_link(link: str) -> str:
    parsed = urlparse(link)
    job_param = parse_qs(parsed.query).get("job", [])
    if job_param:
        return unquote(job_param[0]).strip()
    return ""


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _extract_from_markdown(md: str) -> List[Dict]:
    """Parse markdown mirrors (r.jina.ai) for job links and metadata."""
    jobs: List[Dict] = []
    seen = set()

    # Capture blocks with title, company, and job-details URL.
    pattern = re.compile(
        r"####\s*(?P<title>.*?)\s*Closing Date:\s*(?P<closing_date>.*?)\s*##\s*(?P<company>.*?)\s*Posted On:\s*(?P<posted_on>.*?)\]\((?P<link>https?://technopark\.in/job-details/[^)]+)\)",
        re.IGNORECASE | re.DOTALL,
    )
    for m in pattern.finditer(md):
        title = _clean_text(m.group("title"))
        company = _clean_text(m.group("company")) or "Technopark Company"
        closing_date = _clean_text(m.group("closing_date"))
        posted_on = _clean_text(m.group("posted_on"))
        link = m.group("link").replace("http://", "https://")
        if not link or link in seen:
            continue

        jobs.append(
            {
                "title": title or _title_from_link(link),
                "company": company,
                "location": "Technopark, Kerala",
                "link": link,
                "summary": _clean_text(m.group(0))[:400],
                "experience": "",
                "closing_date": closing_date,
                "posted_on": posted_on,
                "source": "technopark",
            }
        )
        seen.add(link)

    # Fallback: if structured capture fails, at least parse links.
    if jobs:
        return jobs

    for link in re.findall(r"https?://technopark\.in/job-details/[^)\s]+", md, re.IGNORECASE):
        link = link.replace("http://", "https://")
        if link in seen:
            continue
        title = _title_from_link(link) or "Technopark Job"
        jobs.append(
            {
                "title": title,
                "company": "Technopark Company",
                "location": "Technopark, Kerala",
                "link": link,
                "summary": "",
                "experience": "",
                "source": "technopark",
            }
        )
        seen.add(link)

    return jobs


def fetch_technopark_jobs(max_pages: int = 2) -> List[Dict]:
    """Fetch jobs from Technopark job search pages.

    This parser extracts links like /job-details/<id>?job=<title> and builds
    basic job objects used by the main pipeline.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
    }

    jobs: List[Dict] = []
    seen_links = set()

    for page in range(1, max_pages + 1):
        if page == 1:
            url = f"{BASE}/job-search"
        else:
            url = f"{BASE}/job-search?page={page}"

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
        except Exception as exc:
            print(f"Technopark request error on page {page}: {exc}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.select("a[href*='/job-details/']"):
            href = a.get("href") or ""
            link = urljoin(BASE, href)
            if not link or link in seen_links:
                continue

            anchor_text = _clean_text(a.get_text(" ", strip=True))
            title = _title_from_link(link)
            if not title:
                # Fallback for unexpected links
                title = anchor_text[:120]

            # Heuristic company extraction from surrounding anchor text
            company = "Technopark Company"
            if anchor_text:
                company = anchor_text.split(" Closing Date:")[0].strip()
                # Remove title fragment if present
                if title and title.lower() in company.lower():
                    company = re.sub(re.escape(title), "", company, flags=re.IGNORECASE).strip()
                company = company or "Technopark Company"

            summary = anchor_text[:400]
            experience = ""
            m_exp = re.search(r"(\d+\s*(?:-|to)\s*\d+\s*(?:years|year|yrs|yr)|\d+\+?\s*(?:years|year|yrs|yr))", anchor_text, re.IGNORECASE)
            if m_exp:
                experience = m_exp.group(1)

            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": "Technopark, Kerala",
                    "link": link,
                    "summary": summary,
                    "experience": experience,
                    "closing_date": "",
                    "posted_on": "",
                    "source": "technopark",
                }
            )
            seen_links.add(link)

    # Direct HTML can be empty for bot-like requests; use rendered markdown mirror fallback.
    if jobs:
        return jobs

    try:
        mirror_url = "https://r.jina.ai/http://technopark.in/job-search?type=Job%20Posting"
        md = requests.get(mirror_url, headers=headers, timeout=30).text
        mirror_jobs = _extract_from_markdown(md)
        return mirror_jobs
    except Exception as exc:
        print(f"Technopark fallback parse error: {exc}")

    return jobs


if __name__ == "__main__":
    result = fetch_technopark_jobs(2)
    print("found", len(result), "jobs")
    for item in result[:10]:
        print(item["title"], "|", item["company"], "|", item["link"])
