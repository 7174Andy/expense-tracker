## Context

`expense_tracker/utils/extract.py` (70 lines) is the entire PDF surface, with one caller at `gui/dialogs/upload.py:56`. It does two jobs in one loop:

1. **Layout reconstruction** (`extract.py:15-29`) — pull words with coordinates, bucket by `round(top/2)*2` to rebuild table rows, sort each bucket by `x0`. Deliberately ignores pdfplumber's table detection, since statement tables often have no ruling lines.
2. **Row interpretation** (`extract.py:32-53`) — keep a line only if `tokens[0]` matches `^\d{2}/\d{2}/\d{2}$` and some token matches an amount pattern (scanned right-to-left); everything between becomes the description.

Job 1 is bank-agnostic. Job 2 is *mostly* bank-agnostic — "starts with a date, ends with an amount" describes most US statements. The BofA-specific parts are narrow: the date format, the junk lines to skip, and the sign convention.

Constraint driving the whole design: **only Bank of America statements are available for testing.** Any other bank's profile would be unverifiable guesswork.

## Goals / Non-Goals

**Goals**
- Adding bank #2 is a one-entry append to `PROFILES`, with no new function, file, or branch in the parser.
- Bank-specific row logic becomes testable without constructing mocked PDF page objects.
- An unknown bank is attempted via a generic profile, and any misparse is visible to the user before it reaches the database.

**Non-Goals**
- Profiles for banks we cannot test. Two profiles ship: `BOFA` and `GENERIC`.
- OCR for scanned/image-only statements. No such statements exist in use today.
- Encrypted/password-protected PDF support. Add when a password-protected statement actually appears.
- Validating parsed totals against a statement's declared total (see Decision 4).
- CSV export or a CLI. This is a GUI app; monopoly's CLI surface is not wanted.

## Decisions

### Decision 1: Keep pdfplumber. Do not adopt PyMuPDF.

The original motivation was PyMuPDF's speed. Measured on a generated 4-page / 160-row statement-shaped PDF (all three engines extracted an identical 1324 words, so the numbers are comparable):

| engine | warm import | open + metadata | words w/ coords, 4 pages | 235-page PDF | installed size | license |
|---|---|---|---|---|---|---|
| pdfplumber (current) | 55 ms | 3.01 ms | **128 ms** | 65 s | 35 MB | MIT |
| pymupdf | 56 ms | 0.31 ms | **16 ms** | 2.7 s | 61 MB | **AGPL-3.0** |
| pypdfium2 | 24 ms | 0.13 ms | **26 ms** | 4.8 s | 7.8 MB | BSD-3/Apache-2.0 |

The full parse of a realistic statement improves by 112 ms — inside a modal dialog the user just clicked "Upload" on, where Tkinter's own teardown costs more. The 24× advantage on a 235-page document is real but describes a regime statements never enter (4–8 pages).

Rejected alternatives:
- **PyMuPDF**: better ergonomics (`get_text("words")` tuples, `doc.metadata`, `needs_pass`/`authenticate`), but AGPL-3.0 against this project's MIT `LICENSE`, plus 61 MB — nearly 2× pdfplumber's entire dependency tree.
- **pypdfium2**: permissive, and adopting it would let pdfplumber go, dropping `pdfminer.six` + `pillow` + `cryptography` for a net −27 MB and 31 ms faster startup. Rejected because it has no word-level API — words must be grouped from `get_charbox(i)` per character, ~25 lines we would own — and the footprint win does not justify a rewrite plus new tests for a GUI app.

Consequence: the engine sits behind `page_lines(page)`, so a future swap touches one function. Revisit only if encrypted statements or a measurable delay appear.

### Decision 2: One file, not a package.

Everything stays in `utils/extract.py` (~150 lines). Monopoly needs `banks/`, `identifiers.py`, `pipeline.py`, and `handler.py` because it serves 17 institutions and a CLI. At two profiles a package is pure indirection. Split into `utils/statements/` at 3+ profiles, per `openspec/project.md` ("single-file implementations until proven insufficient").

### Decision 3: Profile-driven generic parser, not per-bank parsers.

