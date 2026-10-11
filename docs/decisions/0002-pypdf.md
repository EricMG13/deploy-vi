# 0002 — pypdf for PDF text and page counts

**Need:** `rbot inventory` counts PDF pages and `rbot prepare` turns each PDF page into page-anchored text (interfaces spec section 8.1). Filings, rating reports and bond reports arrive as PDFs (TEST-Issuer Data, the VMO2 packs).

**Order of preference (global rule):** the standard library has no PDF parser; no locked dependency reads PDFs; writing a PDF text extractor (fonts, encodings, compressed streams, cross-reference repair) is far beyond this plan. So a new runtime dependency.

**Choice:** `pypdf` — pure Python, no compiled code and no required dependencies on Python 3.11+, BSD-3-Clause, actively maintained, and the library the Copilot spike installs (`pip install --user pypdf openpyxl`, Plan 01 Task 2). Alternatives rejected: `pdfminer.six` (pulls in `cryptography` and `charset-normalizer`), `pypdfium2` and `PyMuPDF` (compiled binaries; PyMuPDF is AGPL).

**Version:** pinned `pypdf==6.19.0` (released 2026-09-16). The newest release older than 30 days on 2026-10-11 is 6.18.1 (2026-09-11), but it carries three advisories fixed in 6.19.0 (GHSA-w23x-9jrw-r45c page-label memory use, GHSA-php9-fj8v-98fj form flattening runtime, GHSA-v247-6f48-mgcj embedded-file runtime), so `pip-audit --strict` refuses it. 6.19.0 has no known advisory and passes 30 days on 2026-10-16. 6.20.0 (2026-10-09) is too new. Upgrade only to a release at least 30 days old that `pip-audit --strict` accepts.

**Use:** only `PdfReader(path)`, `is_encrypted`, `decrypt("")`, `len(reader.pages)` and `page.extract_text()`. A file pypdf cannot open (`PyPdfError`, `ValueError`, `KeyError`, `OSError`) is listed as unreadable with the error text, never skipped silently. PDFs are untrusted input: no page labels, form flattening or embedded files are read, which keeps RBOT off the code paths of the advisories above.

**Analyst machines:** the Copilot host installs it with `python -m pip install --user pypdf==6.19.0` (the install step arrives with Plan 06).
