# 🚀 Prompt Optimizer

[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=flat&logo=Python&logoColor=white)](https://www.python.org/)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter%20%2F%20OpenAI-blueviolet.svg?style=flat)](https://openrouter.ai/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat)](LICENSE)

An intelligent, hybrid prompt enhancement system designed to transform vague, unstructured user prompts into clear, highly structured, and context-rich prompts tailored for Large Language Models (LLMs).

---

## 📖 Overview

Raw user prompts are often short, ambiguous, or missing crucial context, leading to generic or subpar LLM completions. **Prompt Optimizer** bridges this gap through a modular multi-stage pipeline combining **NLP intent detection**, **domain-specific rule injection**, **LLM rewriting**, **automated drift evaluation**, and **filler compression**.

---

## 🌟 Key Features

- **Multi-Mode Optimization**:
  - `hybrid` *(Default)*: Uses an LLM rewriter with automated drift protection, falling back to deterministic rules if semantic fidelity drops.
  - `rules`: Fast, 100% offline, deterministic rule-based composition (no API keys required).
  - `llm`: Direct AI rewrite guided by domain-specific roles and guidelines.
- **Intent Classification & Rule Injection**: Automatically detects intent (`code`, `sql`, `email`, `resume`, `essay`, `blog`, etc.) and injects tailored expert personas and actionable guidelines.
- **Drift & Hallucination Guard**: Uses keyword-retention similarity scoring (`services/evaluator.py`) to prevent the LLM from inventing unwarranted requirements or losing the user's original objective.
- **Prompt Compressor**: Strips conversational fluff and low-value filler words (`basically`, `please`, `kindly`) to reduce token consumption without losing meaning.
- **Interactive Web UI**: Single-page frontend to submit prompts, toggle modes, inspect token savings, and examine similarity scores in real-time.
- **Evaluation Suite**: Built-in batch test script (`test.py`) to benchmark and calibrate similarity score thresholds.

---

## 🏗️ Architecture & Pipeline Flow

```text
               ┌───────────────────────┐
               │    Raw User Prompt    │
               └───────────┬───────────┘
                           │
                           ▼
          ┌─────────────────────────────────┐
          │     1. Preprocessing (NLTK)     │  (Normalization, lemmatization)
          └────────────────┬────────────────┘
                           │
                           ▼
          ┌─────────────────────────────────┐
          │ 2. Intent Detection & Rules Spec │  (Keyword taxonomy & expert personas)
          └────────────────┬────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        ▼                                     ▼
┌──────────────┐                      ┌───────────────┐
│ "rules" Mode │                      │  "llm" Mode   │ (OpenRouter / Claude-3.5)
└───────┬──────┘                      └───────┬───────┘
        │                                     │
        │                                     ▼
        │                         ┌───────────────────────┐
        │                         │  Similarity Evaluator  │
        │                         │ (Keyword Retention)   │
        │                         └───────────┬───────────┘
        │                                     │
        │                     Score < 0.20?  ┌┴───────────────┐
        │                     (Drift Detected)│               │ Score >= 0.20
        ├────────────────────────────────────►│               │
        │                                     ▼               ▼
        │                                ┌─────────────────────────┐
        │                                │ 3. Prompt Compressor    │ (Strip filler words)
        │                                └────────────┬────────────┘
        │                                             │
        └─────────────────────────────────────────────┴────────┐
                                                               ▼
                                                  ┌────────────────────────┐
                                                  │   Optimized Prompt +   │
                                                  │  Tokens & Metrics Meta │
                                                  └────────────────────────┘
```

---

## 📂 Project Structure

```bash
Prompt_Optimizer/
├── Frontend/
│   └── index.html             # Interactive web UI client
├── models/
│   └── prompt.py              # Pydantic request and response schemas
├── rules/
│   ├── intents.py             # Intent keyword dictionaries (code, email, etc.)
│   └── rules.py               # Domain expert personas and instruction templates
├── services/
│   ├── compressor.py          # Filler word removal and token estimator
│   ├── evaluator.py           # Content-retention similarity metric
│   ├── intent.py              # Intent extraction service
│   ├── llm_rewriter.py        # OpenRouter API client for AI prompt rewriting
│   ├── optimization.py        # Master pipeline orchestrator & mode handler
│   ├── preprocess.py          # NLTK-based text normalization and lemmatizer
│   └── rule_engine.py         # Multi-intent rule aggregator and de-duplicator
├── main.py                    # FastAPI application and route endpoints
├── test.py                    # Evaluation & threshold calibration script
├── pyproject.toml             # Project configuration and dependencies
├── requirement.txt            # Package requirements list
└── .env                       # Environment variables
```

---

## ⚙️ Optimization Modes

| Mode | Description | Latency | API Usage | Recommended Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **`hybrid`** | Rewrites with LLM and verifies retention. Falls back to rules if drift occurs. | Moderate | Yes (with fallback) | Production general use. |
| **`rules`** | Deterministic rule composition based on detected intents and personas. | Instant | None (Offline) | Local environments, zero-cost tasks. |
| **`llm`** | Direct LLM rewrite using prompt engineering and system guidelines. | Moderate | Yes | Maximum creative restructuring. |

---

## 🚀 Getting Started

### 1. Prerequisites
- Python `3.12` or higher
- An OpenRouter API Key (optional, required only for `llm` and `hybrid` modes)

### 2. Installation

Clone the repository and install dependencies:

```bash
# Clone the repository
git clone https://github.com/your-username/Prompt_Optimizer.git
cd Prompt_Optimizer

# Create and activate a virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install required packages
pip install -r requirement.txt
```

Download required NLTK data (run once in Python):
```python
import nltk
nltk.download("wordnet")
nltk.download("omw-1.4")
nltk.download("stopwords")
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-haiku
```

### 4. Running the Backend API

Start the FastAPI development server:

```bash
uvicorn main:app --reload --port 8000
```

The API will be live at `http://127.0.0.1:8000` (Interactive Swagger docs available at `http://127.0.0.1:8000/docs`).

### 5. Running the Frontend

Open [`Frontend/index.html`](Frontend/index.html) directly in any modern web browser or serve it via a local static file server:

```bash
# Example using Python's built-in HTTP server
python -m http.server 3000 --directory Frontend
```
Navigate to `http://127.0.0.1:3000` in your browser.

---

## 🔌 API Reference

### `POST /optimize`
Optimizes a prompt according to the selected mode.

#### Request Body
```json
{
  "prompt": "write a python function for binary search and explain it",
  "mode": "hybrid"
}
```

#### Response
```json
{
  "original_prompt": "write a python function for binary search and explain it",
  "optimized_prompt": "You are an expert software developer. Write clean and readable Python code implementing binary search. Follow PEP 8 guidelines, handle edge cases, and provide an explanation of the logic and complexity.",
  "intent": ["code", "python", "explain"],
  "original_tokens": 10,
  "optimized_tokens": 33,
  "similarity_score": 0.857
}
```

---

### Diagnostic Endpoints

- **`GET /findintent/{prompt}`**: Returns the intent classification for the provided prompt.
- **`GET /preprocess/{prompt}`**: Returns the cleaned, lemmatized version of the prompt.

---

## 🧪 Evaluation & Calibration

Run the evaluation script to test similarity score distributions across sample prompts and calibrate the `MIN_SIMILARITY` threshold in [`services/optimization.py`](services/optimization.py):

```bash
python test.py
```

---

## 🛣️ Future Roadmap

- [ ] Support for custom user-defined rule profiles.
- [ ] Context-aware few-shot prompt injection.
- [ ] Exact token counter integration with `tiktoken`.
- [ ] Multi-turn prompt memory and refinement history.

---

## 📄 License

This project is licensed under the MIT License.