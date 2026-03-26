from scraper.remoteok import fetch_remoteok_jobs
from scraper.naukri import fetch_naukri_jobs
from scraper.indeed import fetch_indeed_jobs
from scraper.mock import fetch_mock_jobs
from matcher.scorer import calculate_score
from database.db import init_db, insert_job
from notifier.telegram import send_job_alert


def run_once() -> None:
    init_db()

    # Try all sources in order
    jobs = []

    print("Fetching from RemoteOK...")
    jobs.extend(fetch_remoteok_jobs())

    print("Fetching from Naukri...")
    jobs.extend(fetch_naukri_jobs())

    print("Fetching from Indeed...")
    jobs.extend(fetch_indeed_jobs())

    if not jobs:
        print("No live jobs found. Falling back to mock data.")
        jobs = fetch_mock_jobs()

    print(f"Total Jobs: {len(jobs)}")

    new_count = 0
    duplicate_count = 0

    for job in jobs:
        # Build text for scoring: title + company + tags/summary
        tags_text = " ".join(job.get("tags", [])) if job.get("tags") else ""
        summary_text = job.get("summary", "")
        text = " ".join([job.get("title", ""), job.get("company", ""), tags_text, summary_text])
        score = calculate_score(text)

        inserted, err = insert_job(job, score)
        if inserted:
            new_count += 1
            print(f"NEW: {job.get('title')} -> {score}%")

            alert_job = {
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location", ""),
                "link": job.get("link"),
                "summary": tags_text or summary_text or job.get("tags"),
            }

            try:
                send_job_alert({**alert_job, "score": score})
            except Exception as e:
                print(f"Telegram alert failed: {e}")
        else:
            duplicate_count += 1

    print(f"New jobs inserted: {new_count}")
    print(f"Duplicates skipped: {duplicate_count}")


if __name__ == "__main__":
    run_once()
