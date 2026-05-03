# OpenClaw Multi-Model Router

A three-model AI setup that routes requests intelligently between local models and Claude. Simple questions stay local (free, private, fast). Complex reasoning escalates to the Claude API.

**Prerequisite**: [OpenClaw](https://mcornelia.github.io/openclaw-setup-guide) already running with your agent (the "Operator") configured.

---

## The Architecture

```
Your message → the Operator (your local agent)
                ├── General Q&A, chat, trivia  → [Gemma]   Gemma 4 31B        (local, free)
                ├── Code tasks                 → [Qwen]    Qwen 2.5 Coder 32B (local, free)
                └── Complex reasoning,         → [Claude]  Claude Sonnet      (API)
                    personal context, tools
```

Every response is labeled `[Gemma]`, `[Qwen]`, or `[Claude]` so you always know which model answered.

> **Customize the labels.** I personally use `[EDI]` for Claude (named after the AI in Mass Effect) and a custom name for my Operator. Pick whatever fits your setup — just keep the labeling consistent so you always know who's talking.

**Hardware tested on**: Mac Mini M4, 24GB unified memory, ~60GB free disk for models.

---

## Step 1 — Install Ollama and Python 3.11

```
brew install ollama python@3.11
```

Verify:

```
ollama --version
/opt/homebrew/bin/python3.11 --version
```

---

## Step 2 — Start Ollama

```
brew services start ollama
```

Verify: `ollama list`

---

## Step 3 — Pull the Models

```
ollama pull gemma4:31b
ollama pull qwen2.5-coder:32b
```

- **Gemma 4 31B** — Google DeepMind. General-purpose, 256K context, multimodal.
- **Qwen 2.5 Coder 32B** — Alibaba. Coding specialist, 92 languages.

Each is ~19–20 GB. Disk needed: ~40 GB. RAM needed: 24 GB (one model loads at a time).

---

## Step 4 — Install Python Packages

```
/opt/homebrew/bin/python3.11 -m pip install litellm anthropic uvicorn fastapi
```

---

## Step 5 — Create the Router Project

```
mkdir -p ~/.openclaw/workspace/openclaw-router
```

Copy `router.py`, `start.sh`, and `.env.example` from this repo into that folder. Then:

```
cp .env.example .env
chmod +x start.sh
```

Edit `.env` and paste your real Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

> **Never commit your `.env`.** It's in `.gitignore` for a reason.

---

## Step 6 — Auto-Start on Login (Optional)

Save the `com.openclaw.router.plist` from this repo to `~/Library/LaunchAgents/com.openclaw.router.plist` and replace `YOUR_USERNAME` with your Mac username.

Then load it:

```
launchctl load ~/Library/LaunchAgents/com.openclaw.router.plist
```

The router will now start automatically every time you log in, and restart if it crashes.

---

## Step 7 — Configure Your Operator to Route Automatically

Add this section to `~/.openclaw/workspace/AGENTS.md` before the "Make It Yours" section:

```markdown
## Smart Routing — Three-Way: Gemma / Qwen / Claude

| Model              | Label    | Role                    |
|--------------------|----------|-------------------------|
| Gemma 4 31B        | [Gemma]  | On-premise generalist   |
| Qwen 2.5 Coder 32B | [Qwen]   | Coding agent            |
| Claude (you)       | [Claude] | Deep reasoning          |

You are the Operator — direct the models, don't label yourself.

**Route to Gemma**: trivia, definitions, casual chat, greetings, sign-offs, anything under ~20 words with no technical content.

**Route to Qwen**: writing/debugging/explaining code, scripting, architecture, anything involving a code block or programming language.

**Keep with Claude**: multi-step reasoning, analysis, tradeoffs, personal context (user's family/work/schedule), tool use, long input (>500 words), anything requiring Bash/file/web access.

**How to call Gemma** (Bash tool):

    curl -s --max-time 90 http://localhost:11434/api/chat \
      -H "Content-Type: application/json" \
      -d '{"model":"gemma4:31b","messages":[{"role":"user","content":"PROMPT"}],"stream":false}' \
      | /opt/homebrew/bin/python3.11 -c "import sys,json; print(json.load(sys.stdin)['message']['content'])"

**How to call Qwen** (Bash tool):

    curl -s --max-time 90 http://localhost:11434/api/chat \
      -H "Content-Type: application/json" \
      -d '{"model":"qwen2.5-coder:32b","messages":[{"role":"user","content":"PROMPT"}],"stream":false}' \
      | /opt/homebrew/bin/python3.11 -c "import sys,json; print(json.load(sys.stdin)['message']['content'])"

Always start every reply with `[Gemma]`, `[Qwen]`, or `[Claude]`.
If a local model times out, fall back to Claude silently and label `[Claude]`.
```

---

## Step 8 — Test Everything

```bash
# Test Gemma
curl -s --max-time 90 http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{"model":"gemma4:31b","messages":[{"role":"user","content":"What is the capital of France?"}],"stream":false}' \
  | /opt/homebrew/bin/python3.11 -c "import sys,json; print(json.load(sys.stdin)['message']['content'])"

# Test Qwen
curl -s --max-time 90 http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5-coder:32b","messages":[{"role":"user","content":"Write a Python function to reverse a string."}],"stream":false}' \
  | /opt/homebrew/bin/python3.11 -c "import sys,json; print(json.load(sys.stdin)['message']['content'])"
```

Both should respond within 30 seconds (longer on first call as the model loads into memory).

---

## Routing at a Glance

| Signal                                   | Goes to           |
| ---------------------------------------- | ----------------- |
| Greeting, joke, trivia, simple question  | Gemma             |
| Code, debugging, scripting, architecture | Qwen              |
| Planning, analysis, personal info, tools | Claude            |
| Local model timeout                      | Claude (fallback) |

---

## Troubleshooting

| Problem               | Fix                                                            |
| --------------------- | -------------------------------------------------------------- |
| Ollama not responding | `brew services restart ollama`                                 |
| Model not found       | `ollama pull gemma4:31b` or `ollama pull qwen2.5-coder:32b`    |
| Slow first response   | Normal — model loads on first query (~30 sec)                  |
| Router won't start    | `cat ~/.openclaw/workspace/openclaw-router/router.log`         |
| Out of memory         | Restart Ollama: `brew services restart ollama`                 |
| API key not set       | Check `.env` exists in `openclaw-router/` and contains the key |

---

## Why this exists

Running everything through the Claude API gets expensive fast, especially for casual chat. Running everything locally means slow, inconsistent answers on hard problems. This router gives you the best of both: cheap local speed for the 80% of requests that don't need a frontier model, and Claude's deep reasoning for the 20% that do.

The labels (`[Gemma]`, `[Qwen]`, `[Claude]`) make the trade-off transparent. You always know which model answered, so you can tell the Operator to "ask Claude this one" if the local answer was weak.

---

## License

MIT — do whatever you want.

---

*Built by Mike Cornelia. See more at [mcornelia.com](https://mcornelia.com).*