```python
@dataclass(frozen=True)
class BankProfile:
    name: str
    detect: tuple[str, ...]           # substrings sought in PDF metadata, then page-1 text
    date_formats: tuple[str, ...]     # ("%m/%d/%y",) — omit %y/%Y for year-less statements
    skip: tuple[str, ...]             # description prefixes to drop ("total ", "balance ")
    expenses_positive: bool = False   # statement prints expenses as positives (credit-card style)
```

Detection order: metadata substring → page-1 text substring → `GENERIC`. A profile matches when **any** of its `detect` substrings is found. Statement generators are stable per institution, so metadata alone usually suffices, and pdfplumber exposes `pdf.metadata` without a new dependency.

Implementation trap: `GENERIC` carries an empty `detect` tuple and MUST NOT be registered in `PROFILES`. It is reached only as the explicit fallback — an `all()`-based match over an empty tuple is vacuously true, so a registered `GENERIC` would match the first statement it saw and shadow every real profile.

Rejected: a bank dropdown in `UploadDialog`. It pushes a question onto the user that metadata answers for free, and `GENERIC` already handles the unknown case. Reconsider if detection proves unreliable across real statements.

### Decision 4: Preview before import, not total-validation.

Monopoly validates that parsed amounts sum to the statement's declared total. That needs a per-profile regex locating where each bank prints its total — untestable beyond BofA, and it catches only one failure class (dropped rows), not wrong signs, wrong years, or phantom rows.

A preview table showing count, sum, and every parsed row catches all of those, needs no per-bank config, and is what makes pointing `GENERIC` at an unknown bank safe. This matters because duplicate detection (`transaction.py:73`) will not save the user from rows that are wrong but unique.

### Decision 5: Year inference by string suffix, leaving `utils/date.py` untouched.

`parse_date_from_str` already tries `%Y-%m-%d`, `%m/%d/%Y`, `%m/%d/%y` and is shared with the dialogs. Rather than adding a `year` parameter to a shared util, year-less raw dates get the inferred year appended (`"01/15"` → `"01/15/2026"`) before the existing call. Two lines, no shared-code change.

Statement year comes from a 4-digit year on page 1. Rollover rule: if a row's month is greater than the statement's month, the row belongs to the previous year (December rows on a January statement).

## Risks / Trade-offs

- **`GENERIC` silently produces wrong rows for an unknown bank.** → Preview requires confirmation before any write; the user sees count, sum, and rows.
- **Sign convention cannot be inferred from the PDF.** Getting it wrong files purchases as income *and* corrupts categorization, since `categorize_merchant` is handed the amount (`transaction.py:69`). → Explicit per-profile `expenses_positive`; default `False` preserves today's behavior; preview surfaces the error.
- **Boilerplate removal could delete a real transaction** that appears identically on every page. → Only lines present on *all* pages are dropped; a genuine transaction repeating verbatim across every page of a statement is not a realistic case.
- **BofA behavior regression during the rewrite.** → Port the existing y-bucketing and amount rules verbatim; keep the current test assertions as the regression baseline.
- **Removing `parse_bofa_*` breaks any external caller.** → Grep confirms one caller (`upload.py:56`) and the test module. No public API.

## Migration Plan

1. Add `page_lines`, `BankProfile`, `PROFILES`, `rows_from_lines`, `parse_statement` alongside the existing functions.
2. Port tests to the new seam, asserting the current BofA results unchanged.
3. Switch `upload.py:56` to `parse_statement`, add the preview.
4. Delete `parse_bofa_page` and `parse_bofa_statement_pdf`.
5. Update `openspec/project.md`.

Rollback: steps are additive until step 4, so reverting is a single commit.

## Open Questions

- Is the BofA statement in use a checking statement (withdrawals printed with a literal `-`, so `expenses_positive=False` is correct) or a credit-card statement (purchases printed as bare positives, requiring `expenses_positive=True`)? Today's parser assumes the former; the first real import through the preview will settle it.
- Does the BofA statement print `MM/DD/YY` (as `DATE_RX` at `extract.py:6` requires) or `MM/DD` on some statement types? Determines whether year inference is exercised by `BOFA` or only by `GENERIC`.
