#!/usr/bin/env python3.11
"""
OpenClaw Multi-Model Router

Three-way routing: Gemma 4 31B (general) / Qwen 2.5 Coder 32B (code) / Claude (complex).
Exposes an OpenAI-compatible /v1/chat/completions endpoint.

Heuristic complexity scorer routes simple chat to local Gemma, code to local Qwen,
and complex reasoning / long input / personal context to the Claude API.
Force-route by setting the request's `model` field to one of the aliases below.

Tune COMPLEXITY_THRESHOLD to taste — higher means more requests stay local.
"""

import os
import re
import json
import time
import logging
from typing import Optional
import litellm
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("openclaw-router")

GEMMA_MODEL = "ollama/gemma4:31b"
QWEN_MODEL = "ollama/qwen2.5-coder:32b"
CLAUDE_MODEL = "anthropic/claude-sonnet-4-6"
COMPLEXITY_THRESHOLD = 0.28
OLLAMA_BASE_URL = "http://localhost:11434"

CODE_PATTERNS = [
    r"\bcode\b", r"\bscript\b", r"\bfunction\b", r"\bclass\b", r"\bapi\b",
    r"\bpython\b", r"\bjavascript\b", r"\btypescript\b", r"\bbash\b", r"\bsql\b",
    r"\bdebug\b", r"\brefactor\b", r"\bimplement\b", r"\bprogram\b",
    r"\bloop\b", r"\barray\b", r"\bvariable\b", r"\bmodule\b", r"\blibrary\b",
    r"\bgit\b", r"\bdocker\b", r"\bregex\b", r"\bjson\b", r"\bhtml\b", r"\bcss\b",
    r"```",
]
_code_re = [re.compile(p, re.IGNORECASE) for p in CODE_PATTERNS]

COMPLEX_PATTERNS = [
    r"\bstep[- ]by[- ]step\b", r"\bplan\b", r"\bstrategy\b", r"\barchitect\b",
    r"\bdebu\w+\b", r"\brefactor\b", r"\bimplementat\w+\b", r"\balgorithm\b",
    r"\boptimiz\w+\b", r"\bdesign pattern\b",
    r"\banalyze\b", r"\banalysi\w+\b", r"\bevaluat\w+\b", r"\bcompar\w+\b",
    r"\btradeoffs?\b", r"\btrade-offs?\b", r"\bpros and cons\b",
    r"\bresearch\b", r"\bsynthesiz\w+\b", r"\bsummariz\w+ (this|the)\b",
    r"\bessay\b", r"\breport\b", r"\bproposal\b", r"\bpresentation\b",
    r"\bmachine learning\b", r"\bpipeline\b", r"\bneural network\b", r"\bcryptograph\w+\b",
    r"\bsecurity\b", r"\bvulnerabilit\w+\b",
    r"\bcalculate\b", r"\bderive\b", r"\bprove\b", r"\bintegral\b", r"\bderivative\b",
]

SIMPLE_PATTERNS = [
    r"\bwhat is\b", r"\bwho is\b", r"\bwhen (was|is|did)\b", r"\bwhere is\b",
    r"\bdefine\b", r"\bhow (do|does) .{1,30} work\b",
    r"\bhi\b", r"\bhello\b", r"\bthanks\b", r"\bthank you\b",
    r"\btell me a joke\b", r"\bweather\b",
]

_complex_re = [re.compile(p, re.IGNORECASE) for p in COMPLEX_PATTERNS]
_simple_re = [re.compile(p, re.IGNORECASE) for p in SIMPLE_PATTERNS]

litellm.verbose = False


def complexity_score(messages: list[dict]) -> float:
    user_texts = [m.get("content", "") for m in messages if m.get("role") == "user"]
    full_text = " ".join(user_texts)
    score = 0.0

    total_chars = len(full_text)
    if total_chars > 2000:
        score += 0.4
    elif total_chars > 800:
        score += 0.25
    elif total_chars > 300:
        score += 0.1

    complex_hits = sum(1 for p in _complex_re if p.search(full_text))
    simple_hits = sum(1 for p in _simple_re if p.search(full_text))
    score += min(complex_hits * 0.15, 0.45)
    score -= min(simple_hits * 0.15, 0.3)

    if len([m for m in messages if m.get("role") == "user"]) > 4:
        score += 0.1
    if "```" in full_text or full_text.count("\n") > 10:
        score += 0.2

    return max(0.0, min(1.0, score))


def is_code_request(messages: list[dict]) -> bool:
    user_texts = [m.get("content", "") for m in messages if m.get("role") == "user"]
    full_text = " ".join(user_texts)
    return sum(1 for p in _code_re if p.search(full_text)) >= 2


def choose_model(messages: list[dict], force: Optional[str] = None) -> tuple[str, float]:
    if force == "claude":
        return CLAUDE_MODEL, 1.0
    if force == "gemma":
        return GEMMA_MODEL, 0.0
    if force == "qwen":
        return QWEN_MODEL, 0.5

    score = complexity_score(messages)
    if score >= COMPLEXITY_THRESHOLD:
        return CLAUDE_MODEL, score
    if is_code_request(messages):
        return QWEN_MODEL, score
    return GEMMA_MODEL, score


app = FastAPI(title="OpenClaw Multi-Model Router", version="2.0.0")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: Optional[str] = "auto"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False


@app.get("/health")
def health():
    return {
        "status": "ok",
        "models": {
            "general": GEMMA_MODEL,
            "code": QWEN_MODEL,
            "strong": CLAUDE_MODEL,
        },
    }


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    msgs = [m.model_dump() for m in req.messages]

    # Force-route via the request's `model` field. Customize the aliases
    # to your taste — e.g., I personally add "edi" as a Claude alias since
    # I name my Claude persona EDI. Keep aliases stable so your agent's
    # AGENTS.md routing rules stay in sync.
    force = None
    if req.model in ("claude", "strong"):
        force = "claude"
    elif req.model in ("gemma", "weak", "local"):
        force = "gemma"
    elif req.model in ("qwen", "code"):
        force = "qwen"

    model, score = choose_model(msgs, force=force)
    log.info("score=%.2f → %s", score, model)

    kwargs = dict(model=model, messages=msgs, temperature=req.temperature)
    if req.max_tokens:
        kwargs["max_tokens"] = req.max_tokens
    if model in (GEMMA_MODEL, QWEN_MODEL):
        kwargs["api_base"] = OLLAMA_BASE_URL

    try:
        if req.stream:
            response = litellm.completion(**kwargs, stream=True)

            def event_stream():
                for chunk in response:
                    yield f"data: {json.dumps(chunk.model_dump())}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(event_stream(), media_type="text/event-stream")
        else:
            response = litellm.completion(**kwargs)
            result = response.model_dump()
            result["x_router"] = {"model": model, "score": round(score, 3)}
            return result
    except Exception as e:
        log.error("Completion error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {"id": "auto", "object": "model"},
            {"id": "claude", "object": "model"},
            {"id": "gemma", "object": "model"},
            {"id": "qwen", "object": "model"},
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4242, log_level="info")
