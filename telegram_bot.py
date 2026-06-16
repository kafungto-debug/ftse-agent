import requests

TELEGRAM_BOT_TOKEN = "7928558624:AAHNQ-wFOeozj3HbI0EE-Fqe96rLPY7ScYI"
TELEGRAM_CHAT_ID = "6996421827"


def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        r = requests.post(url, data=payload)
        print("Telegram status:", r.status_code)
        print("Telegram response:", r.text)
        return r.json()
    except Exception as e:
        print("Telegram error:", e)
        return None
