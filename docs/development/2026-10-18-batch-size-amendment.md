# Owner batch-size amendment — 2026-10-18

The owner answered “Use coherent batches up to 4,000 lines” when asked what size limit should replace AGENTS.md’s 800-line cap for consolidated PRs. Root verified the actual human reply `01a14dfa-eaf0-7f71-8fa0-2025abfc3a58` in chat `01a14db3-5225-7382-8189-79a9b3263cda`.

This replaces the former 800-line limit with at most 4,000 ordinary changed lines per coherent PR. Existing counting, exclusions (including design under ADR 0006), retained checks and no-publication rules remain in force. Historical reports retain their original limits and results.

Not verified: integration, remote CI, merge or publication.
