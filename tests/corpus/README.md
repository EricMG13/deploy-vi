# Corpus

`corpus.json` registers every corpus pack with each file's sha256 (interfaces spec section 12). External files never enter the repo; `RBOT_CORPUS_ROOTS` says where they are:

```bash
export RBOT_CORPUS_ROOTS='{"caos-qualification": "/Users/ericguei/Documents/caos-databricks/qualification", "test-issuer-data": "/Users/ericguei/Documents/TEST-Issuer Data"}'
uv run python rbot/scripts/rbot.py corpus verify   # 0 ok, 1 missing or changed file, 2 unresolved root
make corpus                                        # RBOT_REQUIRE_CORPUS=1: a missing file fails, never skips
```

Hashes were taken on 2026-10-11 from caos-databricks `5ca9118e` (`qualification/` last changed in `8fd9652b`) and `TEST-Issuer Data` as found that day. A differing hash means the source changed: re-check the pack and update its entry with the tests it affects. `synthetic/` holds packs authored for RBOT: every authored file is labelled SYNTHETIC in its name and first line, and files borrowed from an external root are listed with `external` and copied in at test time.
