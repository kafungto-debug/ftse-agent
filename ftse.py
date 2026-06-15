import pandas as pd
import yfinance as yf


# =========================
# 1. GET FTSE DATA
# =========================
def get_ftse_data():
    df = yf.download("^FTSE", period="5d", interval="15m")

    # 🔥 fix MultiIndex issue (yfinance sometimes returns nested columns)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df


# =========================
# 2. RSI CALCULATION
# =========================
def compute_rsi(series, period=14):
    delta = series.diff()

    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


# =========================
# 3. SIGNAL ENGINE
# =========================
def compute_signals(df):
    df = df.copy()

    close = df["Close"]

    # 🔥 safety: ensure Series (not DataFrame)
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    # indicators
    df["ma20"] = close.rolling(20).mean()
    df["ma50"] = close.rolling(50).mean()
    df["rsi"] = compute_rsi(close, 14)

    # drop NaN rows (important)
    df = df.dropna()

    latest = df.iloc[-1]

    # 🔥 force scalar safely
    ma20 = float(df["ma20"].iloc[-1])
    ma50 = float(df["ma50"].iloc[-1])
    rsi = float(df["rsi"].iloc[-1])
    price = float(df["Close"].iloc[-1])

    # =========================
    # SIGNAL LOGIC
    # =========================
    signal = "HOLD"

    if ma20 > ma50 and rsi < 70:
        signal = "BUY"
    elif ma20 < ma50 and rsi > 30:
        signal = "SELL"

    return {
        "price": price,
        "rsi": rsi,
        "ma20": ma20,
        "ma50": ma50,
        "signal": signal
    }
