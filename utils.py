import yfinance as yf
import pandas as pd


def get_stock_data(ticker, period="1y"):
    """
    Fetch historical stock data for the given ticker and period.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)

        if df.empty:
            return None

        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()

        # Moving averages
        df["MA20"] = df["Close"].rolling(window=20).mean()
        df["MA50"] = df["Close"].rolling(window=50).mean()

        return df
    except Exception:
        return None


def get_stock_info(ticker):
    """
    Fetch stock metadata / latest information.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except Exception:
        return {}


def calculate_metrics(df):
    """
    Calculate stock insights and trend summary.
    """
    max_close = df["Close"].max()
    min_close = df["Close"].min()
    avg_close = df["Close"].mean()

    first_close = df["Close"].iloc[0]
    last_close = df["Close"].iloc[-1]

    if last_close > first_close:
        trend = "Uptrend"
    elif last_close < first_close:
        trend = "Downtrend"
    else:
        trend = "Stable"

    percentage_change = ((last_close - first_close) / first_close) * 100

    summary = (
        f"The stock moved from ${first_close:.2f} to ${last_close:.2f} during the selected period, "
        f"showing a {trend.lower()} with an overall change of {percentage_change:.2f}%. "
        f"The highest closing price was ${max_close:.2f}, while the lowest closing price was ${min_close:.2f}. "
        f"The average closing price during this period was ${avg_close:.2f}."
    )

    return {
        "max_close": max_close,
        "min_close": min_close,
        "avg_close": avg_close,
        "trend": trend,
        "summary": summary
    }


def get_popular_stocks_snapshot(tickers):
    """
    Fetch latest snapshot for popular stocks dashboard.
    """
    result = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")

            if hist.empty:
                result.append({"Ticker": ticker, "Price": None, "Change": None})
                continue

            latest_close = hist["Close"].iloc[-1]

            if len(hist) > 1:
                prev_close = hist["Close"].iloc[-2]
                change_pct = ((latest_close - prev_close) / prev_close) * 100
            else:
                change_pct = 0

            result.append({
                "Ticker": ticker,
                "Price": float(latest_close),
                "Change": float(change_pct)
            })

        except Exception:
            result.append({"Ticker": ticker, "Price": None, "Change": None})

    return result