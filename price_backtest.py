# Library for working with tables (dataframes)
import pandas as pd
# Library to download stock data from Yahoo Finance
import yfinance as yf

# Load daily sentiment signals
signals = pd.read_csv("daily_signals.csv")
# Convert the "date" column into proper date format
signals["date"] = pd.to_datetime(signals["date"])

# Print the sentiment data so we can see it
print("\nDaily sentiment signals:")
print(signals)

# Download stock prices
# Get a list of all unique stock tickers in the data
tickers = signals["ticker"].unique().tolist()

# Start date slightly before the earliest sentiment date
start_date = signals["date"].min() - pd.Timedelta(days=5)
# End date slightly after the latest sentiment date
end_date = signals["date"].max() + pd.Timedelta(days=5)

# Download stock price data from Yahoo Finance
raw = yf.download(
    tickers,
    start=start_date,
    end=end_date,
    progress=False, # Do not show download progress bar
    auto_adjust=False # Use raw prices (no adjustments)
)

# Show the columns so we can see what Yahoo returned
print("\nRaw downloaded columns:")
print(raw.columns)

# Raw is usually a DataFrame with multiple columns like:
# ("Adj Close", "AAPL"), ("Close", "AAPL"), etc
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

# Compute next-day returns
prices.index = pd.to_datetime(prices.index)

returns = prices.pct_change()

# Shift so that sentiment on date D matches return from D to D+1
returns = returns.shift(-1)

# Reshape returns for merging
returns_long = (
    returns
    .reset_index() # Move date index into a column
    # Convert wide table = long table
    .melt(id_vars=returns.index.name or "index", var_name="ticker", value_name="next_day_return")
)

# Rename the first column to "date"
returns_long = returns_long.rename(columns={returns_long.columns[0]: "date"})

# Merge sentiment with returns
data = signals.merge(returns_long, on=["ticker", "date"], how="inner")

# Print combined dataset
print("\nSentiment + next-day returns:")
print(data)

# Simple evaluation
# Check if we have enough data to analyze
if len(data) < 2:
    print("\nNot enough merged rows to compute correlation yet.")
else:
    # Compute correlation between sentiment and next-day returns
    corr = data["daily_sentiment"].corr(data["next_day_return"])
    print("\nCorrelation between sentiment and next-day return:")
    print(corr)
