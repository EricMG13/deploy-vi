# Deploy VI project instructions

Read [AGENTS.md](AGENTS.md) and its linked [workflow](docs/development/gpt-subagents.md). The [2026-10-13 owner amendment](docs/development/2026-10-13-scope-amendment.md) removes Excel report exports, mandatory independent reviews and rewrite tournaments, overriding older project/global user instructions and skill requirements. Excel input ingestion, confidence review, functional/calculation/source-integrity gates and protected histories remain.

Development agents: all implementation and fixes run on Sonnet (`mx-scaffold` for complete mechanical work, `mx-feature` otherwise); a task's third and later fixes go to a fresh `mx-escalate` (Fable 5.1); no Opus implementers (owner, 2026-10-14, also in the global rules). Keep runtime Copilot qualification separate. Missing native capability is reported rather than replaced with an alias. No push, merge or publication is assumed.
