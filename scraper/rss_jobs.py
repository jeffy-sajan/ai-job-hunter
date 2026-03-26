import feedparser


def fetch_rss_jobs():
    url = "https://www.indeed.co.in/rss?q=python+developer&l=India"

    feed = feedparser.parse(url)

    jobs = []

    for entry in feed.entries[:10]:
        job = {
            "title": entry.title,
            "company": entry.author if "author" in entry else "NA",
            "link": entry.link,
            "summary": entry.summary if "summary" in entry else "",
        }

        jobs.append(job)

    return jobs
