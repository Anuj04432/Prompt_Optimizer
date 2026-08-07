from typing import Optional
from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    prompt: str = Field(description="Use only the strings")
    mode: Optional[str] = Field(default="hybrid", description="rules | llm | hybrid")


class PromptResponse(BaseModel):
    original_prompt: str
    optimized_prompt: str
    intent: list[str] = Field(default_factory=list)
    original_tokens: int
    optimized_tokens: int
    similarity_score: float