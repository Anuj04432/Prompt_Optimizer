from fastapi import FastAPI
from models.prompt import PromptRequest, PromptResponse
from services.intent import detect_intent
from services.preprocess import preprocess
from services.optimization import optimize_prompt

app = FastAPI()


@app.post("/optimize", response_model=PromptResponse)
def optimize(request: PromptRequest):
    return optimize_prompt(request.prompt, mode=request.mode)


@app.get("/findintent/{prompt}")
def check_intent(prompt: str):
    intent = detect_intent(prompt)
    return {
        "prompt": prompt,
        "intent": intent,
    }


@app.get("/preprocess/{prompt}")
def get_preprocess(prompt: str):
    pre = preprocess(prompt)
    return {
        "optimized prompt": pre,
    }