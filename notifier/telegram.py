from typing import Dict
from html import escape

import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_job_alert(job: Dict[str, str]) -> None:
	"""Send a simple job alert to Telegram.

	Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in config.py.
	If they are empty, this function does nothing.
	"""

	if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
		print(f"[Telegram] Skipping alert: TOKEN={'***' if TELEGRAM_BOT_TOKEN else 'MISSING'}, CHAT_ID={'***' if TELEGRAM_CHAT_ID else 'MISSING'}")
		return

	title = escape(str(job.get("title", "")))
	company = escape(str(job.get("company", "")))
	location = escape(str(job.get("location", "")))
	source = escape(str(job.get("source", "")))
	link = str(job.get("link", "")).strip()

	text_lines = [
		f"<b>Title:</b> {title}",
		f"<b>Company:</b> {company}",
		f"<b>Location:</b> {location}",
		f"<b>Source:</b> {source}",
	]
	if link:
		# HTML parse mode makes links consistently clickable in Telegram.
		safe_link = escape(link, quote=True)
		text_lines.append(f"<b>Link:</b> <a href=\"{safe_link}\">Open Job</a>")
		text_lines.append(f"<code>{escape(link)}</code>")
	else:
		text_lines.append("<b>Link:</b> NA")

	posted_on = job.get("posted_on")
	if posted_on:
		text_lines.append(f"<b>Posted:</b> {escape(str(posted_on))}")

	closing_date = job.get("closing_date")
	if closing_date:
		text_lines.append(f"<b>Closing:</b> {escape(str(closing_date))}")
	summary = job.get("summary")
	if summary:
		text_lines.append("")
		text_lines.append(escape(str(summary))[:400])

	message = "\n".join(text_lines)

	url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
	payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}
	try:
		print(f"[Telegram] Sending alert for: {job.get('title', 'Unknown')}")
		r = requests.post(url, json=payload, timeout=10)
		print(f"[Telegram] Alert sent. Status code: {r.status_code}")
	except Exception as e:
		print(f"[Telegram] Failed to send alert: {e}")
		pass


