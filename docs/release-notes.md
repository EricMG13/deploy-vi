# Release notes

## v1 (draft)

RC: build/v1-rc3 `2d19018`. Live status: **pending** (work-PC acceptance by the owner; see [acceptance/v1.md](acceptance/v1.md)).

### What v1 does

Full Credit Assessment at `full` depth, run unattended as sub-agents in Copilot: CP-0, CP-1, CP-1A, CP-1B, CP-1D, MODEL, CP-2, CP-3, FIT, CP-5, CP-6, then a rendered report (`report.html`, `report.md`) with citations and a Limitations tab. Excel input ingestion is supported; Excel report export is not part of v1. Quick, CP-DR, CP-8, PROJECTION and the other Pathways are backlog.

### What changed in Plan 08

- Model fix (F3): the pro forma undrawn revolver now reflects facility-stack movements on the revolver (spec §6.5).
- Model fix: an income statement with no cost of revenue (nature-of-expense) now computes EBITDA and EBIT instead of blanking them; gross profit is left blank with a note.
- Report fix (R7): Restricted steps that no CP-5 row names appear as unforeseen limitations.
- A validator finding for unresolved `[[...]]` placeholders.
- Module revisions after the model-written A/B: canon rules (counter-argument, conflict register, time-ordered downside), and process changes in CP-0, CP-1, CP-1D and CP-3.
- Windows run lock (`msvcrt.locking`) for the work PC.
- Transfer package, extracted-install smoke and acceptance check scripts.

### Known limitations

- F4: Adjusted debt (rent-bearing) is paired with rent-excluded SSIM EBITDA, per spec; the pairing awaits an owner decision.
- F5, F6: FIT Evidence Trace is empty; C-17 is not computed when the sector is only in CP-1A prose.
- F7: CP-3 comparables may mix secured and unsecured seniority without disclosure; indenture Schedule II is not examined.
- F8: an expected (term-sheet) rating counts as rated in FIT bucket limits and can oversize a new tranche. Owner decision.
- F9: CP-6 recovery stress may rank sale-leaseback obligations ahead of secured lenders.
- F10: the Credit Snapshot print is zoomed to one page and is unreadable for long snapshots. Owner decision.
- F11: negative add-backs are excluded with their category, so FY2024 Adjusted EBITDA can exceed the issuer's figure. Owner decision.
- F12: opening report.html with a hash shows two panes until a nav item is clicked.
- R5 measurement is keyed on worker-chosen facility ids.
- Windows behaviour (run lock, installers, `os.replace` with open handles) is unverified.

### Live acceptance

Pending: L1-L11 and R1-R8 on one Claude and one GPT model on the work PC. The package (rbot-v1-2d190181a539.zip, sha256 `b86bc28e5bc6fb8dcf9970f458e8c156ff807dcdd77e2a487962d17afa7ed183`) has not been handed over yet.
