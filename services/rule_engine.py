from rules.rules import rules
from services.intent import detect_intent


def rule_engine(prompt: str) -> dict:
    """
    Detects intent for the prompt, then combines the role + instructions
    of every matched intent from rules.rules into a single rule spec.

    Returns:
        {
            "intents": [...],
            "role": str | None,
            "instructions": [...]
        }
    """
    detected = detect_intent(prompt)
    matched_intents = detected["intents"] if detected != "unknown" else ["general"]

    role = None
    instructions = []

    for name in matched_intents:
        rule = rules.get(name)
        if not rule:
            continue
        if role is None and "role" in rule:
            role = rule["role"]
        instructions.extend(rule.get("instructions", []))

    if not instructions:
        instructions = rules["general"]["instructions"]

    # de-duplicate while preserving order
    seen = set()
    unique_instructions = []
    for ins in instructions:
        if ins not in seen:
            seen.add(ins)
            unique_instructions.append(ins)

    return {
        "intents": matched_intents,
        "role": role,
        "instructions": unique_instructions,
    }