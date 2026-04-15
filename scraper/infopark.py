import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict

BASE = "https://infopark.in"


def fetch_infopark_jobs(page: int = 1) -> List[Dict]:
    """Fetch jobs from Infopark job-search page (single page).

    Returns a list of job dicts with keys: title, company, link, date, deadline
    """
    url = f"{BASE}/companies/job-search"
    if page and page > 1:
        url = f"{url}?page={page}"

    resp = requests.get(url, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []

    # Look for table rows that contain a 'Details' link
    for a in soup.find_all("a", string=lambda t: t and "Details" in t):
        # prefer the parent <tr>
        tr = a.find_parent("tr")
        if tr:
            tds = tr.find_all("td")
            if len(tds) >= 4:
                posted = tds[0].get_text(strip=True)
                title = tds[1].get_text(strip=True)
                company = tds[2].get_text(strip=True)
                deadline = tds[3].get_text(strip=True)
                link = a.get("href") or ""
                link = urljoin(BASE, link)
                jobs.append({
                    "title": title,
                    "company": company,
                    "link": link,
                    "posted": posted,
                    "deadline": deadline,
                    "source": "infopark",
                })
                continue

        # If no <tr>, try to parse from nearby text nodes
        parent = a.parent
        text = parent.get_text(" ", strip=True)
        parts = [p.strip() for p in text.split("|") if p.strip()]
        if len(parts) >= 3:
            # heuristic: date | title | company | ...
            posted = parts[0]
            title = parts[1]
            company = parts[2]
            link = a.get("href") or ""
            link = urljoin(BASE, link)
            jobs.append({
                "title": title,
                "company": company,
                "link": link,
                "posted": posted,
                "deadline": "",
                "source": "infopark",
            })

    return jobs


def fetch_infopark_jobs_pages(max_pages: int = 2) -> List[Dict]:
    """Fetch multiple Infopark pages and dedupe by link."""
    jobs: List[Dict] = []
    seen_links = set()

    total_pages = max(1, int(max_pages))
    for page in range(1, total_pages + 1):
        try:
            page_jobs = fetch_infopark_jobs(page)
        except Exception as exc:
            print(f"Infopark request error on page {page}: {exc}")
            continue

        for job in page_jobs:
            link = (job.get("link") or "").strip()
            if not link or link in seen_links:
                continue
            jobs.append(job)
            seen_links.add(link)

    return jobs


if __name__ == "__main__":
    # Quick manual test
    j = fetch_infopark_jobs(1)
    print("found", len(j), "jobs")
    for i, job in enumerate(j[:10], 1):
        print(i, job["title"], "-", job["company"], job["link"])
