## Context

`expense_tracker/utils/extract.py` (70 lines) is the entire PDF surface, with one caller at `gui/dialogs/upload.py:56`. It does two jobs in one loop:

1. **Layout reconstruction** (`extract.py:15-29`) — pull words with coordinates, bucket by `round(top/2)*2` to rebuild table rows, sort each bucket by `x0`. Deliberately ignores pdfplumber's table detection, since statement tables often have no ruling lines.
2. **Row interpretation** (`extract.py:32-53`) — keep a line only if `tokens[0]` matches `^\d{2}/\d{2}/\d{2}$` and some token matches an amount pattern (scanned right-to-left); everything between becomes the description.

Job 1 is bank-agnostic. Job 2 is *mostly* bank-agnostic — "starts with a date, ends with an amount" describes most US statements. The BofA-specific parts are narrow: the date format, the junk lines to skip, and the sign convention.

Constraint driving the whole design: **only Bank of America statements are available for testing.** Any other bank's profile would be unverifiable guesswork.

## Goals / Non-Goals

**Goals**
- Adding the next bank — or the next statement type from a bank already supported — is a one-entry append to `PROFILES`, with no new function, file, or branch in the parser.
- Bank-specific row logic becomes testable without constructing mocked PDF page objects.
- An unknown bank is attempted via a generic profile, and any misparse is visible to the user before it reaches the database.

**Non-Goals**
- Profiles for statements we cannot test. Two ship: `BOFA_CHECKING` and `GENERIC`.
- Credit-card statements. Out of scope entirely — no such statement is available to test against, and its sign convention, header, and layout would all be guesswork. Upgrade path when one appears: add an `expenses_positive: bool` field to `StatementProfile` (one field plus one negation at the parse site), register a sibling profile with a page-text discriminator, and rely on text-before-metadata detection to pick it over `BOFA_CHECKING`. Until then a credit statement falls to `BOFA_CHECKING` and the preview shows its purchases as positives — visible, not silent.
- An explicit ETL orchestrator class. Monopoly's `Pipeline` holds `passwords` and a handler across extract/transform/load stages; here extract is `parse_statement()` and load is `TransactionService.import_transactions` — two calls with no shared state. The transform stage was year inference, which is out of scope below.
- OCR for scanned/image-only statements. No such statements exist in use today.
- Encrypted/password-protected PDF support. Add when a password-protected statement actually appears.
- Validating parsed totals against a statement's declared total (see Decision 4).
- Year inference for statements printing year-less dates (`MM/DD`). The BofA statement in use prints `MM/DD/YY`, and every `GENERIC` date format carries a year, so nothing would exercise the code. Upgrade path when a year-less statement appears: add the year-less format to that bank's profile, scrape a 4-digit year from page 1, append it to the raw token before `parse_date_from_str` (leaving `utils/date.py` untouched), and assign the preceding year when a row's month exceeds the statement month.
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

### Decision 3: Profile-driven generic parser, keyed by (bank, statement type).

```python
@dataclass(frozen=True)
class StatementProfile:
    name: str                         # "BofA Checking" — one bank AND statement type
    detect: tuple[str, ...]           # substrings sought in page-1 text, then PDF metadata
    date_formats: tuple[str, ...]     # ("%m/%d/%y",) — must include a year
    skip: tuple[str, ...]             # description prefixes to drop ("total ", "balance ")
```

The unit is a **(bank, statement type)** pair, in one flat collection. This comes from monopoly's `handler.py`: each of its banks holds a list of `statement_configs`, and `StatementHandler` picks between them at parse time by searching for a `header_pattern`, returning a `DebitStatement` or a `CreditStatement`. The reason is that one institution's debit and credit statements differ in layout and carry opposite sign conventions.

Monopoly needs two config levels (bank → statement configs), a handler to walk them, and a `BaseStatement`/`DebitStatement`/`CreditStatement` hierarchy. Flattening to one profile list collapses all three into a single detection pass: statement types are sibling entries, not a nested grouping. Same expressiveness, no handler, no class tree.

Only the naming and the flat shape are adopted now — credit-card support itself is a Non-Goal above. `BOFA_CHECKING` is named for what it is so a sibling can be added later without renaming or restructuring; the flat tuple is what a list of profiles would be anyway, so this costs nothing today.

Detection is two ordered passes over `PROFILES`: **page-1 text first, then metadata**, then `GENERIC`. A profile matches when **any** of its `detect` substrings is found. Text outranks metadata specifically because of the case above — statements from one bank are produced by the same software, so their metadata is likely identical and cannot discriminate them, while page text can. Metadata-first would let the less specific signal win and the discriminator never run. pdfplumber exposes `pdf.metadata`, so neither pass needs a new dependency.

Implementation trap: `GENERIC` carries an empty `detect` tuple and MUST NOT be registered in `PROFILES`. It is reached only as the explicit fallback — an `all()`-based match over an empty tuple is vacuously true, so a registered `GENERIC` would match the first statement it saw and shadow every real profile.

Rejected: a bank dropdown in `UploadDialog`. It pushes a question onto the user that metadata answers for free, and `GENERIC` already handles the unknown case. Reconsider if detection proves unreliable across real statements.

