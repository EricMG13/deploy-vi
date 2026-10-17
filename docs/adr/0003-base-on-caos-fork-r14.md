# Rewrite the methodology, using the caos-databricks Deploy V fork at r14 as reference

Upstream Deploy V (`a43cb903`) contradicts its own checkers: a three-part review in caos-databricks found 50+ places where canon or method text told the model to write what the validators refuse, closed over fork rounds r1–r14 (`claude/book-model-01-vendor-cp1-r14`, `a14f9051`). The fork also carries M365-only machinery (retrieval index, build ids, integrity manifests, alias plumbing, saved-memory launchers) and registers no consumer reads. With the owner's approval to alter the files, Deploy VI does not run the fork: each module is rewritten as its own contract in the increment that first needs it, keeping Deploy V's analytical method, using the house scales, emitting only what a downstream module, the Model or a Front Page reads, and generating prose and validator from one contract. The r14 text is kept read-only in the repo as reference and is never shipped.

## Consequences

A rewritten module ships only after an A/B on the golden pack (forked vs rewritten, graded on the analytical-depth rules) shows no loss. Later caos fork fixes are reference input, not merges. CP-MEMO is dropped: the HTML Report replaces it.

## Amendment (owner, 2026-10-11): partial, not full

A full rewrite is not required. Each module keeps the r14 analytical method and wording, ported into its contract with the minimum change the skill structure needs for performance: the Handoff contract format (tagged tables, front matter, citations) and checker agreement, the MODULE.md + canon.md size budget, removal of M365-only machinery (retrieval index, build ids, manifests, alias plumbing, memory launchers), the house scales, and emitting only what a downstream module, the Model or a Front Page reads. Method text is rewritten only where r14 contradicts its checker or the budget forces it. The A/B on the golden pack still gates each ported module.
