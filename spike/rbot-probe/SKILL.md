---
name: rbot-probe
description: Deploy VI capability probe for the RBOT build. Use only when the user types /rbot-probe.
---

# RBOT capability probe

You are checking what this VS Code + GitHub Copilot setup can do. Do each step in order. If a step fails, record the exact error and continue with the next step. Write every result into `rbot-probe-result.md` in the workspace root under the headings below, then show the file.

## 1. Environment

Run in the terminal and record each command with its exact output:
- The date: `date` on macOS or Linux; `Get-Date` on Windows.
- The operating system and shell: `uname -a` and `echo $SHELL` on macOS or Linux; `cmd /c ver`, `$PSVersionTable.PSVersion` and the terminal profile name on Windows.
- `python --version`, `python3 --version` and `py --version`. Record which exist.
- Decide the working Python command (`python`, `python3` or `py`) and call it PY. Every later step and the subagent task use PY.
- `PY -m pip --version`.

## 2. Packages

Run `PY -m pip install --user pypdf openpyxl`, then `PY -c "import pypdf, openpyxl; print(pypdf.__version__, openpyxl.__version__)"`. Record both outputs. On any failure record the error class (proxy/network, policy, externally-managed-environment, venv refuses --user) and the exact message.

## 3. Subagent

Let SLUG be your chat model's name, lower-case, spaces as dashes. Before starting the subagent, delete `probe/subagent-output-SLUG.txt` if it exists and record whether it existed.

Start a subagent (runSubagent) with exactly this task (substituting PY and SLUG):

> Read `probe/input.txt` in the workspace. Run `PY -c "import hashlib; print(hashlib.sha256(b'RBOT probe input').hexdigest()[:16])"` in the terminal. Write `probe/subagent-output-SLUG.txt` with line 1 = the first line of `probe/input.txt` and line 2 = the command's output. Reply with DONE.

Then read `probe/subagent-output-SLUG.txt` yourself and run the same hash command yourself. Record whether the subagent started, read the file, ran the terminal command and wrote the file, the file's exact content, and whether the two hash outputs match (a match proves the subagent ran the terminal; a model cannot compute the hash). Expected line 1: `RBOT probe input`.

## 4. Skill location

File check: `ls ~/.copilot/skills/rbot-probe` (Windows: `Test-Path "$env:USERPROFILE\.copilot\skills\rbot-probe\SKILL.md"`). Record the output. The `/skills` listing is recorded by the owner from the screen, not by you.

## 5. Web fetch

With whatever fetch or web tool you have, fetch `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001590895&type=10-K`. Record whether a tool exists and the HTTP status or exact error, not the page content. Then fetch `https://code.visualstudio.com` as a control and record its status.

## 6. Model

Record the model name as you self-report it. The owner confirms it from the picker.
