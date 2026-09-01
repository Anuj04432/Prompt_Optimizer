from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from models.prompt import PromptRequest, PromptResponse
from services.intent import detect_intent
from services.preprocess import preprocess
from services.optimization import optimize_prompt

app = FastAPI(
    title="Prompt Optimizer API",
    description="Intelligent prompt engineering, intent classification, and token optimization engine.",
    version="1.0.0"
)

# Allows the frontend (opened as a local HTML file, or served from a
# different port) to call this API. "*" is fine for local development;
# restrict this to your real domain before deploying publicly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent / "Frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/style.css", include_in_schema=False)
    def serve_css():
        return FileResponse(FRONTEND_DIR / "style.css")

    @app.get("/app.js", include_in_schema=False)
    def serve_js():
        return FileResponse(FRONTEND_DIR / "app.js")


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