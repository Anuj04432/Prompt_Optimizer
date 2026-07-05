from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Pydantic model for prompt

class PromptRequest(BaseModel):
    prompt: str 
    