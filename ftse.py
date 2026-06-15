import yfinance as yf
import pandas as pd

def get_ftse_data():
    df = yf.download("^FTSE", period="5d", interval="15m")
    return df

def compute_signals(df):
    df = df.copy()

    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma50"] = df["Close"].rolling(50).mean()
    df["rsi"] = compute_rsi(df["Close"], 14)

    latest = df.iloc[-1]

    signal = "HOLD"

    if latest["ma20"] > latest["ma50"] and latest["rsi"] < 70:
        signal = "BUY"
    elif latest["ma20"] < latest["ma50"]:
        signal = "SELL"

    return {
        "price": float(latest["Close"]),
        "rsi": float(latest["rsi"]),
        "ma20": float(latest["ma20"]),
        "ma50": float(latest["ma50"]),
        "signal": signal
    }


def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs))
