from pydantic import BaseModel,Field

# Pydantic model for prompt

class PromptRequest(BaseModel):
    prompt: str = Field(description="Use only the strings")

class PromptResponse(BaseModel):
    orginal_prompt: str
    optimized_prompt: str
