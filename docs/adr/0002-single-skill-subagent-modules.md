# One discoverable rbot skill; modules run as subagents

Deploy V shipped ~25 sibling skills, and its own launcher documents the resulting failure modes: whole-folder retrieval blending modules and bare IDs triggering by accident. Copilot selects skills from name and description alone, so siblings would compete on every prompt. Deploy VI exposes only `rbot/SKILL.md`; analytical modules live as internal files that the orchestrator hands to one subagent each (fresh context, only that module's file plus its declared input handoffs), with Markdown handoff files between them.

## Consequences

Modules cannot be invoked directly as `/skills`; all entry goes through RBOT. Subagent support in the work VS Code version must be verified before release.
