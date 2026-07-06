import nltk
from nltk.stem import WordNetLemmatizer

nltk.download("wordnet")
nltk.download("omw-1.4")

def grammar(prompt):
    lematizer = WordNetLemmatizer()
    word = [lematizer.lemmatize(word,pos="v") for word in prompt.split()]
    prompt =  (" ".join(word)).capitalize()

    return prompt



