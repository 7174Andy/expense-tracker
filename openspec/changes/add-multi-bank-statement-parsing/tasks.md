# Implementation Tasks

## 1. Layout Pass (bank-agnostic)
- [ ] 1.1 Add `page_lines(page) -> list[list[str]]` to `expense_tracker/utils/extract.py`, porting the y-bucketing from `parse_bofa_page` (`extract.py:15-29`) verbatim — 2-point tolerance, sorted by `x0`, empty tokens dropped
- [ ] 1.2 Keep this the only function touching the pdfplumber API, so a future engine swap is one function
- [ ] 1.3 Test that words sharing a vertical position group into one ordered line, and that words beyond the tolerance stay separate

## 2. Bank Profiles
- [ ] 2.1 Add frozen `BankProfile` dataclass with `name`, `detect`, `date_formats`, `skip`, `expenses_positive=False`
- [ ] 2.2 Define `BOFA` profile reproducing today's behavior: `("%m/%d/%y",)`, skip `("total ",)`, `expenses_positive=False`
- [ ] 2.3 Define `GENERIC` fallback profile accepting `("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d")` with the same skip prefixes
- [ ] 2.4 Register `PROFILES = (BOFA,)` — do NOT add profiles for banks without a real statement to test against
- [ ] 2.5 Test that a profile is immutable

## 3. Bank Detection
- [ ] 3.1 Add `detect_profile(pdf) -> BankProfile`: match `detect` substrings against `pdf.metadata` values, then first-page text, else return `GENERIC`
- [ ] 3.2 Determine BofA's actual metadata substring from a real statement and populate `BOFA.detect`
- [ ] 3.3 Test all three paths: metadata match, page-text match, and fallback to `GENERIC`

## 4. Preprocessing
- [ ] 4.1 Add boilerplate removal: `Counter` over joined lines across all pages, drop lines whose count equals the page count
- [ ] 4.2 Skip removal entirely for single-page statements
- [ ] 4.3 Test that a footer repeated on every page is dropped, including one that begins with a date and ends with an amount
- [ ] 4.4 Test that a line present on some but not all pages is retained

## 5. Row Interpretation
- [ ] 5.1 Add `rows_from_lines(lines: list[list[str]], profile, statement_year=None) -> list[dict]` taking plain token lists — no PDF types
- [ ] 5.2 Port the date-at-start / rightmost-amount / description-between rules from `extract.py:32-53`
- [ ] 5.3 Apply `profile.skip` prefixes case-insensitively against the description
- [ ] 5.4 Build the date regex from `profile.date_formats` rather than the module-level `DATE_RX`
- [ ] 5.5 Test: valid line, missing date, missing amount, numeric token inside description, skip-prefix line

## 6. Amount Signs
- [ ] 6.1 Keep `_parse_amount` handling `$`, thousands separators, leading `-`, and parentheses
- [ ] 6.2 Invert the parsed amount when `profile.expenses_positive` is set
- [ ] 6.3 Test both sign conventions, retaining the existing `_parse_amount` assertions as the regression baseline

## 7. Year Inference
- [ ] 7.1 Add `statement_year(pdf) -> int | None` scraping a 4-digit year from page 1
- [ ] 7.2 For year-less `date_formats`, append the inferred year to the raw token before calling `parse_date_from_str` — leave `utils/date.py` unchanged
- [ ] 7.3 Assign the preceding year when a row's month exceeds the statement month
- [ ] 7.4 Raise a clear error when dates lack a year and no statement year can be found
- [ ] 7.5 Test the January-statement / December-row rollover

## 8. Public Entry Point
- [ ] 8.1 Add `parse_statement(path) -> list[dict]` composing: open → detect profile → `page_lines` per page → boilerplate removal → `rows_from_lines`
- [ ] 8.2 Confirm the return contract stays `list[{date, description, amount}]` so `TransactionService` needs no change

## 9. Import Preview
- [ ] 9.1 Add a `ttk.Treeview` to `UploadDialog` showing each parsed row's date, description, and amount
- [ ] 9.2 Show detected bank name, transaction count, and sum of amounts
- [ ] 9.3 Split `_on_upload` (`upload.py:49-74`) into parse-and-preview, then a confirm action that calls `import_transactions`
- [ ] 9.4 Show a clear message and write nothing when parsing yields zero transactions
- [ ] 9.5 Verify cancelling writes nothing to the database

## 10. Cleanup
- [ ] 10.1 Delete `parse_bofa_page` and `parse_bofa_statement_pdf`
- [ ] 10.2 Rewrite `tests/utils/test_extract.py` against the new seam, replacing mocked-page word dicts with token lists where coordinates are irrelevant
- [ ] 10.3 Update `openspec/project.md`: PDF Format constraint, PDF Statement Import section, File Structure
- [ ] 10.4 Run `ruff check .` and `pytest`
- [ ] 10.5 Import a real BofA statement through the preview and confirm the rows, signs, and dates are correct — this resolves both Open Questions in `design.md`
