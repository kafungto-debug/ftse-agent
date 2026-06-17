from news_sentiment_scoring import scan_market
from telegram_bot import send_telegram_message
from datetime import datetime, date, timedelta
import pandas as pd
import json
import os

# 自動取得 FTSE100 股票
try:
    ftse = pd.read_html(
        "https://en.wikipedia.org/wiki/FTSE_100_Index"
    )[4]

    TICKERS = [
        str(t).replace(".", "-") + ".L"
        for t in ftse["EPIC"].tolist()
    ]

except Exception as e:
    print("Failed to load FTSE100 list:", e)

    # 備用名單
    TICKERS = [
        "BP.L",
        "HSBA.L",
        "BARC.L",
        "LLOY.L",
        "SHEL.L",
        "RIO.L",
        "GSK.L"
    ]


def load_history():
    if os.path.exists("previous_picks.json"):
        with open("previous_picks.json", "r") as f:
            return json.load(f)

    return {}


def save_history(history):
    with open("previous_picks.json", "w") as f:
        json.dump(history, f, indent=4)


def get_recent_picks(history, days=7):
    recent = set()

    for i in range(days):
        d = str(date.today() - timedelta(days=i))

        if d in history:
            recent.update(history[d])

    return recent


def format_message(results):
    msg = "📊 *FTSE AI DAILY SIGNAL*\n\n"
    msg += f"🕒 {datetime.now()}\n\n"

    for i, r in enumerate(results[:3], 1):
        msg += f"*#{i} {r['ticker']}*\n"
        msg += f"Score: {round(r['score'], 4)}\n"
        msg += f"Sentiment: {round(r['sentiment'], 4)}\n"
        msg += f"Momentum: {round(r['momentum'], 4)}\n\n"

    msg += "⚠️ Not financial advice"

    return msg


def run():
    history = load_history()
    recent = get_recent_picks(history)

    results = scan_market(TICKERS)

    if not results:
        print("No results")
        return

    # 排序
    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    # 去重覆
    filtered = []

    for r in results:
        if r["ticker"] not in recent:
            filtered.append(r)

        if len(filtered) >= 3:
            break

    # 如果唔夠3隻就補返
    if len(filtered) < 3:
        for r in results:
            if r not in filtered:
                filtered.append(r)

            if len(filtered) >= 3:
                break

    # 儲存今日推薦
    today = str(date.today())
    history[today] = [x["ticker"] for x in filtered]
    save_history(history)

    message = format_message(filtered)

    print(message)
    send_telegram_message(message)


if __name__ == "__main__":
    run()
