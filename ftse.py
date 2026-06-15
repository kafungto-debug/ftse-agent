import pandas as pd
import yfinance as yf


def get_ftse_data():
    return yf.download("^FTSE", period="5d", interval="15m")


def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs))


def compute_signals(df):
    df = df.copy()

    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma50"] = df["Close"].rolling(50).mean()
    df["rsi"] = compute_rsi(df["Close"], 14)

    latest = df.iloc[-1]

    ma20 = float(latest["ma20"])
    ma50 = float(latest["ma50"])
    rsi = float(latest["rsi"])

    signal = "HOLD"

    if ma20 > ma50 and rsi < 70:
        signal = "BUY"
    elif ma20 < ma50:
        signal = "SELL"

    return {
        "price": float(latest["Close"]),
        "rsi": rsi,
        "ma20": ma20,
        "ma50": ma50,
        "signal": signal
    }
