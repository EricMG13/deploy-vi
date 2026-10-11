# Copilot spike — results

Owner-run on the work machine (Plan 01, Task 2). Paste each `rbot-probe-result.md` below it, then fill the table. Dates in ISO form.

| Check | Claude model | GPT model |
|---|---|---|
| Date run (`date` output) | | |
| Model name (picker, owner) | | |
| Model name (self-reported) | | |
| OS | | |
| Shell | | |
| Python command (PY) and version | | |
| `pip install --user pypdf openpyxl` works | | |
| Skill file present in `~/.copilot/skills/rbot-probe` (file check) | | |
| `/skills` lists `rbot-probe` (owner, from screen) | | |
| Subagent started | | |
| Subagent read a workspace file | | |
| Subagent ran a terminal command | | |
| Subagent wrote a workspace file | | |
| Subagent and main hash outputs match | | |
| Fetch tool exists | | |
| SEC fetch status or error | | |
| Control fetch (code.visualstudio.com) status | | |
| Context window, tokens (from GitHub's Copilot model docs) | | |

**Smallest context window across the two models (tokens):** 

**Provisional size budget in use until this record is filled:** 51,200 bytes (128k tokens × 4 × 0.10).

**Module size budget** = smallest window × 4 bytes × 0.10 = ____ bytes (goes into `rbot/catalog.json` in Task 8).

## Outcome

Provisional module size budget 51,200 bytes in rbot/catalog.json, pending the owner's spike run.

Every "no" above changes the design before Plan 02 starts; record the change here and in the spec:
- Subagent cannot run the terminal or write files → the orchestrator runs every script and writes every file; subagents return Handoff text only.
- No subagents at all → modules run sequentially in the main chat, one module file per step, with a context reset between modules by starting a new chat from `run-state.json`.
- Python older than 3.11 → lower the floor in `pyproject.toml` (decision record 0001).
- pip blocked → Plan 02 uses only the standard library for xlsx (zipfile + xml) and needs the analyst to export PDFs as text.
- No fetch tool → Deep Research is Source Pack-only (ADR 0004 consequence).
- Subagent could not read a workspace file → the orchestrator reads inputs and passes their content in the subagent task.
- `/skills` does not list `rbot-probe` from `~/.copilot/skills/` → the install location must change; record where it does load from.
- pip install works but the import fails → treat as pip blocked (stdlib-only xlsx path).
- Only `python3` exists on macOS/Linux → every command uses `python3`.
- Fetch tool exists but the SEC fetch fails → Deep Research stays Source Pack-only unless the control URL succeeds and a public source with a declared User-Agent is reachable.
- Windows → `install.ps1` is the primary installer and every MODULE.md command uses `python`, not `python3`.

## Raw results

### Claude model

### GPT model
