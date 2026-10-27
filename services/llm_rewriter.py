import os
import re
from typing import AsyncGenerator
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI

load_dotenv()

_sync_client = None
_async_client = None

def get_model() -> str:
    return os.environ.get("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")

SYSTEM_PROMPT = """You are a world-class prompt engineering expert.
Your mission is to rewrite the user's raw prompt so that it yields the highest quality, most structured, and accurate response from an LLM.

Guidelines:
1. Preserve the user's core intent, requested language/format, and constraints exactly.
2. If an expert role or guidelines are provided, integrate them seamlessly into the rewritten prompt structure.
3. Enhance specificity and clarity without fabricating unrequested features or hallucinations.
4. Add clear output formatting expectations (e.g. structured markdown, step-by-step logic, edge cases) where helpful.
5. Return ONLY the rewritten prompt. Do NOT wrap in quotes. Do NOT include any preamble like "Here is the rewritten prompt:".
"""

USER_TEMPLATE = """Target Persona / Role: {role}
Domain Guidelines:
{instructions}

Raw User Prompt:
{prompt}
"""

_PREAMBLE_PATTERN = re.compile(
    r"^(here('s| is)\s+(a|the)?\s*(rewritten|revised|updated|new)?\s*prompt[^:]*:|"
    r"sure[,!]?[^:]*:|okay[,!]?[^:]*:|certainly[,!]?[^:]*:)\s*",
    re.IGNORECASE,
)


def _get_api_key() -> str | None:
    return os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")


def _get_base_url() -> str:
    return os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")


def _get_sync_client() -> OpenAI | None:
    global _sync_client
    api_key = _get_api_key()
    if not api_key:
        return None
    if _sync_client is None:
        _sync_client = OpenAI(
            base_url=_get_base_url(),
            api_key=api_key,
        )
    return _sync_client


def _get_async_client() -> AsyncOpenAI | None:
    global _async_client
    api_key = _get_api_key()
    if not api_key:
        return None
    if _async_client is None:
        _async_client = AsyncOpenAI(
            base_url=_get_base_url(),
            api_key=api_key,
        )
    return _async_client


def _clean_llm_output(text: str) -> str:
    text = text.strip()
    text = _PREAMBLE_PATTERN.sub("", text).strip()
    # Strip a single pair of wrapping quotes if the whole text is enclosed
    if len(text) >= 2 and text[0] in "\"'" and text[-1] in "\"'":
        text = text[1:-1].strip()
    return text


def _build_messages(prompt: str, role: str | None, instructions: list[str]) -> list[dict]:
    instructions_block = "\n".join(f"- {i}" for i in instructions) if instructions else "- Be clear, direct, and rigorous."
    user_content = USER_TEMPLATE.format(
        role=role or "General AI Assistant",
        instructions=instructions_block,
        prompt=prompt,
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def _compose_without_llm(prompt: str, role: str | None, instructions: list[str]) -> str:
    parts = []
    if role:
        parts.append(role)
    if instructions:
        parts.append("Follow these guidelines: " + "; ".join(instructions) + ".")
    parts.append(f"Task: {prompt}")
    return " ".join(parts)


def llm_rewrite(prompt: str, role: str | None, instructions: list[str]) -> str:
    """Synchronous LLM prompt rewriting with fallback."""
    client = _get_sync_client()
    if client is None:
        return _compose_without_llm(prompt, role, instructions)

    messages = _build_messages(prompt, role, instructions)
    response = client.chat.completions.create(
        model=get_model(),
        max_tokens=600,
        temperature=0.3,
        messages=messages,
    )
    raw = response.choices[0].message.content or ""
    return _clean_llm_output(raw)


async def async_llm_rewrite(prompt: str, role: str | None, instructions: list[str]) -> str:
    """Asynchronous LLM prompt rewriting (non-blocking for FastAPI)."""
    client = _get_async_client()
    if client is None:
        return _compose_without_llm(prompt, role, instructions)

    messages = _build_messages(prompt, role, instructions)
    response = await client.chat.completions.create(
        model=get_model(),
        max_tokens=600,
        temperature=0.3,
        messages=messages,
    )
    raw = response.choices[0].message.content or ""
    return _clean_llm_output(raw)


async def async_llm_rewrite_stream(
    prompt: str, role: str | None, instructions: list[str]
) -> AsyncGenerator[str, None]:
    """Asynchronous generator yielding streamed tokens for real-time frontend / extension updates."""
    client = _get_async_client()
    if client is None:
        yield _compose_without_llm(prompt, role, instructions)
        return

    messages = _build_messages(prompt, role, instructions)
    stream = await client.chat.completions.create(
        model=get_model(),
        max_tokens=600,
        temperature=0.3,
        messages=messages,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if delta:
            yield delta
