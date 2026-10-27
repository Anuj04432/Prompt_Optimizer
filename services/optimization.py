from services.rule_engine import rule_engine
from services.llm_rewriter import llm_rewrite, async_llm_rewrite
from services.compressor import compress, count_tokens
from services.evaluator import similarity_score
from models.prompt import PromptResponse

# If the LLM rewrite's semantic retention drops below this threshold,
# it is likely hallucinated or drifted, triggering deterministic rule fallback.
MIN_SIMILARITY = 0.20


def _rule_spec_to_text(rule_spec: dict, prompt: str) -> str:
    parts = []
    if rule_spec.get("role"):
        parts.append(rule_spec["role"].rstrip("."))
    if rule_spec.get("instructions"):
        formatted_ins = "; ".join(i.rstrip(".") for i in rule_spec["instructions"])
        parts.append(f"Follow these guidelines: {formatted_ins}.")
    parts.append(f"Task: {prompt}")
    return " ".join(parts)


def _handle_short_prompt(prompt: str) -> PromptResponse:
    return PromptResponse(
        original_prompt=prompt,
        optimized_prompt="Could you provide a bit more detail or context to your prompt?",
        intent=[],
        original_tokens=count_tokens(prompt),
        optimized_tokens=0,
        similarity_score=0.0,
    )


def optimize_prompt(prompt: str, mode: str = "hybrid") -> PromptResponse:
    """
    Synchronous pipeline runner:
      mode:
        "rules"  -> deterministic rule-based composition only (0 API cost, instant)
        "llm"    -> direct LLM rewrite guided by detected persona and guidelines
        "hybrid" -> LLM rewrite with automated drift protection falling back to rules
    """
    user_prompt = prompt.strip()
    words = user_prompt.split()
    if len(words) < 3:
        return _handle_short_prompt(user_prompt)

    rule_spec = rule_engine(user_prompt)
    rule_based_text = _rule_spec_to_text(rule_spec, user_prompt)

    if mode == "rules":
        rewritten = rule_based_text
    else:
        rewritten = llm_rewrite(user_prompt, rule_spec["role"], rule_spec["instructions"])
        if mode == "hybrid":
            score = similarity_score(user_prompt, rewritten)
            if score < MIN_SIMILARITY:
                rewritten = rule_based_text  # Semantic drift detected, fallback to rules

    optimized = compress(rewritten)
    score = similarity_score(user_prompt, optimized)

    return PromptResponse(
        original_prompt=user_prompt,
        optimized_prompt=optimized,
        intent=rule_spec["intents"],
        original_tokens=count_tokens(user_prompt),
        optimized_tokens=count_tokens(optimized),
        similarity_score=score,
    )


async def async_optimize_prompt(prompt: str, mode: str = "hybrid") -> PromptResponse:
    """
    Asynchronous pipeline runner for non-blocking FastAPI handling.
    """
    user_prompt = prompt.strip()
    words = user_prompt.split()
    if len(words) < 3:
        return _handle_short_prompt(user_prompt)

    rule_spec = rule_engine(user_prompt)
    rule_based_text = _rule_spec_to_text(rule_spec, user_prompt)

    if mode == "rules":
        rewritten = rule_based_text
    else:
        rewritten = await async_llm_rewrite(user_prompt, rule_spec["role"], rule_spec["instructions"])
        if mode == "hybrid":
            score = similarity_score(user_prompt, rewritten)
            if score < MIN_SIMILARITY:
                rewritten = rule_based_text

    optimized = compress(rewritten)
    score = similarity_score(user_prompt, optimized)

    return PromptResponse(
        original_prompt=user_prompt,
        optimized_prompt=optimized,
        intent=rule_spec["intents"],
        original_tokens=count_tokens(user_prompt),
        optimized_tokens=count_tokens(optimized),
        similarity_score=score,
    )
