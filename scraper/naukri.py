import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from config import JOB_SEARCH_KEYWORDS


def fetch_naukri_jobs():
    """Fetch broader CS/MCA fresher-friendly jobs from Naukri.com."""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
    }

    jobs = []
    seen_links = set()

    for keyword in JOB_SEARCH_KEYWORDS:
        url = f"https://www.naukri.com/search?keyword={quote_plus(keyword)}"

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
        except Exception as e:
            print(f"Naukri request error for '{keyword}': {e}")
            continue

        try:
            soup = BeautifulSoup(response.text, "html.parser")

            # Naukri uses article.jobTuple or divs with job data
            job_cards = soup.select("article.jobTuple")

            for card in job_cards[:10]:
                title_el = card.select_one("a.jobTitle")
                company_el = card.select_one("a.subTitle")
                location_el = card.select_one(".job-location")

                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                company = company_el.get_text(strip=True) if company_el else "NA"
                location = location_el.get_text(strip=True) if location_el else "NA"
                link = title_el.get("href", "")
                if not link.startswith("http"):
                    link = "https://www.naukri.com" + link if link.startswith("/") else ""

                if not title or not link or link in seen_links:
                    continue

                job = {
                    "title": title,
                    "company": company,
                    "location": location,
                    "link": link,
                    "summary": f"Naukri keyword: {keyword}",
                }
                jobs.append(job)
                seen_links.add(link)
        except Exception as e:
            print(f"Naukri parse error for '{keyword}': {e}")
            continue

    return jobs
