# main.py

from news_sentiment_scoring import scan_market
import json
from datetime import datetime


# =========================
# CONFIG
# =========================

TICKERS = [
    "BP.L",
    "HSBA.L",
    "BARC.L",
    "LLOY.L",
    "SHEL.L",
    "RDSA.L",
    "RIO.L",
    "GSK.L"
]


# =========================
# RUN ENGINE
# =========================

def run_scan():
    print("\n==============================")
    print(" FTSE AI AGENT RUN STARTED")
    print(" Time:", datetime.now())
    print("==============================\n")

    results = scan_market(TICKERS)

    if not results:
        print("No results found.")
        return

    # sort already done inside module, but double safe
    top = results[:3]

    print("\n🔥 TOP 3 POTENTIAL BUYS\n")

    for i, r in enumerate(top, 1):
        print(f"\n#{i} {r['ticker']}")
        print(f"Score: {round(r['score'], 4)}")
        print(f"Sentiment: {round(r['sentiment'], 4)}")
        print(f"Momentum: {round(r['momentum'], 4)}")

        print("\n📰 Top News:")
        for n in r["top_news"]:
            print("-", n["title"])

    # save output for GitHub Actions artifact / logs
    with open("latest_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n==============================")
    print("DONE - results saved")
    print("==============================")


# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    run_scan()
