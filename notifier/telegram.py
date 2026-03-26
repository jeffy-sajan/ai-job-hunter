from typing import Dict

import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_job_alert(job: Dict[str, str]) -> None:
	"""Send a simple job alert to Telegram.

	Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in config.py.
	If they are empty, this function does nothing.
	"""

	if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
		return

	text_lines = [
		f"Title: {job.get('title', '')}",
		f"Company: {job.get('company', '')}",
		f"Location: {job.get('location', '')}",
		f"Source: {job.get('source', '')}",
		f"Link: {job.get('link', '')}",
	]

	posted_on = job.get("posted_on")
	if posted_on:
		text_lines.append(f"Posted: {posted_on}")

	closing_date = job.get("closing_date")
	if closing_date:
		text_lines.append(f"Closing: {closing_date}")
	summary = job.get("summary")
	if summary:
		text_lines.append("")
		text_lines.append(summary[:400])

	message = "\n".join(text_lines)

	url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
	payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
	try:
		requests.post(url, json=payload, timeout=10)
	except Exception:
		# Fail silently for now; can be improved with logging
		pass


