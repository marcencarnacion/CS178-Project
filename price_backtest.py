import pandas as pd
import yfinance as yf

# -----------------------------
# Load daily sentiment signals
# -----------------------------
signals = pd.read_csv("daily_signals.csv")
signals["date"] = pd.to_datetime(signals["date"])

print("\nDaily sentiment signals:")
print(signals)

# -----------------------------
# Download stock prices
# -----------------------------
tickers = signals["ticker"].unique().tolist()

start_date = signals["date"].min() - pd.Timedelta(days=5)
end_date = signals["date"].max() + pd.Timedelta(days=5)

raw = yf.download(
    tickers,
    start=start_date,
    end=end_date,
    progress=False,
    auto_adjust=False
)

# Show the columns so we can see what Yahoo returned
print("\nRaw downloaded columns:")
print(raw.columns)

# raw is usually a DataFrame with multiple columns like:
# ("Adj Close", "AAPL"), ("Close", "AAPL"), etc.
# or for one ticker, columns like: Open High Low Close Adj Close Volume

# Pick a price series:
# Prefer "Adj Close" if it exists, otherwise use "Close"
if isinstance(raw.columns, pd.MultiIndex):
    # Multi-ticker case
    if "Adj Close" in raw.columns.get_level_values(0):
        prices = raw["Adj Close"]
    else:
        prices = raw["Close"]
else:
    # Single-ticker case
    if "Adj Close" in raw.columns:
        prices = raw["Adj Close"].to_frame()
    else:
        prices = raw["Close"].to_frame()

# If prices is a Series, convert to DataFrame
if isinstance(prices, pd.Series):
    prices = prices.to_frame()

print("\nPrices used (head):")
print(prices.head())

# Stop early if nothing downloaded
if prices.dropna(how="all").empty:
    raise RuntimeError(
        "No price data downloaded. This can happen from network issues, rate limits, or invalid tickers."
    )

# -----------------------------
# Compute next-day returns
# -----------------------------
prices.index = pd.to_datetime(prices.index)

returns = prices.pct_change()

# Shift so that sentiment on date D matches return from D to D+1
returns = returns.shift(-1)

# -----------------------------
# Reshape returns for merging
# -----------------------------
returns_long = (
    returns
    .reset_index()
    .melt(id_vars=returns.index.name or "index", var_name="ticker", value_name="next_day_return")
)

# Fix the date column name
returns_long = returns_long.rename(columns={returns_long.columns[0]: "date"})

# -----------------------------
# Merge sentiment with returns
# -----------------------------
data = signals.merge(returns_long, on=["ticker", "date"], how="inner")

print("\nSentiment + next-day returns:")
print(data)

# -----------------------------
# Simple evaluation
# -----------------------------
if len(data) < 2:
    print("\nNot enough merged rows to compute correlation yet.")
else:
    corr = data["daily_sentiment"].corr(data["next_day_return"])
    print("\nCorrelation between sentiment and next-day return:")
    print(corr)
