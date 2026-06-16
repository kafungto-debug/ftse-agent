# news_sentiment_scoring.py

import feedparser
import pandas as pd
import requests
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import yfinance as yf

nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()


# =========================
# 1. NEWS SOURCES
# =========================

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}+stock&hl=en-GB&gl=GB&ceid=GB:en"

MOTLEY_FOOL_RSS = "https://www.fool.com/feeds/index.aspx"


def fetch_rss(url):
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries[:20]:
        articles.append({
            "title": entry.title,
            "summary": getattr(entry, "summary", ""),
            "link": entry.link
        })

    return articles


def fetch_google_news(query):
    url = GOOGLE_NEWS_RSS.format(query=query)
    return fetch_rss(url)


def fetch_motley_fool():
    return fetch_rss(MOTLEY_FOOL_RSS)


# =========================
# 2. SENTIMENT ANALYSIS
# =========================

def get_sentiment(text):
    score = sia.polarity_scores(text)
    return score["compound"]  # -1 to +1


def analyze_articles(articles):
    results = []

    for a in articles:
        text = a["title"] + " " + a["summary"]
        sentiment = get_sentiment(text)

        results.append({
            "title": a["title"],
            "link": a["link"],
            "sentiment": sentiment
        })

    return results


# =========================
# 3. STOCK DATA
# =========================

def get_price_momentum(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")

    if len(hist) < 2:
        return 0

    return (hist["Close"][-1] - hist["Close"][0]) / hist["Close"][0]


# =========================
# 4. SCORING ENGINE
# =========================

def compute_score(sentiment_avg, momentum):
    """
    Weighted scoring:
    sentiment 60%
    momentum 40%
    """
    return (sentiment_avg * 0.6) + (momentum * 0.4)


# =========================
# 5. MAIN PIPELINE
# =========================

def analyze_ticker(ticker, query):
    print(f"\nAnalyzing {ticker}...")

    # news
    google_news = fetch_google_news(query)
    fool_news = fetch_motley_fool()

    all_news = google_news + fool_news

    analyzed = analyze_articles(all_news)

    if len(analyzed) == 0:
        return None

    sentiment_avg = sum(a["sentiment"] for a in analyzed) / len(analyzed)

    momentum = get_price_momentum(ticker)

    score = compute_score(sentiment_avg, momentum)

    return {
        "ticker": ticker,
        "sentiment": sentiment_avg,
        "momentum": momentum,
        "score": score,
        "top_news": sorted(analyzed, key=lambda x: x["sentiment"], reverse=True)[:3]
    }


# =========================
# 6. MULTI-STOCK SCANNER
# =========================

def scan_market(tickers):
    results = []

    for t in tickers:
        r = analyze_ticker(t, t)
        if r:
            results.append(r)

    return sorted(results, key=lambda x: x["score"], reverse=True)


if __name__ == "__main__":
    ftse_stocks = ["BP.L", "HSBA.L", "BARC.L", "LLOY.L", "SHEL.L"]

    results = scan_market(ftse_stocks)

    for r in results[:3]:
        print("\n===================")
        print(r)
