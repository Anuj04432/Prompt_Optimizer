from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Pydantic model for prompt

class PromptRequest(BaseModel):
    prompt: str 

class PromptResponse(BaseModel):
    org_prompt: str
    optimized_prompt: str
