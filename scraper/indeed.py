
import requests
from bs4 import BeautifulSoup
import time
import random


def fetch_indeed_jobs():
    url = "https://in.indeed.com/jobs?q=python+developer&l=India"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    time.sleep(random.uniform(2, 4))

    try:
        response = requests.get(url, headers=headers, timeout=20)
        print("HTTP status:", response.status_code)
    except Exception as e:
        print("Request error:", e)
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    cards = soup.select("div.job_seen_beacon")
    print("Found job card elements:", len(cards))

    jobs = []

    for card in cards[:10]:

        title_tag = card.select_one("h2.jobTitle")
        company_tag = card.select_one("span.companyName")
        location_tag = card.select_one("div.companyLocation")
        link_tag = card.select_one("a")

        if not title_tag or not link_tag:
            continue

        job = {
            "title": title_tag.text.strip(),
            "company": company_tag.text.strip() if company_tag else "NA",
            "location": location_tag.text.strip() if location_tag else "NA",
            "link": "https://in.indeed.com" + link_tag.get("href"),
        }

        jobs.append(job)

    return jobs


