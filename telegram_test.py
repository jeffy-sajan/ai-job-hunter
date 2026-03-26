import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def main() -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in config.py first.")
        return

    message = "🚀 AI Job Hunter Test Message"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }

    response = requests.post(url, data=payload, timeout=10)
    print(response.text)


if __name__ == "__main__":
    main()
