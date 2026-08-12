# Implementation Tasks

## 1. Layout Pass (bank-agnostic)
- [ ] 1.1 Add `page_lines(page) -> list[list[str]]` to `expense_tracker/utils/extract.py`, porting the y-bucketing from `parse_bofa_page` (`extract.py:15-29`) verbatim — 2-point tolerance, sorted by `x0`, empty tokens dropped
- [ ] 1.2 Keep this the only function touching the pdfplumber API, so a future engine swap is one function
- [ ] 1.3 Test that words sharing a vertical position group into one ordered line, and that words beyond the tolerance stay separate

## 2. Statement Profiles
- [ ] 2.1 Add frozen `StatementProfile` dataclass with `name`, `detect`, `date_formats`, `skip`
- [ ] 2.2 Define `BOFA_CHECKING` profile reproducing today's behavior exactly — `("%m/%d/%y",)`, skip `("total ",)`
- [ ] 2.3 Define `GENERIC` fallback profile accepting `("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d")` with the same skip prefixes
- [ ] 2.4 Register `PROFILES = (BOFA_CHECKING,)` as a flat collection keyed by (bank, statement type) — do NOT add profiles for statements without a real PDF to test against, and do NOT introduce a per-bank grouping level
- [ ] 2.5 Test that a profile is immutable

## 3. Statement Profile Detection
- [ ] 3.1 Add `detect_profile(pdf) -> StatementProfile` doing two ordered passes over `PROFILES`: match `detect` substrings against first-page text, then against `pdf.metadata` values, else return `GENERIC`
- [ ] 3.2 Confirm `GENERIC` is NOT in `PROFILES` — an empty `detect` tuple must never match (see `design.md` Decision 3)
- [ ] 3.3 Determine BofA's actual metadata substring from a real statement and populate `BOFA_CHECKING.detect`
- [ ] 3.4 Test all four paths: page-text match, metadata match, fallback to `GENERIC`, and text-outranks-metadata when both could match

## 4. Preprocessing
- [ ] 4.1 Add boilerplate removal: `Counter` over joined lines across all pages, drop lines whose count equals the page count
- [ ] 4.2 Skip removal entirely for single-page statements
- [ ] 4.3 Test that a footer repeated on every page is dropped, including one that begins with a date and ends with an amount
- [ ] 4.4 Test that a line present on some but not all pages is retained

## 5. Row Interpretation
- [ ] 5.1 Add `rows_from_lines(lines: list[list[str]], profile) -> list[dict]` taking plain token lists — no PDF types
- [ ] 5.2 Port the date-at-start / rightmost-amount / description-between rules from `extract.py:32-53`
- [ ] 5.3 Apply `profile.skip` prefixes case-insensitively against the description
- [ ] 5.4 Build the date regex from `profile.date_formats` rather than the module-level `DATE_RX`
- [ ] 5.5 Test: valid line, missing date, missing amount, numeric token inside description, skip-prefix line

## 6. Amount Parsing
- [ ] 6.1 Keep `_parse_amount` unchanged — `$`, thousands separators, leading `-`, and parentheses — preserving the sign as printed
- [ ] 6.2 Retain the existing `_parse_amount` assertions verbatim as the regression baseline
- [ ] 6.3 Assert every registered profile's `date_formats` include a year — year inference is explicitly out of scope

## 7. Public Entry Point
- [ ] 7.1 Add `parse_statement(path) -> list[dict]` composing: open → detect profile → `page_lines` per page → boilerplate removal → `rows_from_lines`
- [ ] 7.2 Confirm the return contract stays `list[{date, description, amount}]` so `TransactionService` needs no change

## 8. Import Preview
- [ ] 8.1 Add a `ttk.Treeview` to `UploadDialog` showing each parsed row's date, description, and amount
- [ ] 8.2 Show detected bank name, transaction count, and sum of amounts
- [ ] 8.3 Split `_on_upload` (`upload.py:49-74`) into parse-and-preview, then a confirm action that calls `import_transactions`
- [ ] 8.4 Show a clear message and write nothing when parsing yields zero transactions
- [ ] 8.5 Verify cancelling writes nothing to the database

## 9. Cleanup and Verification
- [ ] 9.1 Delete `parse_bofa_page` and `parse_bofa_statement_pdf`
- [ ] 9.2 Port `tests/utils/test_extract.py` to the new seam, replacing mocked-page word dicts with token lists where coordinates are irrelevant — keep the existing assertions unchanged, since BofA behavior is not meant to change
- [ ] 9.3 Update `openspec/project.md`: PDF Format constraint, PDF Statement Import section, File Structure
- [ ] 9.4 Run `ruff check .` and `pytest`
- [ ] 9.5 Import a real BofA checking statement through the preview and confirm rows, signs, and dates match what the previous parser produced
