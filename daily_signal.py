#Import pandas: used to work with tables of data (CSV files)
import pandas as pd

#Import the pipeline helper from transformers (allows me to easily load and use a pre trained NLP model)
from transformers import pipeline

#Create a FinBERT sentiment analysis pipeline, same as finbert_test.py
pipe = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert",
    tokenizer="ProsusAI/finbert",
    top_k=None
)

#Define function that turns text into sentiment number
def sentiment_score(text: str) -> float:
    #This function takes one headline as input and returns a single number representing sentiment

    #Positive number = positive news
    #Negative number = negative news
    #Near zero = neutral news

    #Run the FinBERT model on the text, result is a list of dictionaries with sentiment labels and scores
    scores = pipe(text)[0]

    #Convert the list of scores into a dictionary
    #Example result:{"positive": 0.90, "negative": 0.05, "neutral": 0.05}
    d = {s["label"].lower(): s["score"] for s in scores}

    #Create one simple sentiment value
    #We subtract negative from positive
    return d["positive"] - d["negative"]

#Read the CSV file that contains headlines
df = pd.read_csv("headlines.csv")

#Convert the time column from text into a datetime object
#Extracts dates and group by day later
df["time"] = pd.to_datetime(df["time"], errors="coerce")
df = df.dropna(subset=["time"])

#Apply the sentiment_score function to every headline
#This creates a new column called "sentiment"
df["sentiment"] = df["text"].apply(sentiment_score)

#Create a new column that keeps only the date
#This is used to group all headlines from the same day
df["date"] = df["time"].dt.date

#Group the data by ticker and date
#Then take the average sentiment for that day
#This becomes the daily trading signal
daily = (
    df.groupby(["ticker", "date"])["sentiment"]
      .mean()
      .reset_index()
      .rename(columns={"sentiment": "daily_sentiment"})
)

#Print the scored headlines so you can see individual results
print("\nScored headlines:")
print(df[["time", "ticker", "sentiment", "text"]])

#Print the daily signals table
print("\nDaily signals:")
print(daily)

#Save the scored headlines to a CSV file
#Reuses the data later without re running FinBERT
df.to_csv("headlines_scored.csv", index=False)

#Save the daily sentiment signals to another CSV file
daily.to_csv("daily_signals.csv", index=False)

#Prints tha files were saved successfully
print("\nSaved: headlines_scored.csv and daily_signals.csv")
