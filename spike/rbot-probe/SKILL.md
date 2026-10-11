---
name: rbot-probe
description: Deploy VI capability probe for the RBOT build. Use only when the user types /rbot-probe.
---

# RBOT capability probe

You are checking what this VS Code + GitHub Copilot setup can do. Do each step in order. If a step fails, record the exact error and continue with the next step. Write every result into `rbot-probe-result.md` in the workspace root under the headings below, then show the file.

## 1. Environment

Run in the terminal and record each command with its exact output:
- The operating system and shell: `uname -a` on macOS or Linux; `ver` and `$PSVersionTable.PSVersion` on Windows.
- `python --version`, `python3 --version` and `py --version`. Record which exist.
- `python -m pip --version`, using whichever Python command worked.

## 2. Packages

With the working Python command, run `python -m pip install --user pypdf openpyxl`, then `python -c "import pypdf, openpyxl; print(pypdf.__version__, openpyxl.__version__)"`. Record both outputs. If the install is refused (proxy, policy), record the exact error.

## 3. Subagent

Start a subagent (runSubagent) with exactly this task:

> Read `probe/input.txt` in the workspace. Run `python -c "print(6 * 7)"` in the terminal. Write `probe/subagent-output.txt` containing the first line of `probe/input.txt` on line 1 and the command's output on line 2. Reply with DONE.

Then read `probe/subagent-output.txt` yourself. Record whether the subagent started, read the file, ran the terminal command and wrote the file, and the file's exact content. Expected content: `RBOT probe input` on line 1 and `42` on line 2.

## 4. Skill location

Record the folder this SKILL.md was loaded from.

## 5. Web fetch

With whatever fetch or web tool you have, fetch `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001590895&type=10-K`. Record only whether a tool exists and whether the fetch succeeded (status or error), not the page content.

## 6. Model

Record the model name shown in the chat model picker for this conversation.
