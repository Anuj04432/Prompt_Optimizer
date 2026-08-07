from services.preprocess import preprocess
from services.rule_engine import rule_engine
from services.llm_rewriter import llm_rewrite
from services.compressor import compress, count_tokens
from services.evaluator import similarity_score
from models.prompt import PromptResponse

# If the LLM rewrite's similarity to the original prompt drops below this,
# we don't trust it — the model likely drifted or hallucinated content that
# wasn't in the original ask, so fall back to the safer rule-based version.
MIN_SIMILARITY = 0.20


def optimize_prompt(prompt: str, mode: str = "hybrid") -> PromptResponse:
    """
    mode:
      "rules" -> rule-based composition only, no LLM call (fast, free, offline)
      "llm"   -> LLM rewrite, informed by rule_spec for role/instructions
      "hybrid"-> LLM rewrite with an automatic fallback to the rule-based
                 version if the rewrite drifts too far from the original
                 (similarity_score < MIN_SIMILARITY)
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
    rule_based_text = _rule_spec_to_text(rule_spec, cleaned)

    if mode == "rules":
        rewritten = rule_based_text
    else:
        rewritten = llm_rewrite(cleaned, rule_spec["role"], rule_spec["instructions"])

        if mode == "hybrid":
            score = similarity_score(prompt, rewritten)
            if score < MIN_SIMILARITY:
                rewritten = rule_based_text  # LLM drifted too far, use the safe fallback

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