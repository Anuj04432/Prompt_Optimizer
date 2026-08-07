from services.preprocess import preprocess
from services.rule_engine import rule_engine
from services.llm_rewriter import llm_rewrite
from services.compressor import compress, count_tokens
from services.evaluator import similarity_score
from models.prompt import PromptResponse


def optimize_prompt(prompt: str, mode: str = "hybrid") -> PromptResponse:
    """
    mode:
      "rules" -> rule-based composition only, no LLM call (fast, free, offline)
      "llm"   -> LLM rewrite, informed by rule_spec for role/instructions
      "hybrid"-> same as "llm" for now; kept as its own mode so the rule
                 pass can be extended into a pre-cleanup step later
                 without changing the API surface
    """
    words = prompt.split()
    if len(words) < 3:
        return PromptResponse(
            original_prompt=prompt,
            optimized_prompt="Could you add a bit more detail to your prompt?",
            intent=[],
            original_tokens=count_tokens(prompt),
            optimized_tokens=0,
            similarity_score=0.0,
        )

    cleaned = preprocess(prompt)
    rule_spec = rule_engine(prompt)  # rule_engine runs its own intent detection internally

    if mode == "rules":
        rewritten = _rule_spec_to_text(rule_spec, cleaned)
    else:
        rewritten = llm_rewrite(cleaned, rule_spec["role"], rule_spec["instructions"])

    optimized = compress(rewritten)
    score = similarity_score(prompt, optimized)

    return PromptResponse(
        original_prompt=prompt,
        optimized_prompt=optimized,
        intent=rule_spec["intents"],
        original_tokens=count_tokens(prompt),
        optimized_tokens=count_tokens(optimized),
        similarity_score=score,
    )


def _rule_spec_to_text(rule_spec: dict, prompt: str) -> str:
    parts = []
    if rule_spec.get("role"):
        parts.append(rule_spec["role"])
    if rule_spec.get("instructions"):
        parts.append("Follow these guidelines: " + "; ".join(rule_spec["instructions"]) + ".")
    parts.append(f"Task: {prompt}")
    return " ".join(parts)