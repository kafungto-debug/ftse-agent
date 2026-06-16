import feedparser
import pandas as pd
import requests
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import yfinance as yf
import math

nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()


# =========================
# NEWS SOURCES
# =========================

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}+stock&hl=en-GB&gl=GB&ceid=GB:en"

MOTLEY_FOOL_RSS = "https://www.fool.com/feeds/index.aspx"


def fetch_rss(url):
    feed = feedparser.parse(url)
    articles = []

    if not feed or not hasattr(feed, "entries"):
        return []

    for entry in feed.entries[:20]:
        articles.append({
            "title": getattr(entry, "title", ""),
            "summary": getattr(entry, "summary", ""),
            "link": getattr(entry, "link", "")
        })

    return articles


def fetch_google_news(query):
    url = GOOGLE_NEWS_RSS.format(query=query)
    return fetch_rss(url)


def fetch_motley_fool():
    return fetch_rss(MOTLEY_FOOL_RSS)


# =========================
# SENTIMENT
# =========================

def get_sentiment(text):
    if not text:
        return 0.0

    score = sia.polarity_scores(text)
    return float(score.get("compound", 0.0))


def analyze_articles(articles):
    results = []

    for a in articles:
        text = f"{a.get('title','')} {a.get('summary','')}"
        sentiment = get_sentiment(text)

        results.append({
            "title": a.get("title", ""),
            "link": a.get("link", ""),
            "sentiment": sentiment
        })

    return results


# =========================
# PRICE MOMENTUM (FIXED)
# =========================

def get_price_momentum(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")

        if hist is None or hist.empty:
            return 0.0

        close_prices = hist["Close"].dropna()

        if len(close_prices) < 2:
            return 0.0

        start = float(close_prices.iloc[0])
        end = float(close_prices.iloc[-1])

        if start == 0:
            return 0.0

        return float((end - start) / start)

    except Exception:
        return 0.0


# =========================
# SCORING
# =========================

def compute_score(sentiment_avg, momentum):
    if sentiment_avg is None or math.isnan(sentiment_avg):
        sentiment_avg = 0.0

    if momentum is None or math.isnan(momentum):
        momentum = 0.0

    return float((sentiment_avg * 0.6) + (momentum * 0.4))


# =========================
# MAIN ANALYSIS
# =========================

def analyze_ticker(ticker, query):
    print(f"Analyzing {ticker}")

    google_news = fetch_google_news(query)
    fool_news = fetch_motley_fool()

    all_news = google_news + fool_news

    analyzed = analyze_articles(all_news)

    if not analyzed:
        return {
            "ticker": ticker,
            "sentiment": 0.0,
            "momentum": 0.0,
            "score": 0.0,
            "top_news": []
        }

    sentiment_avg = sum(a["sentiment"] for a in analyzed) / len(analyzed)

    momentum = get_price_momentum(ticker)

    score = compute_score(sentiment_avg, momentum)

    top_news = sorted(analyzed, key=lambda x: x["sentiment"], reverse=True)[:3]

    return {
        "ticker": ticker,
        "sentiment": float(sentiment_avg),
        "momentum": float(momentum),
        "score": float(score),
        "top_news": top_news
    }


# =========================
# MARKET SCAN
# =========================

def scan_market(tickers):
    results = []

    for t in tickers:
        r = analyze_ticker(t, t)
        results.append(r)

    return sorted(results, key=lambda x: x["score"], reverse=True)
