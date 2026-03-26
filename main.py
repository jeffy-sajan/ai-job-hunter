from scraper.remoteok import fetch_remoteok_jobs
from scraper.naukri import fetch_naukri_jobs
from scraper.indeed import fetch_indeed_jobs
from scraper.mock import fetch_mock_jobs
from scraper.infopark import fetch_infopark_jobs
from scraper.technopark import fetch_technopark_jobs
from matcher.scorer import calculate_score
from matcher.job_filters import is_entry_level_job
from matcher.resume_profile import build_resume_skill_list
from database.db import init_db, insert_job
from notifier.telegram import send_job_alert
from config import SKILLS, RESUME_PDF_PATH, RESUME_SKILLS_OVERRIDE, MIN_MATCH_SCORE


def run_once() -> None:
    init_db()
    if RESUME_SKILLS_OVERRIDE.strip():
        resume_skills = [s.strip().lower() for s in RESUME_SKILLS_OVERRIDE.split(",") if s.strip()]
    else:
        resume_skills = build_resume_skill_list(RESUME_PDF_PATH, SKILLS)
    print(f"Using {len(resume_skills)} resume/profile skills for matching")

    # Try all sources in order
    jobs = []

    print("Fetching from RemoteOK...")
    jobs.extend(fetch_remoteok_jobs())

    print("Fetching from Naukri...")
    jobs.extend(fetch_naukri_jobs())

    print("Fetching from Indeed...")
    jobs.extend(fetch_indeed_jobs())

    print("Fetching from Infopark...")
    # fetch first page; increase range if you want more pages
    jobs.extend(fetch_infopark_jobs(1))

    print("Fetching from Technopark...")
    jobs.extend(fetch_technopark_jobs(2))

    if not jobs:
        print("No live jobs found. Falling back to mock data.")
        jobs = fetch_mock_jobs()

    print(f"Total Jobs: {len(jobs)}")

    new_count = 0
    duplicate_count = 0
    filtered_not_entry = 0
    filtered_low_score = 0

    for job in jobs:
        if not is_entry_level_job(job):
            filtered_not_entry += 1
            continue

        # Build text for scoring: title + company + tags/summary
        tags_text = " ".join(job.get("tags", [])) if job.get("tags") else ""
        summary_text = job.get("summary", "")
        text = " ".join([job.get("title", ""), job.get("company", ""), tags_text, summary_text])
        score = calculate_score(text, resume_skills)

        if score < MIN_MATCH_SCORE:
            filtered_low_score += 1
            continue

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
                "source": job.get("source", ""),
                "posted_on": job.get("posted_on", job.get("posted", "")),
                "closing_date": job.get("closing_date", job.get("deadline", "")),
            }

            try:
                send_job_alert({**alert_job, "score": score})
            except Exception as e:
                print(f"Telegram alert failed: {e}")
        else:
            duplicate_count += 1

    print(f"New jobs inserted: {new_count}")
    print(f"Duplicates skipped: {duplicate_count}")
    print(f"Filtered (not entry-level): {filtered_not_entry}")
    print(f"Filtered (low match score < {MIN_MATCH_SCORE}%): {filtered_low_score}")


if __name__ == "__main__":
    run_once()
