# Provenance

Read-only copy of the Deploy V fork vendored in caos-databricks, used as reference for Deploy VI's module rewrites (ADR 0003). Never installed, never run by RBOT, never edited.

- Source: `/Users/ericguei/Documents/caos-databricks`, `vendor/deploy-v/`
- Commit: `a14f9051` on branch `claude/book-model-01-vendor-cp1-r14` (fork round r14: CP-1 pro forma register and debt terms)
- Copied with: `git -C <caos> archive a14f9051 vendor/deploy-v | tar -x -C reference/deploy-v-r14 --strip-components=2`
- Integrity: `python3 -B reference/deploy-v-r14/verify_package.py` exits 0 on this copy.
