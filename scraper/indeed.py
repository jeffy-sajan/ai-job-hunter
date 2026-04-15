
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote_plus

from config import JOB_SEARCH_KEYWORDS, JOB_SEARCH_LOCATION


def fetch_indeed_jobs():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    jobs = []
    seen_links = set()

    for keyword in JOB_SEARCH_KEYWORDS:
        q = quote_plus(keyword)
        l = quote_plus(JOB_SEARCH_LOCATION)
        url = f"https://in.indeed.com/jobs?q={q}&l={l}"

        time.sleep(random.uniform(2, 4))

        try:
            response = requests.get(url, headers=headers, timeout=20)
            print(f"Indeed HTTP status for '{keyword}':", response.status_code)
        except Exception as e:
            print(f"Indeed request error for '{keyword}': {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("div.job_seen_beacon")
        print(f"Indeed cards for '{keyword}':", len(cards))

        for card in cards[:10]:
            title_tag = card.select_one("h2.jobTitle")
            company_tag = card.select_one("span.companyName")
            location_tag = card.select_one("div.companyLocation")
            link_tag = card.select_one("a")

            if not title_tag or not link_tag:
                continue

            href = link_tag.get("href", "")
            if not href:
                continue
            link = "https://in.indeed.com" + href
            if link in seen_links:
                continue

            job = {
                "title": title_tag.text.strip(),
                "company": company_tag.text.strip() if company_tag else "NA",
                "location": location_tag.text.strip() if location_tag else "NA",
                "link": link,
                "summary": f"Indeed keyword: {keyword}",
            }

            jobs.append(job)
            seen_links.add(link)

    return jobs


