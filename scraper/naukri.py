import requests
from bs4 import BeautifulSoup


def fetch_naukri_jobs():
    """Fetch Python developer jobs from Naukri.com"""

    url = "https://www.naukri.com/search?keyword=python+developer"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"Naukri request error: {e}")
        return []

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = []

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

            if not title or not link:
                continue

            job = {
                "title": title,
                "company": company,
                "location": location,
                "link": link,
                "summary": "",
            }
            jobs.append(job)

        return jobs
    except Exception as e:
        print(f"Naukri parse error: {e}")
        return []
