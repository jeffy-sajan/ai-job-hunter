# AI Job Hunter 🚀

An automated job scraper that finds Python/tech opportunities from **RemoteOK**, **Naukri**, **Indeed**, **Infopark**, and **Technopark**, scores them based on your profile, and sends instant **Telegram notifications**.

## Features

✅ **Multi-source scraping**: RemoteOK + Naukri + Indeed  
✅ **Resume-based scoring**: filters jobs matching your resume/profile  
✅ **Entry-level filter**: keeps roles focused on 0-1 year/fresher/intern tracks  
✅ **Telegram alerts**: Instant notifications for matching jobs  
✅ **Duplicate protection**: SQLite prevents repeat notifications  
✅ **Zero cost**: Runs free on GitHub Actions  
✅ **One-time setup**: Set and forget automation  

## Local Setup

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd ai-job-hunter
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Telegram

1. Open Telegram → search for **@BotFather**
2. Create a new bot: `/newbot` → name it → copy TOKEN
3. Send `/start` to your bot
4. Get chat ID:
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
   (Find `"id"` in response)

### 3. Create `.env` File

```bash
# .env
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 4. Customize Skills / Resume

Edit `config.py`:
```python
SKILLS = [
    "python",
    "react",
    "fastapi",
    # add your skills
]
```

Optional resume-based setup:

1. Put your resume PDF in project root as `Jeffy_Sajan.pdf` (or set `RESUME_PDF_PATH` in `.env`).
2. For GitHub Actions without uploading PDF, set `RESUME_SKILLS_OVERRIDE` in secrets/variables:
   ```
   RESUME_SKILLS_OVERRIDE=python,django,sql,react,fastapi
   ```

### 5. Test Locally

```bash
python main.py
```

Expected output:
```
Fetching from RemoteOK...
Fetching from Naukri...
Fetching from Indeed...
Total Jobs: 12
NEW: Senior Python Engineer -> 66%
New jobs inserted: 5
Duplicates skipped: 7
```

## Deploy on GitHub Actions (FREE)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial AI job hunter"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-job-hunter.git
git push -u origin main
```

### 2. Add Secrets

Go to **GitHub Settings → Secrets and Variables → Actions**

Add:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### 3. Enable Workflow

The file `.github/workflows/job-hunter.yml` runs:
- **Every 6 hours** automatically
- **Manually** via "Actions" tab

### 4. View Logs

**Settings → Actions → All workflows → AI Job Hunter** → check run logs

## How It Works

```
RemoteOK API ──┐
Naukri Scrape ─┼─→ [Fetch Jobs] ─→ [Score] ─→ [DB Filter] ─→ [Telegram Alert]
Indeed RSS ────┘
Mock Fallback ──→ (if all sources fail)
```

## Customization

### Change job search keywords (Naukri/Indeed):

Edit `scraper/naukri.py`:
```python
url = "https://www.naukri.com/search?keyword=react+developer"
```

### Change run frequency:

Edit `.github/workflows/job-hunter.yml`:
```yaml
- cron: '0 */3 * * *'  # Every 3 hours
- cron: '0 9,18 * * *'  # 9 AM & 6 PM daily
```

### Skip certain sources:

Edit `main.py`, comment out:
```python
# jobs.extend(fetch_indeed_jobs())
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "403 Forbidden" | Rotate IP/increase delay (Indeed blocks scrapers) |
| No jobs returned | Some sites may block temporarily; fallback to mock data runs |
| Telegram alerts not received | Check token, chat ID, and "Start" bot in Telegram |
| GitHub Action fails | Check secrets are set correctly |

##File Structure

```
ai-job-hunter/
├── main.py                    # Main pipeline
├── config.py                  # Skills & secrets
├── requirements.txt           # Dependencies
├── .env                       # Local secrets (git-ignored)
├── .gitignore                 
│
├── scraper/
│   ├── remoteok.py           # RemoteOK API
│   ├── naukri.py             # Naukri scraper
│   ├── indeed.py             # Indeed scraper
│   ├── google_jobs.py        # Google Jobs (backup)
│   ├── mock.py               # Mock data fallback
│   └── rss_jobs.py           # RSS parser
│
├── matcher/
│   └── scorer.py             # Job scoring logic
│
├── notifier/
│   └── telegram.py           # Telegram alerts
│
├── database/
│   └── db.py                 # SQLite ops
│
├── data/
│   └── jobs.db               # Job cache (git-ignored in production)
│
└── .github/workflows/
    └── job-hunter.yml        # GitHub Actions config
```

## License

MIT — modify & share freely

---

**Happy job hunting! 🎯**
