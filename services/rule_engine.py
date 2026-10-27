from rules.rules import rules
from services.intent import detect_intent


def rule_engine(prompt: str) -> dict:
    """
    Detects intents for the prompt, then combines the role and instructions
    of every matched intent from rules.rules into a single unified rule spec.

    Returns:
        {
            "intents": [...],
            "role": str | None,
            "instructions": [...]
        }
    """
    detected = detect_intent(prompt)
    matched_intents = detected.get("intents") or []
    if not matched_intents:
        matched_intents = ["general"]

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

    # De-duplicate while preserving insertion order
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
