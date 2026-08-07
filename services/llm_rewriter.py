import os
from openai import OpenAI

_client = None
_MODEL = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")

META_PROMPT = """You are a prompt engineering expert. Rewrite the user's prompt so it is \
clear, specific, and well structured for an LLM to follow.

Rules:
- Preserve the user's original intent and requested output type. Do not add facts or \
requirements they didn't imply.
- If a role or instructions are provided below, weave them naturally into the rewritten \
prompt instead of just listing them.
- Remove redundancy and filler. Keep it as short as possible without losing meaning.
- Return ONLY the rewritten prompt text. No preamble, no explanation, no quotes around it.

Suggested role: {role}
Suggested instructions:
{instructions}

Original prompt:
{prompt}
"""


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            return None
        _client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    return _client


def llm_rewrite(prompt: str, role: str | None, instructions: list[str]) -> str:
    client = _get_client()

    if client is None:
        # No API key configured — fall back to a deterministic, rule-only
        # composition so the pipeline still works offline.
        return _compose_without_llm(prompt, role, instructions)

    instructions_block = "\n".join(f"- {i}" for i in instructions) or "- Be clear and concise."

    response = client.chat.completions.create(
        model=_MODEL,
        max_tokens=400,
        messages=[
            {
                "role": "user",
                "content": META_PROMPT.format(
                    role=role or "N/A",
                    instructions=instructions_block,
                    prompt=prompt,
                ),
            }
        ],
    )

    return response.choices[0].message.content.strip()


def _compose_without_llm(prompt: str, role: str | None, instructions: list[str]) -> str:
    parts = []
    if role:
        parts.append(role)
    if instructions:
        parts.append("Follow these guidelines: " + "; ".join(instructions) + ".")
    parts.append(f"Task: {prompt}")
    return " ".join(parts)