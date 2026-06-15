import os
import requests
from datetime import datetime
from ftse import get_ftse_data, compute_signals


def send_telegram(message):
    bot_token = os.environ["BOT_TOKEN"]
    chat_id = os.environ["CHAT_ID"]

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.get(url, params={"chat_id": chat_id, "text": message})


def format_message(result):
    return f"""
📊 FTSE AI AGENT

⏰ Time: {datetime.now()}

💷 Price: {result['price']:.2f}
📈 RSI: {result['rsi']:.2f}
📊 MA20: {result['ma20']:.2f}
📊 MA50: {result['ma50']:.2f}

🚦 Signal: {result['signal']}
"""


if __name__ == "__main__":
    df = get_ftse_data()
    result = compute_signals(df)

    msg = format_message(result)
    print(msg)

    send_telegram(msg)
