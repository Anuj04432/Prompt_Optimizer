import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = None
_MODEL = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")

SYSTEM_PROMPT = """You are a prompt engineering expert. Rewrite the user's prompt so it is \
clear, specific, and well structured for an LLM to follow.

Rules:
- Preserve the user's original intent and requested output type exactly.
- Do NOT add facts, topics, examples, or requirements the user did not state or clearly imply.
- If a role or instructions are provided, weave them naturally into the rewritten prompt \
instead of just listing them.
- Remove redundancy and filler. Keep it as short as possible without losing meaning.
- Return ONLY the rewritten prompt text itself. Do not include any preamble such as \
"Here is the rewritten prompt:", do not explain what you did, and do not wrap the \
result in quotation marks.
"""

USER_TEMPLATE = """Suggested role: {role}
Suggested instructions:
{instructions}

Original prompt:
{prompt}
"""

# Catches leading filler like "Here is the rewritten prompt:", "Sure, here's ...:",
# "Okay, here is ...:" that models add despite being told not to.
_PREAMBLE_PATTERN = re.compile(
    r"^(here('s| is)\s+(a|the)?\s*(rewritten|revised|updated|new)?\s*prompt[^:]*:|"
    r"sure[,!]?[^:]*:|okay[,!]?[^:]*:|certainly[,!]?[^:]*:)\s*",
    re.IGNORECASE,
)


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


def _clean_llm_output(text: str) -> str:
    text = text.strip()
    text = _PREAMBLE_PATTERN.sub("", text).strip()
    # strip a single layer of wrapping quotes if the whole output is quoted
    if len(text) >= 2 and text[0] in "\"'" and text[-1] in "\"'":
        text = text[1:-1].strip()
    return text


def llm_rewrite(prompt: str, role: str | None, instructions: list[str]) -> str:
    client = _get_client()

    if client is None:
        return _compose_without_llm(prompt, role, instructions)

    instructions_block = "\n".join(f"- {i}" for i in instructions) or "- Be clear and concise."

    response = client.chat.completions.create(
        model=_MODEL,
        max_tokens=400,
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_TEMPLATE.format(
                    role=role or "N/A",
                    instructions=instructions_block,
                    prompt=prompt,
                ),
            },
        ],
    )

    raw = response.choices[0].message.content.strip()
    return _clean_llm_output(raw)


def _compose_without_llm(prompt: str, role: str | None, instructions: list[str]) -> str:
    parts = []
    if role:
        parts.append(role)
    if instructions:
        parts.append("Follow these guidelines: " + "; ".join(instructions) + ".")
    parts.append(f"Task: {prompt}")
    return " ".join(parts)