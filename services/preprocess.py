import re
from nltk.stem import WordNetLemmatizer

_lemmatizer = None


def _get_lemmatizer() -> WordNetLemmatizer:
    global _lemmatizer
    if _lemmatizer is None:
        _lemmatizer = WordNetLemmatizer()
    return _lemmatizer


def preprocess(prompt: str) -> str:
    """
    Normalizes text for NLP intent detection and keyword matching:
    - Lowercases text
    - Replaces punctuation with whitespace
    - Lemmatizes verbs and nouns
    - Collapses consecutive whitespace
    """
    if not prompt:
        return ""

    lemmatizer = _get_lemmatizer()
    text = prompt.lower()

    # Replace punctuation and special characters with spaces
    text = re.sub(r"[^\w\s]", " ", text)

    words = text.split()
    processed_words = []
    for word in words:
        # First lemmatize as verb, then as noun
        v_lemma = lemmatizer.lemmatize(word, pos="v")
        n_lemma = lemmatizer.lemmatize(v_lemma, pos="n")
        processed_words.append(n_lemma)

    return " ".join(processed_words)
