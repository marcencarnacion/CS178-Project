# FinBERT Stocks

This project uses news headlines to measure stock sentiment and see whether that sentiment relates to next-day stock price movements.

- Read financial news
- Use a pre-trained FinBERT model to score how positive or negative the news sounds
- Combine those scores into a daily sentiment signal per stock
- Compare the sentiment signal to what the stock does the next day

## How the project works

The pipeline looks like this:

1. fetch_headlines.py  
2. headlines.csv  
3. daily_signal.py  
4. headlines_scored.csv + daily_signals.csv  
5. price_backtest.py  

In other words:
1. Collect stock-related news headlines  
2. Score each headline using FinBERT  
3. Average sentiment by stock and by day  
4. Compare daily sentiment to next-day stock returns  

## Files in this project

### fetch_headlines.py
This script pulls recent news headlines from Google News RSS.

- Adds the ticker and a timestamp to each headline
- Appends new headlines to headlines.csv
- Removes duplicates so it can be run multiple times

Run this whenever there is more data.

### headlines.csv
This is the raw input data.

Each row contains:
- time the headline was published
- stock ticker
- headline text

All sentiment analysis starts from this file.

### daily_signal.py
This is the main processing script.

- Reads headlines.csv
- Runs each headline through FinBERT
- Converts model output into a single sentiment score  
  (positive score minus negative score)
- Groups headlines by stock and day
- Outputs daily sentiment signals

It creates two files:
- headlines_scored.csv
- daily_signals.csv

### headlines_scored.csv
This file stores sentiment for every individual headline.

It is mainly used for:
- debugging
- inspecting model behavior
- experimenting with different aggregation rules

### daily_signals.csv
This file contains the final daily sentiment signal.

- One row per stock per day
- This is the signal used for price analysis

### price_backtest.py
This script checks whether sentiment is useful.

- Loads daily_signals.csv
- Downloads historical stock prices from Yahoo Finance
- Computes next-day returns
- Matches sentiment on day D with price movement on day D+1
- Prints basic evaluation results like correlation

### finbert_test.py
A small test script to confirm FinBERT installs and runs correctly.

Not part of the main pipeline.

## How to run everything

Typical workflow:

1. Fetch new headlines  
   python fetch_headlines.py

2. Build daily sentiment signals  
   python daily_signal.py

3. Compare sentiment to prices  
   python price_backtest.py

Repeat this as new headlines become available.

## Interpreting sentiment values

Sentiment values usually fall between -1 and +1.

- Positive values mean the news sounds positive
- Negative values mean the news sounds negative
- Values close to zero are weak or neutral

A simple rule of thumb:
- Above +0.2 → bullish leaning
- Below -0.2 → bearish leaning
- Otherwise → neutral

## Summary

This project shows how financial news sentiment can be turned into daily stock signals and evaluated against real market data using a clean and simple Python pipeline.
