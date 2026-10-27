import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from models.prompt import PromptRequest, PromptResponse
from services.intent import detect_intent
from services.preprocess import preprocess
from services.optimization import async_optimize_prompt, optimize_prompt
from services.rule_engine import rule_engine
from services.llm_rewriter import async_llm_rewrite_stream
from services.compressor import count_tokens, compress
from services.evaluator import similarity_score

app = FastAPI(
    title="Prompt Optimizer API",
    description="High-performance prompt engineering, intent classification, and token optimization engine.",
    version="1.1.0"
)

# Enable CORS for Chrome extensions (chrome-extension://*) and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check for Chrome extension and clients to verify connectivity."""
    return {"status": "ok", "version": "1.1.0"}


@app.post("/optimize", response_model=PromptResponse)
async def optimize(request: PromptRequest):
    """Asynchronous, non-blocking prompt optimization endpoint."""
    return await async_optimize_prompt(request.prompt, mode=request.mode or "hybrid")


@app.post("/optimize/stream")
async def optimize_stream(request: PromptRequest):
    """
    Streaming endpoint using Server-Sent Events (SSE).
    Streams tokens in real-time to the Chrome Extension or Web UI.
    """
    prompt = request.prompt.strip()
    mode = request.mode or "hybrid"

    async def event_generator():
        # 1. Send initial metadata (detected intents, original tokens)
        rule_spec = rule_engine(prompt)
        meta = {
            "type": "meta",
            "intents": rule_spec["intents"],
            "original_tokens": count_tokens(prompt)
        }
        yield f"data: {json.dumps(meta)}\n\n"

        accumulated_text = []

        if mode == "rules":
            # Deterministic text (instant)
            parts = []
            if rule_spec.get("role"):
                parts.append(rule_spec["role"].rstrip("."))
            if rule_spec.get("instructions"):
                formatted_ins = "; ".join(i.rstrip(".") for i in rule_spec["instructions"])
                parts.append(f"Follow these guidelines: {formatted_ins}.")
            parts.append(f"Task: {prompt}")
            full_text = " ".join(parts)
            yield f"data: {json.dumps({'type': 'chunk', 'text': full_text})}\n\n"
            accumulated_text.append(full_text)
        else:
            # Stream LLM tokens
            async for chunk in async_llm_rewrite_stream(prompt, rule_spec["role"], rule_spec["instructions"]):
                accumulated_text.append(chunk)
                yield f"data: {json.dumps({'type': 'chunk', 'text': chunk})}\n\n"

        full_rewritten = "".join(accumulated_text)
        optimized = compress(full_rewritten)
        score = similarity_score(prompt, optimized)

        # 2. Send final completion event with metrics
        done_payload = {
            "type": "done",
            "optimized_prompt": optimized,
            "optimized_tokens": count_tokens(optimized),
            "similarity_score": score
        }
        yield f"data: {json.dumps(done_payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/findintent/{prompt}")
def check_intent(prompt: str):
    """Utility endpoint to test intent detection."""
    result = detect_intent(prompt)
    return {
        "prompt": prompt,
        "intents": result.get("intents", []),
    }


@app.get("/preprocess/{prompt}")
def get_preprocess(prompt: str):
    """Utility endpoint to inspect normalized lemmatized tokens."""
    return {
        "original": prompt,
        "preprocessed": preprocess(prompt),
    }


# Mount the frontend directory
FRONTEND_DIR = Path(__file__).parent / "Frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
