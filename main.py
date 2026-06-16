from news_sentiment_scoring import scan_market
from telegram_bot import send_telegram_message
from datetime import datetime


TICKERS = [
    "BP.L", "HSBA.L", "BARC.L", "LLOY.L",
    "SHEL.L", "RIO.L", "GSK.L"
]


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
    results = scan_market(TICKERS)

    if not results:
        print("No results")
        return

    message = format_message(results)

    print(message)

    send_telegram_message(message)


if __name__ == "__main__":
    run()
