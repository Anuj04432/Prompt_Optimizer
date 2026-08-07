from nltk.corpus import stopwords

# nltk.download("stopwords")  # run once if not already downloaded

_STOPWORDS = None
_FILLER = {"just", "really", "very", "actually", "basically", "please", "kindly"}


def _get_stopwords():
    global _STOPWORDS
    if _STOPWORDS is None:
        _STOPWORDS = set(stopwords.words("english"))
    return _STOPWORDS


def count_tokens(text: str) -> int:
    """Rough word-based token estimate. Swap for tiktoken if you need
    exact per-model counts later."""
    return len(text.split())


def compress(text: str, max_ratio: float = 0.85) -> str:
    """
    Strips low-value filler words when the prompt is long enough to
    safely trim. Never compresses below max_ratio of the original word
    count, so short/dense prompts are left untouched.
    """
    words = text.split()
    original_len = len(words)

    if original_len <= 8:
        return text

    filler = _FILLER
    kept = [w for w in words if w.strip(".,!?").lower() not in filler]

    if len(kept) < original_len * max_ratio:
        return text

    return " ".join(kept)