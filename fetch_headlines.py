import urllib.parse
from datetime import datetime, timezone
import feedparser
import pandas as pd

# Change this list to whatever tickers you want
TICKERS = ["AAPL", "TSLA"]

# How many RSS items to request per ticker each time you run it
ITEMS_PER_TICKER = 30

# Name of the file where we will save the data
OUTPUT_CSV = "headlines.csv"


def google_news_rss_url(ticker: str) -> str:
    """
    Build a Google News RSS query for a stock ticker.
    This is not official finance data. It is a convenient free headline source.
    """
    query = f"{ticker} stock" # Example: "AAPL stock"
    q = urllib.parse.quote(query) # Convert to URL-safe format
    return f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


def parse_time(entry) -> str:
    """
    Try to get a timestamp from the RSS entry.
    If missing, use current UTC time.
    Returns time as a string like '2026-01-20 09:15:00'.
    """
    # If the article has a published time, use it
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

    # If not, try using updated time
    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
        dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
    else: # If no time at all, use current time
        dt = datetime.now(timezone.utc)

    # Store as a simple timestamp string
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def load_existing() -> pd.DataFrame:
    """
    Load existing headlines.csv if it exists.
    If it does not exist, return an empty table with the right columns.
    """
    try:
        df = pd.read_csv(OUTPUT_CSV) # Try to read file
        # Make sure required columns exist
        needed = {"time", "ticker", "text", "link"}
        for col in needed:
            if col not in df.columns:
                df[col] = ""
        return df[["time", "ticker", "text", "link"]]  # Return only the columns we care about
    except FileNotFoundError:
        return pd.DataFrame(columns=["time", "ticker", "text", "link"])  # If file does not exist, return empty table


def main():
    existing = load_existing() # Load old data

    new_rows = [] # Store new data here

    for ticker in TICKERS:  # Loop through each stock ticker
        url = google_news_rss_url(ticker) # Get RSS link
        feed = feedparser.parse(url) # Read RSS feed

        # Take only a limited number of items to avoid huge files
        for entry in feed.entries[:ITEMS_PER_TICKER]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()

            # Skip empty items
            if not title:
                continue

            time_str = parse_time(entry)

            # Save the data in a dictionary
            new_rows.append({
                "time": time_str,
                "ticker": ticker,
                "text": title,
                "link": link
            })

    # Convert new data into a table
    new_df = pd.DataFrame(new_rows)

    # Combine old + new
    combined = pd.concat([existing, new_df], ignore_index=True)

    # Remove duplicates so running this multiple times does not spam the CSV
    # Using text + link is a simple dedupe key
    combined = combined.drop_duplicates(subset=["ticker", "text", "link"], keep="first")

    # Sort newest first by time (string sort works because we used YYYY-MM-DD HH:MM:SS)
    combined = combined.sort_values(by="time", ascending=False)

    # Save back to headlines.csv
    combined.to_csv(OUTPUT_CSV, index=False)

    # Print results
    print(f"Saved {len(new_df)} fetched rows.")
    print(f"Total rows in {OUTPUT_CSV}: {len(combined)}")

# Run the program
if __name__ == "__main__":
    main()
