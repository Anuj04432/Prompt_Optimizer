import re
from nltk.corpus import stopwords

_STOPWORDS = None


def _get_stopwords():
    global _STOPWORDS
    if _STOPWORDS is None:
        _STOPWORDS = set(stopwords.words("english"))
    return _STOPWORDS


def _content_words(text: str) -> set:
    """Lowercased alphabetic words, minus stopwords and very short words."""
    words = re.findall(r"[a-zA-Z]+", text.lower())
    stop = _get_stopwords()
    return {w for w in words if w not in stop and len(w) > 2}


def similarity_score(original: str, optimized: str) -> float:
    """
    Keyword-retention score: what fraction of the ORIGINAL prompt's content
    words survive somewhere in the optimized prompt.

    This replaces a plain TF-IDF cosine similarity, which penalized
    legitimate rewrite expansion just as much as genuine topic drift — a
    5-word prompt honestly expanded into a full paragraph would score low
    even with perfect fidelity, making it impossible to separate "good
    rewrite" from "hallucinated rewrite" by score alone.

    Recall against the original's own content words isn't penalized by
    length or added structure, only by the original subject actually
    disappearing — which is the failure mode we're trying to catch.
    """
    orig_words = _content_words(original)
    if not orig_words:
        return 1.0  # nothing meaningful in the original to check drift against

    opt_words = _content_words(optimized)
    retained = orig_words & opt_words
    return round(len(retained) / len(orig_words), 3)