from scraper.remoteok import fetch_remoteok_jobs
from scraper.naukri import fetch_naukri_jobs
from scraper.indeed import fetch_indeed_jobs
from scraper.mock import fetch_mock_jobs
from scraper.infopark import fetch_infopark_jobs_pages
from scraper.technopark import fetch_technopark_jobs
from matcher.scorer import calculate_score
from matcher.job_filters import is_entry_level_job, is_cs_masters_eligible_job
from matcher.resume_profile import build_resume_skill_list
from database.db import init_db, insert_job
from notifier.telegram import send_job_alert
from config import (
    SKILLS,
    RESUME_PDF_PATH,
    RESUME_SKILLS_OVERRIDE,
    MIN_MATCH_SCORE,
    POSTED_WITHIN_DAYS,
    INFOPARK_MAX_PAGES,
    TECHNOPARK_MAX_PAGES,
)
import re
from datetime import datetime, date, timedelta


def _parse_posted_date(posted_str: str):
    if not posted_str:
        return None
    s = posted_str.strip()
    low = s.lower()
    today = date.today()

    if not low:
        return None
    if "just" in low or "now" in low:
        return today
    if "today" in low:
        return today
    if "yesterday" in low:
        return today - timedelta(days=1)

    m = re.search(r"(\d+)\s+day", low)
    if m:
        try:
            return today - timedelta(days=int(m.group(1)))
        except Exception:
            pass

    m = re.search(r"(\d+)\s+hour", low)
    if m:
        try:
            return (datetime.now() - timedelta(hours=int(m.group(1)))).date()
        except Exception:
            pass

    # Try a few common date formats
    cleaned = re.sub(r"[^0-9A-Za-z, \-/:]", " ", s).strip()
    fmts = ["%d,%b %Y", "%d %b %Y", "%d-%b-%Y", "%Y-%m-%d", "%b %d, %Y", "%d/%m/%Y"]
    for fmt in fmts:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except Exception:
            continue

    # Fallback to dateutil if available
    try:
        from dateutil import parser as _dp
        dt = _dp.parse(s, dayfirst=True)
        return dt.date()
    except Exception:
        return None


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
    remote_jobs = fetch_remoteok_jobs()
    jobs.extend(remote_jobs)
    print(f"RemoteOK jobs fetched: {len(remote_jobs)}")

    print("Fetching from Naukri...")
    naukri_jobs = fetch_naukri_jobs()
    jobs.extend(naukri_jobs)
    print(f"Naukri jobs fetched: {len(naukri_jobs)}")

    print("Fetching from Indeed...")
    indeed_jobs = fetch_indeed_jobs()
    jobs.extend(indeed_jobs)
    print(f"Indeed jobs fetched: {len(indeed_jobs)}")

    print(f"Fetching from Infopark ({INFOPARK_MAX_PAGES} page(s))...")
    infopark_jobs = fetch_infopark_jobs_pages(INFOPARK_MAX_PAGES)
    jobs.extend(infopark_jobs)
    print(f"Infopark jobs fetched: {len(infopark_jobs)}")

    print(f"Fetching from Technopark ({TECHNOPARK_MAX_PAGES} page(s))...")
    technopark_jobs = fetch_technopark_jobs(TECHNOPARK_MAX_PAGES)
    jobs.extend(technopark_jobs)
    print(f"Technopark jobs fetched: {len(technopark_jobs)}")

    if not jobs:
        print("No live jobs found. Falling back to mock data.")
        jobs = fetch_mock_jobs()

    print(f"Total Jobs: {len(jobs)}")

    new_count = 0
    duplicate_count = 0
    filtered_not_entry = 0
    filtered_not_mca_role = 0
    filtered_low_score = 0
    filtered_old_posted = 0
    kept_unknown_posted = 0
    sent_any = False

    cutoff_date = date.today() - timedelta(days=POSTED_WITHIN_DAYS)

    for job in jobs:
        # Enforce posted-date cutoff
        posted_str = job.get("posted_on", job.get("posted", ""))
        parsed = _parse_posted_date(posted_str)
        if not parsed:
            # Keep jobs where posted date is missing/unclear; many sources omit this.
            kept_unknown_posted += 1
        elif parsed < cutoff_date:
            filtered_old_posted += 1
            continue

        if not is_entry_level_job(job):
            filtered_not_entry += 1
            continue

        if not is_cs_masters_eligible_job(job):
            filtered_not_mca_role += 1
            continue

        # Build text for scoring: title + company + tags/summary
        tags_text = " ".join(job.get("tags", [])) if job.get("tags") else ""
        summary_text = job.get("summary", "")
        text = " ".join([job.get("title", ""), job.get("company", ""), tags_text, summary_text])
        score = calculate_score(text, resume_skills)

        # For broader MCA/CS discovery, skill score is a ranking signal, not a hard filter.
        if score < MIN_MATCH_SCORE:
            filtered_low_score += 1

        inserted, err = insert_job(job, score)
        if inserted:
            new_count += 1
            print(f"NEW: {job.get('title')} -> {score}%")

            source = job.get("source", "")
            if not source:
                link_for_source = (job.get("link", "") or "").lower()
                if "infopark.in" in link_for_source:
                    source = "infopark"
                elif "technopark.in" in link_for_source:
                    source = "technopark"

            alert_job = {
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location", ""),
                "link": job.get("link"),
                "summary": tags_text or summary_text or job.get("tags"),
                "source": source,
                "posted_on": job.get("posted_on", job.get("posted", "")),
                "closing_date": job.get("closing_date", job.get("deadline", "")),
            }

            try:
                send_job_alert({**alert_job, "score": score})
                sent_any = True
            except Exception as e:
                print(f"Telegram alert failed: {e}")
        else:
            duplicate_count += 1

    print(f"New jobs inserted: {new_count}")
    print(f"Duplicates skipped: {duplicate_count}")
    print(f"Filtered (not entry-level): {filtered_not_entry}")
    print(f"Filtered (not MCA/CS role): {filtered_not_mca_role}")
    print(f"Filtered (posted older than {POSTED_WITHIN_DAYS} days): {filtered_old_posted}")
    print(f"Kept with unknown posted date: {kept_unknown_posted}")
    print(f"Below preferred match score (< {MIN_MATCH_SCORE}%) but kept: {filtered_low_score}")

    if not sent_any:
        print(f"[Main] No jobs sent. Sending 'no jobs found' alert...")
        try:
            send_job_alert({
                "title": "No new jobs found",
                "company": "",
                "location": "",
                "link": "",
                "summary": f"No matching jobs found.\nFilters: early-career + MCA/CS role relevance (skill score shown for ranking; preferred threshold {MIN_MATCH_SCORE}%).",
                "source": "All sources",
                "posted_on": "",
                "closing_date": "",
            })
            print(f"[Main] 'No jobs found' alert attempted")
        except Exception as e:
            print(f"[Main] 'No jobs found' alert failed: {e}")


if __name__ == "__main__":
    run_once()
