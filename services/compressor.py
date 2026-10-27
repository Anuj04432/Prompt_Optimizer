import re

try:
    import tiktoken
    _TIKTOKEN_ENCODER = tiktoken.get_encoding("cl100k_base")
except Exception:
    _TIKTOKEN_ENCODER = None

# Low-information conversational fluff and fillers
_FILLER_WORDS = {
    "basically", "actually", "literally", "kindly", "please",
    "just", "really", "very", "totally", "honestly", "simply"
}

# Common polite fluff prefixes that add no prompt engineering value
_FILLER_PHRASES = [
    re.compile(r"^(can|could)\s+you\s+(please\s+)?(help\s+me\s+)?", re.IGNORECASE),
    re.compile(r"^i\s+(would\s+like|want|need)\s+you\s+to\s+", re.IGNORECASE),
    re.compile(r"^i\s+was\s+wondering\s+if\s+you\s+could\s+", re.IGNORECASE),
    re.compile(r"^(please\s+)?help\s+me\s+(to\s+)?", re.IGNORECASE),
]


def count_tokens(text: str) -> int:
    """
    Returns exact BPE token count using tiktoken (cl100k_base).
    Falls back to a calibrated word-count multiplier if tiktoken is unavailable.
    """
    if not text:
        return 0

    if _TIKTOKEN_ENCODER is not None:
        try:
            return len(_TIKTOKEN_ENCODER.encode(text))
        except Exception:
            pass

    # Fallback estimate: 1 word ≈ 1.3 tokens for English prose & code
    return max(1, int(len(text.split()) * 1.3))


def compress(text: str, min_retained_ratio: float = 0.5) -> str:
    """
    Strips low-value conversational filler words and phrases while preserving
    core semantic meaning and structure.
    """
    if not text or not text.strip():
        return text

    original_text = text.strip()
    words = original_text.split()
    original_len = len(words)

    # Don't aggressively compress very short phrases (e.g. 3 words)
    if original_len <= 4:
        return original_text

    working_text = original_text

    # 1. Strip conversational leading phrases if prompt is long enough
    if original_len > 6:
        for phrase_pat in _FILLER_PHRASES:
            new_text = phrase_pat.sub("", working_text).strip()
            if new_text and len(new_text.split()) >= 3:
                # Capitalize the first letter if stripped
                working_text = new_text[0].upper() + new_text[1:] if len(new_text) > 1 else new_text.upper()
                break

    # 2. Strip standalone filler words
    tokens = working_text.split()
    filtered_tokens = []
    for token in tokens:
        clean_word = token.strip(".,!?:;\"'()[]{}").lower()
        if clean_word in _FILLER_WORDS:
            continue
        filtered_tokens.append(token)

    # Safety guard: ensure we didn't wipe out the prompt or retain fewer words than threshold
    if len(filtered_tokens) >= max(3, int(original_len * min_retained_ratio)):
        return " ".join(filtered_tokens)

    return working_text
