import pandas as pd
import yfinance as yf


# =========================
# DATA
# =========================
def get_ftse_data():
    df = yf.download("^FTSE", period="5d", interval="15m")

    # fix possible multi-index issue
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df


# =========================
# RSI
# =========================
def compute_rsi(series, period=14):
    delta = series.diff()

    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs))


# =========================
# SIGNAL ENGINE (FINAL)
# =========================
def compute_signals(df):
    df = df.copy()
    close = df["Close"]

    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    df["ma20"] = close.rolling(20).mean()
    df["ma50"] = close.rolling(50).mean()
    df["rsi"] = compute_rsi(close, 14)

    df = df.dropna()

    ma20 = float(df["ma20"].iloc[-1])
    ma50 = float(df["ma50"].iloc[-1])
    rsi = float(df["rsi"].iloc[-1])
    price = float(df["Close"].iloc[-1])

    signal = "HOLD"

    # =========================
    # FINAL STRATEGY
    # =========================

    if ma20 > ma50 and rsi < 70:
        signal = "BUY"

    elif ma20 < ma50 and rsi < 30:
        signal = "POSSIBLE REVERSAL BUY"

    elif ma20 < ma50 and rsi > 50:
        signal = "SELL"

    return {
        "price": price,
        "rsi": rsi,
        "ma20": ma20,
        "ma50": ma50,
        "signal": signal
    }
