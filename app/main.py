from fastapi import FastAPI
from models.prompt import PromptRequest ,PromptResponse
from services.intent import detect_intent
from services.preprocess import optimize

app = FastAPI()

@app.post("/optimize")
def home():
    return {"message":"This is a prompt optimizer"}

@app.get("/")
def get(response: PromptResponse):
    return response.optimized_prompt
    

@app.post("/check")
def prompt(request: PromptRequest):
    return {"prompt":request.prompt }

@app.get("/findintent/{prompt}")

def check_intent(prompt: str):
    intent = detect_intent(prompt)

    return {
        "prompt":prompt,
        "intent":intent
    }

@app.get("/preprocess/{prompt}")
def get_preprocess(prompt: str):
    pre = optimize(prompt)

    return {
        "optimized prompt":pre
    }

    