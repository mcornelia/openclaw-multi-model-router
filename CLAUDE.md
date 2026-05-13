# Project: OpenClaw Multi-Model Router

**Sensitivity**: public

## Overview
Public guide + minimal repo for a three-model AI router that runs alongside an OpenClaw agent. Routes simple questions to local Gemma/Qwen and keeps complex reasoning on the Claude API. Sister piece to the existing OpenClaw Setup Guide.

## Status
- **Phase**: Published — router.py shipped 2026-05-04 (scrubbed-and-published from Mike's working MacMini source)
- **GitHub**: https://github.com/mcornelia/openclaw-multi-model-router
- **Website post**: https://mcornelia.com/posts/openclaw-multi-model-router.html
- **Source guide**: drafted by Glyph (Mike's local OpenClaw agent on the MacMini)

## Local repo
This gdrive folder IS the local repo (matches the pattern of mountain-mesh-node-guide / openclaw-setup-guide / room-layout-tool — `.git/` lives inside the project folder, synced through gdrive).

## Files in repo
- `README.md` — full setup guide (renders on GitHub repo home)
- `router.py` — working FastAPI router (~150 lines). Ships scrubbed of personal naming. Real version on Mike's MacMini at `~/.openclaw/workspace/glyph-router/router.py` keeps Glyph/EDI labels.
- `start.sh` — startup script (loads `.env`, runs uvicorn on port 4242)
- `com.openclaw.router.plist` — launchd plist for auto-start on login
- `.env.example` — placeholder env template
- `.gitignore` — excludes `.env`, `router.log`, `__pycache__`, `.venv`

## Sensitivity scrubs (already applied — across README, plist, AGENTS.md snippets, and router.py)
- `Glyph` → `the Operator` throughout
- `[EDI]` → `[Claude]` throughout
- `glyph-router/` → `openclaw-router/` (folder name in install instructions)
- `com.glyph.router` → `com.openclaw.router` (plist label)
- `glyph-router` logger name → `openclaw-router`
- `Glyph Router` FastAPI title → `OpenClaw Multi-Model Router`
- `"edi"` force-route alias removed (kept `"claude"` and `"strong"`); comment added explaining how to add custom aliases
- `litellm.set_verbose = False` (deprecated) → `litellm.verbose = False`
- API key sits in `.env` (gitignored); `.env.example` is the public template

## Open TODOs
1. Mike to copy GDoc draft into Workplace Profile post (Part 3 / multi-model router post in the Home AI series — but per Mike's call, the Workplace post does NOT link to GitHub; published source is for the website-readers / DM-followers audience only)

## Maintenance
If Ollama API endpoints change, model names rev, or the router architecture evolves, update both:
- `~/gdrive/01_projects/22_openclaw_multi_model_router/router.py` (and README.md if interface changes) → push to the GitHub repo
- `~/gdrive/02_areas/career/website/posts/openclaw-multi-model-router.html` and push to mcornelia.com

If Mike wants to keep the personal MacMini version in sync with the published version:
- Copy `~/gdrive/01_projects/22_openclaw_multi_model_router/router.py` → `~/.openclaw/workspace/glyph-router/router.py`
- Re-add `"edi"` alias if he wants
- Restart launchd: `launchctl kickstart -k gui/$(id -u)/com.glyph.router` (or whatever local label he uses)

## Notes
- This is the natural sequel to the OpenClaw Setup Guide. Cross-linked in both directions.
- Tile position on play.html: **2** (right after OpenClaw Setup Guide), icon 🧠
- OG image accent color: magenta (#ff5cf2) — distinct from amber (Morning Brief) and violet (AI Chief of Staff)
- The Home AI Workplace series Part 3 GDoc still says "DM me if you want my version" — leave that language since the Workplace post intentionally doesn't link to GitHub. The GitHub source becomes the answer when colleagues DM, not a public push.