### Decision 4: Preview before import, not total-validation.

Monopoly validates that parsed amounts sum to the statement's declared total. That needs a per-profile regex locating where each bank prints its total — untestable beyond BofA, and it catches only one failure class (dropped rows), not wrong signs, wrong years, or phantom rows.

A preview table showing count, sum, and every parsed row catches all of those, needs no per-bank config, and is what makes pointing `GENERIC` at an unknown bank safe. This matters because duplicate detection (`transaction.py:73`) will not save the user from rows that are wrong but unique.

### Decision 5: No untriggered code paths.

The design ships nothing that no available statement exercises. Year inference was cut because BofA prints `MM/DD/YY`; sign inversion (`expenses_positive`) was cut because BofA checking prints withdrawals with a literal `-`. Both have upgrade paths recorded in Non-Goals, each a handful of lines, and neither is speculatively built.

The cost of this discipline is that the first credit-card statement imports its purchases as income. That is accepted because the preview makes it visible before anything is written, and because guessing a sign convention for a statement format nobody has read is not meaningfully safer than not having the field at all.

### Decision 6: One preprocessing step, and it is not one of monopoly's.

Monopoly preprocesses via `PdfConfig` before any text is read: `page_range` (slice pages), `page_bbox` (`page.set_cropbox()` per bank), `remove_vertical_text` (redact where `line["dir"] != (1, 0)`), OCR through `ocrmypdf` when a page has under 10 characters, and decryption via `unlock_document()`. This design adopts none of them, and adds one they lack: dropping lines repeated on every page.

The divergence follows from opposite architectures. Monopoly's `PdfPage.lines` is `raw_text.split("\n")` — it delegates layout reconstruction to `pdftotext`, then applies a strict per-bank `transaction_pattern` regex that rejects footers on its own. This design reconstructs lines from word coordinates and applies one permissive generic rule, so junk must be removed *before* interpretation rather than rejected during it. Boilerplate removal is load-bearing here; monopoly's steps are load-bearing for a `pdftotext` pipeline this project does not have.

Per step: `page_range` is unnecessary because the date-and-amount row filter already discards cover and terms pages. `remove_vertical_text` is unnecessary because vertical marginalia stacks characters at distinct y-values, producing one-token lines that the existing `len(tokens) < 3` guard drops — pdfplumber itself does not filter by text direction (no `upright` parameter; `line_dir_rotated`/`char_dir_rotated` retain rotated text). OCR and decryption are Non-Goals above.

`page_bbox` is the one with genuine value — cropping marketing sidebars and legal columns. It is deferred because choosing a bounding box requires a statement whose junk survives the existing filters; guessing one risks cropping out transactions. If junk ever survives, adding an optional `bbox` field to `StatementProfile` and calling `page.crop()` in `page_lines` is the next preprocessing step.

Also noted for later: monopoly's `StatementConfig.transaction_bound` is an x-coordinate threshold separating debit and credit columns. `page_lines` already has `x0` for every word and discards it after sorting, so a two-column statement is addressable without new extraction work.

## Risks / Trade-offs

- **`GENERIC` silently produces wrong rows for an unknown bank.** → Preview requires confirmation before any write; the user sees count, sum, and rows.
- **A statement printing expenses as positives imports them as income**, which also corrupts categorization, since `categorize_merchant` is handed the amount (`transaction.py:69`). No shipped profile has this convention, and none is guessed at. → The preview surfaces it before any write: purchases appear as positive amounts and the sum has the wrong sign. Recovery is the `expenses_positive` upgrade path in Non-Goals.
- **Boilerplate removal could delete a real transaction** that appears identically on every page. → Only lines present on *all* pages are dropped; a genuine transaction repeating verbatim across every page of a statement is not a realistic case.
- **BofA behavior regression during the rewrite.** → Port the existing y-bucketing and amount rules verbatim; keep the current test assertions as the regression baseline.
- **Removing `parse_bofa_*` breaks any external caller.** → Grep confirms one caller (`upload.py:56`) and the test module. No public API.

## Migration Plan

1. Add `page_lines`, `StatementProfile`, `PROFILES`, `rows_from_lines`, `parse_statement` alongside the existing functions.
2. Port tests to the new seam, asserting the current BofA results unchanged.
3. Switch `upload.py:56` to `parse_statement`, add the preview.
4. Delete `parse_bofa_page` and `parse_bofa_statement_pdf`.
5. Update `openspec/project.md`.

Rollback: steps are additive until step 4, so reverting is a single commit.

## Resolved Questions

- **Statement type: checking.** Withdrawals are printed with a literal `-`, so preserving the printed sign is correct for `BOFA_CHECKING` and matches today's behavior. This is why sign inversion is out of scope.
- **Date format: `MM/DD/YY`.** `DATE_RX` at `extract.py:6` is correct, `BOFA_CHECKING.date_formats = ("%m/%d/%y",)`, and year inference was dropped from scope as a result (see Non-Goals).

Consequence: the `BOFA_CHECKING` profile reproduces current behavior exactly. This change is a refactor plus preprocessing plus preview, with **no intended behavior change** for the statements in use — so the existing test assertions in `tests/utils/test_extract.py` are a valid regression baseline, not tests to be rewritten for new expectations.
