import re
from nltk.corpus import stopwords
from services.preprocess import _get_lemmatizer

_STOPWORDS = None


def _get_stopwords() -> set:
    global _STOPWORDS
    if _STOPWORDS is None:
        try:
            _STOPWORDS = set(stopwords.words("english"))
        except Exception:
            _STOPWORDS = {
                "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
                "any", "are", "as", "at", "be", "because", "been", "before", "being", "below",
                "between", "both", "but", "by", "could", "did", "do", "does", "doing", "down",
                "during", "each", "few", "for", "from", "further", "had", "has", "have", "having",
                "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if",
                "in", "into", "is", "it", "its", "itself", "me", "more", "most", "my", "myself",
                "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
                "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so",
                "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves",
                "then", "there", "these", "they", "this", "those", "through", "to", "too", "under",
                "until", "up", "very", "was", "we", "were", "what", "when", "where", "which", "while",
                "who", "whom", "why", "with", "would", "you", "your", "yours", "yourself"
            }
    return _STOPWORDS


def _extract_lemmatized_content_words(text: str) -> set[str]:
    """
    Extracts lowercased, lemmatized alphabetic words, excluding stopwords.
    Ensures that morphological variations (e.g. 'debugging' vs 'debug') match.
    """
    words = re.findall(r"[a-zA-Z]+", text.lower())
    stop = _get_stopwords()
    lemmatizer = _get_lemmatizer()

    content_words = set()
    for w in words:
        if len(w) > 2 and w not in stop:
            # Lemmatize both verb and noun forms
            v_form = lemmatizer.lemmatize(w, pos="v")
            n_form = lemmatizer.lemmatize(v_form, pos="n")
            content_words.add(n_form)

    return content_words


def similarity_score(original: str, optimized: str) -> float:
    """
    Keyword-retention recall score: what fraction of the ORIGINAL prompt's
    key concepts survive in the optimized rewrite.
    """
    orig_words = _extract_lemmatized_content_words(original)
    if not orig_words:
        return 1.0  # Nothing substantive in the original to check drift against

    opt_words = _extract_lemmatized_content_words(optimized)
    retained = orig_words & opt_words
    return round(len(retained) / len(orig_words), 3)
