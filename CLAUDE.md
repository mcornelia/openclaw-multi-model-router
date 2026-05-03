# Project: OpenClaw Multi-Model Router

**Sensitivity**: public

## Overview
Public guide + minimal repo for a three-model AI router that runs alongside an OpenClaw agent. Routes simple questions to local Gemma/Qwen and keeps complex reasoning on the Claude API. Sister piece to the existing OpenClaw Setup Guide.

## Status
- **Phase**: Published (router.py source pending)
- **GitHub**: https://github.com/mcornelia/openclaw-multi-model-router
- **Website post**: https://mcornelia.com/posts/openclaw-multi-model-router.html
- **Source guide**: drafted by Glyph (Mike's local OpenClaw agent on the MacMini)

## Local repo
This gdrive folder IS the local repo (matches the pattern of mountain-mesh-node-guide / openclaw-setup-guide / room-layout-tool — `.git/` lives inside the project folder, synced through gdrive).

## Files in repo
- `README.md` — full setup guide (renders on GitHub repo home)
- `router.py` — **STUB pending** — Mike to provide the working source from `~/.openclaw/workspace/glyph-router/router.py` on the MacMini
- `start.sh` — startup script (loads `.env`, runs uvicorn on port 4242)
- `com.openclaw.router.plist` — launchd plist for auto-start on login
- `.env.example` — placeholder env template
- `.gitignore` — excludes `.env`, `router.log`, `__pycache__`, `.venv`

## Sensitivity scrubs (already applied)
- `Glyph` → `the Operator` throughout (Glyph is Mike's personal agent name)
- `[EDI]` → `[Claude]` throughout (EDI is Mike's personal Claude persona)
- `glyph-router/` → `openclaw-router/` (folder name in install instructions)
- `com.glyph.router` → `com.openclaw.router` (plist label)
- API key sits in `.env` (gitignored); `.env.example` is the public template

## Open TODOs
1. **CRITICAL**: Mike to paste the actual `router.py` from MacMini → follow-up commit replaces the stub
2. Mike to screenshot OG image template → push to website's `og-images/openclaw-multi-model-router.png`
3. Mike to copy GDoc draft into Workplace Profile post

## Maintenance
If Ollama API endpoints change, model names rev, or the router architecture evolves, update both:
- `~/gdrive/01_projects/22_openclaw_multi_model_router/README.md` and push to the GitHub repo
- `~/gdrive/02_areas/career/website/posts/openclaw-multi-model-router.html` and push to mcornelia.com

## Notes
- This is the natural sequel to the OpenClaw Setup Guide. Cross-linked in both directions.
- Tile position on play.html: **2** (right after OpenClaw Setup Guide), icon 🧠
- OG image accent color: magenta (#ff5cf2) — distinct from amber (Morning Brief) and violet (AI Chief of Staff)
