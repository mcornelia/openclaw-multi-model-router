"""
OpenClaw Multi-Model Router
============================

FastAPI app that proxies requests between local Ollama models (Gemma, Qwen)
and the Anthropic Claude API based on routing rules.

PLACEHOLDER — actual implementation pending. The working source lives on
the author's MacMini at ~/.openclaw/workspace/openclaw-router/router.py
and will be committed in a follow-up.

Expected behavior:
  - FastAPI app listening on 0.0.0.0:4242
  - Reads ANTHROPIC_API_KEY from environment (loaded by start.sh from .env)
  - Receives chat-style requests; routes to:
      * gemma4:31b via Ollama (http://localhost:11434/api/chat)
      * qwen2.5-coder:32b via Ollama (http://localhost:11434/api/chat)
      * Claude API for everything else
  - Falls back to Claude on local-model timeout (90s default)
  - Labels every response with [Gemma], [Qwen], or [Claude]

Stack: fastapi + uvicorn + litellm + anthropic (see start.sh for the run command).
"""

raise NotImplementedError(
    "router.py is a placeholder. The working implementation is pending — "
    "see README.md for the architecture and Step 7 for the routing rules."
)
