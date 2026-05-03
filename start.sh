#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ -f "$SCRIPT_DIR/.env" ] && export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
[ -z "$ANTHROPIC_API_KEY" ] && echo "ERROR: ANTHROPIC_API_KEY not set" && exit 1
exec /opt/homebrew/bin/python3.11 -m uvicorn router:app \
    --host 0.0.0.0 --port 4242 --log-level info --app-dir "$SCRIPT_DIR"
