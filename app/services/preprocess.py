from rules.rules import rules
import nltk
from nltk.stem import WordNetLemmatizer
import re

# nltk.download("wordnet")
# nltk.download("omw-1.4")


def preprocess(prompt):
    lematize = WordNetLemmatizer()
    prompt = prompt.lower()



    prompt = re.sub(r"[,.<>/^;()\[\]{}\"]","",prompt)
    prompt = [lematize.lemmatize(word,pos = "v") for word in prompt.split()]
    
    return " ".join(prompt)

print(preprocess("I want to/? sbkd() learn python today"))

