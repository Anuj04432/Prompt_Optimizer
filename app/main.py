from fastapi import FastAPI
from models.prompt import PromptRequest ,PromptResponse

app = FastAPI()

@app.post("/optimize")
def optimize():
    return {"message":"This is a prompt optimizer"}

@app.get("/")
def get(response: PromptResponse):
    return response.optimized_prompt
    

@app.post("/check")
def prompt(request: PromptRequest):
    return {"prompt":request.prompt }
        
    