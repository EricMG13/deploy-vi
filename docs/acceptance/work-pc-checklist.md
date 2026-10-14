# Work-PC acceptance checklist

## 6. Owner work-PC procedure

### 6.1 Checklist (shipped as `CHECKLIST.md`)

Run everything in the PowerShell terminal inside the editor. Append each command's output with `| Tee-Object -Append evidence\<file>.txt`.

1. **Check the package.** Run `Get-FileHash -Algorithm SHA256 rbot-v1-*.zip`. The result must equal the sha256 in the hand-off. Unzip to `C:\rbot-transfer\`.
2. **Record the environment** (`env.txt`): `$PSVersionTable.PSVersion`, `Get-ExecutionPolicy -List`, `py --version`, `python --version`, and the editor and Copilot Chat versions.
3. **Run the probe** for each model, Claude first and then GPT:
   1. Copy `spike\rbot-probe` to `$HOME\.copilot\skills\rbot-probe`.
   2. Open `spike\probe-workspace` in the editor.
   3. Open a new Agent-mode chat, pick the model and run `/rbot-probe`.
   4. Save the result as `evidence\<claude|gpt>\rbot-probe-result.md`.
   5. Note whether `/skills` lists the probe.
   6. Note the model's context window in tokens, from GitHub's Copilot model docs.
4. **Set up Python** (`install.txt`):
   1. `py -3.11 -m venv $HOME\.rbot-venv`.
   2. `& $HOME\.rbot-venv\Scripts\python.exe -m pip install --no-index --find-links .\wheels pypdf==6.19.0 openpyxl==3.1.5`.
   3. Import both packages and print their versions.
5. **Install the skill** (`install.txt`):
   1. Run `powershell -ExecutionPolicy Bypass -File .\install.ps1 -Python $HOME\.rbot-venv\Scripts\python.exe`.
   2. If policy forbids it, record the error, copy `rbot\` to `$HOME\.copilot\skills\rbot\` by hand and write `install_method: manual`.
   3. Run the installed `rbot.py version` and `check`, then append the installed `runtime.json` line `runtime_tree` (`Select-String '"runtime_tree"' $HOME\.copilot\skills\rbot\runtime.json`) to `install.txt`.
6. **Run with the Claude model:**
   1. Copy `pack\czr-2026q2-primary` to `C:\rbot-acceptance\claude\` and open that folder.
   2. Open a new Agent-mode chat with the Claude model and type `/rbot`. Note the start time. If asked for Python, give the venv path.
   3. **Turn 1:** confirm what is shown. Edit only a value that contradicts the pack, and record the edit.
   4. **Turn 2:** choose Full Credit Assessment, `full`, Primary yes, analyst `acceptance-claude`.
   5. Type nothing more except for the resume check. When CP-1A is reported accepted, close the chat, open a new one and type `/rbot`. Note whether it resumes without asking for Approval.
   6. At the end, note the finish time and copy the final reply.
   7. Open `rbot-runs\<run>\report.html` from disk.
   8. Export the chat (Chat: Export…, or copy the text) to `evidence\claude\chat.json` or `chat.md`, and redact account names.
   9. Record verbatim any question the agent asked after Approval.
7. **Run with the GPT model:** repeat step 6 under `C:\rbot-acceptance\gpt\`, without the resume check.
8. **Fill in `evidence\checklist.txt`.**
9. **Zip and return.** Zip `evidence\` and both `C:\rbot-acceptance\<model>\czr-2026q2-primary` folders, including `rbot-runs\`, as `rbot-v1-evidence-<date>.zip`. Confirm it holds no work data, then transfer it to the Mac.

### 6.2 Evidence the owner brings back

```
rbot-v1-evidence-<date>/
  checklist.txt  env.txt  install.txt
  claude/rbot-probe-result.md  claude/chat.(json|md)  claude/czr-2026q2-primary/**  (incl. rbot-runs/<run_id>/)
  gpt/   … same
```

`checklist.txt` keys (all required, one `key: value` line each):

- **Package and environment:** `package_sha256`, `os`, `editor`, `editor_version`, `copilot_chat_version`, `execution_policy`, `python_cmd`, `python_version`.
- **Installation:** `wheels_install`, `install_method`.
- **Per model, with a `claude_` or `gpt_` prefix:** `picker_label`, `context_tokens`, `skills_lists_rbot`, `rbot_invoked`, `turns_before_approval`, `questions_after_approval`, `subagents` (yes, fallback or no), `report_opened`, `start_utc`, `finish_utc`.
- **Claude run only:** `claude_resume_ok`.
- **Values:** `yes` or `no` for `wheels_install`, `*_skills_lists_rbot`, `*_rbot_invoked`, `*_report_opened` and `claude_resume_ok`; `install_method` is `ps1` or `manual`; `*_context_tokens`, `*_turns_before_approval` and `*_questions_after_approval` are whole numbers; `*_start_utc` and `*_finish_utc` are ISO times such as `2026-10-14T09:00:00Z`.

### 6.3 Ingest command (Mac)

```bash
unzip -q rbot-v1-evidence-<date>.zip -d "<scratch>/evidence-<date>"   # its own empty folder; data only
uv run python scripts/acceptance.py ingest --evidence "<scratch>/evidence-<date>/rbot-v1-evidence-<date>" \
  --manifest "<08.7 build dir>/MANIFEST.json" --out docs/acceptance/v1-work-pc-<date>.md
```

### 6.4 Blank `checklist.txt`

The package ships this block as `evidence\checklist.txt`.

```checklist.txt
package_sha256:
os:
editor:
editor_version:
copilot_chat_version:
execution_policy:
python_cmd:
python_version:
wheels_install:
install_method:
claude_picker_label:
claude_context_tokens:
claude_skills_lists_rbot:
claude_rbot_invoked:
claude_turns_before_approval:
claude_questions_after_approval:
claude_subagents:
claude_report_opened:
claude_start_utc:
claude_finish_utc:
claude_resume_ok:
gpt_picker_label:
gpt_context_tokens:
gpt_skills_lists_rbot:
gpt_rbot_invoked:
gpt_turns_before_approval:
gpt_questions_after_approval:
gpt_subagents:
gpt_report_opened:
gpt_start_utc:
gpt_finish_utc:
```
