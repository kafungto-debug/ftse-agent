import os
import requests
from ftse import get_ftse_data, compute_signals
from datetime import datetime

data = get_ftse_data()
result = compute_signals(data)

msg = f"""
📊 FTSE AI AGENT

⏰ Time: {datetime.now()}

💷 Price: {result['price']:.2f}
📈 RSI: {result['rsi']:.2f}
📊 MA20: {result['ma20']:.2f}
📊 MA50: {result['ma50']:.2f}

🚦 Signal: {result['signal']}
"""

print(msg)

# Telegram
bot_token = os.environ["BOT_TOKEN"]
chat_id = os.environ["CHAT_ID"]

requests.get(
    f"https://api.telegram.org/bot{bot_token}/sendMessage",
    params={"chat_id": chat_id, "text": msg}
)
