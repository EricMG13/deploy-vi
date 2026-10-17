# Corpus regression on the owner's machine (interfaces spec section 12.3).
# Needs RBOT_CORPUS_ROOTS (tests/corpus/README.md); a missing corpus file fails, never skips.
.PHONY: corpus
corpus:
	RBOT_REQUIRE_CORPUS=1 uv run pytest -m corpus --no-cov
	uv run python rbot/scripts/rbot.py corpus verify
