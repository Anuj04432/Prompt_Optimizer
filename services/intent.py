import re
from rules.intents import intent
from services.preprocess import preprocess

# Precompile regex patterns for each keyword to maximize performance
_INTENT_PATTERNS = {}
for intent_name, keywords in intent.items():
    _INTENT_PATTERNS[intent_name] = [
        re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE)
        for kw in keywords
    ]


def detect_intent(prompt: str) -> dict:
    """
    Detects user intent using normalized keyword boundary matching.
    Returns:
        {"intents": ["code", "python", ...]} or {"intents": []}
    """
    if not prompt or not prompt.strip():
        return {"intents": []}

    cleaned = preprocess(prompt)
    detected = []

    for intent_name, patterns in _INTENT_PATTERNS.items():
        for pattern in patterns:
            # Check pattern against both normalized text and original prompt
            if pattern.search(cleaned) or pattern.search(prompt):
                detected.append(intent_name)
                break  # Matched this category, move to next category

    # Preserve order while ensuring uniqueness
    seen = set()
    unique_intents = [i for i in detected if not (i in seen or seen.add(i))]

    return {"intents": unique_intents}
