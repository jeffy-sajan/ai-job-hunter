import requests


def fetch_remoteok_jobs():

    url = "https://remoteok.com/api"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        data = response.json()
    except Exception as e:
        print("API error:", e)
        return []

    jobs = []

    # first element is metadata → skip
    for job in data[1:15]:

        title = job.get("position")
        company = job.get("company")
        tags = job.get("tags", [])
        link = job.get("url")

        job_obj = {
            "title": title,
            "company": company,
            "tags": tags,
            "link": link
        }

        jobs.append(job_obj)

    return jobs
