#Import the pipeline tool from the transformers library
#A pipeline is a ready-made wrapper that handles loading the model,
#tokenizing text, running the model, and returning results
from transformers import pipeline


#Create a sentiment analysis pipeline using FinBERT
# - "sentiment-analysis" tells transformers what task we want
# - model and tokenizer both point to the FinBERT model trained on finance text
# - return_all_scores=True means we get scores for positive, negative, and neutral

#Essentially, downloads a pre trained FinBERT model from an online model library 
# and sets it up so I can give it text and ask,
# “Does this sound positive, negative, or neutral?”
# The pipeline function does all the hard work, like loading the model, 
# preparing the text, running the model, and giving back easy to read results.
pipe = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert",
    tokenizer="ProsusAI/finbert",
    return_all_scores=True
)


#Define a function that takes in text and returns a single sentiment number
def score(text: str) -> float:
    #Run the FinBERT model on the input text
    #The result is a list, so we take the first item with [0]
    out = pipe(text)[0]

    #Convert the model output into a dictionary
    #Example: {"positive": 0.90, "negative": 0.05, "neutral": 0.05}
    d = {x["label"].lower(): x["score"] for x in out}

    #Return a single sentiment score
    #Positive score = good news
    #Negative score = bad news
    #Near zero = neutral
    return d["positive"] - d["negative"]


#Create a list of example headlines to test the model
tests = [
    "Apple creates new M5 chip that will double performance",
    "Apple beats earnings expectations and raises guidance.",
    "Tesla faces investigation after reported crash.",
    "Company reports results in line with estimates."
]


#Loop through each test headline and print sentiment score w/ the original text
for t in tests:
    print(score(t), "|", t)