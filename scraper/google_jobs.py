import requests
from bs4 import BeautifulSoup
import time
import random


def fetch_google_jobs():

    query = "python developer jobs in India"
    url = f"https://www.google.com/search?q={query}&ibp=htl;jobs"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    time.sleep(random.uniform(2, 4))

    try:
        response = requests.get(url, headers=headers, timeout=20)
        print("HTTP status:", response.status_code)
    except Exception as e:
        print("Request failed:", e)
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []

    cards = soup.select("div.MQUd2b")

    print("Found cards:", len(cards))

    for card in cards[:10]:

        title_tag = card.select_one("div.tNxQIb")
        company_tag = card.select_one("div.wHYlTd")
        location_tag = card.select_one("div.wHYlTd span")

        if not title_tag:
            continue

        job = {
            "title": title_tag.text.strip(),
            "company": company_tag.text.strip() if company_tag else "NA",
            "location": location_tag.text.strip() if location_tag else "NA"
        }

        jobs.append(job)

    return jobs
