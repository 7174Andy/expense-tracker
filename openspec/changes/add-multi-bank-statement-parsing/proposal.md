# Proposal: Generalize PDF Statement Parsing to Multiple Banks

## Why
PDF import only understands Bank of America statements. `expense_tracker/utils/extract.py` hardcodes one date format, one set of junk-line rules, and one sign convention into functions named `parse_bofa_*`, so supporting a second institution today means copying the whole parser. The parsing rule that actually matters — "a transaction line starts with a date and ends with an amount" — is not BofA-specific and already generalizes; only a handful of constants around it are bank-specific.

Inspired by [benjamin-awd/monopoly](https://github.com/benjamin-awd/monopoly), which parses 17 institutions from declarative per-bank config rather than per-bank parsers.

## What Changes
- Split `extract.py` into a bank-agnostic layout pass (`page_lines`) and a profile-driven interpretation pass (`rows_from_lines`), replacing `parse_bofa_page` / `parse_bofa_statement_pdf` with a single public `parse_statement(path)`.
- Add a frozen `StatementProfile` dataclass holding the only genuinely statement-specific values: detection substrings, date formats, skip prefixes, and sign convention. A profile keys on **(bank, statement type)** in one flat collection, so a bank issuing both checking and credit-card statements is two sibling profiles — not a nested per-bank grouping as in monopoly's `bank.statement_configs` + `StatementHandler`.
- Ship exactly two profiles: `BOFA_CHECKING` (tested against real statements) and `GENERIC` (fallback). **No speculative profiles for untested statements.**
- Detect the profile from page-1 text, then PDF metadata, falling back to `GENERIC` so unknown banks are attempted rather than rejected. Text outranks metadata because two statement types from one bank share metadata and can only be told apart by text.
- Add a boilerplate-removal preprocessing pass that drops lines repeated on every page (headers/footers), computed generically with `Counter` — no per-bank keyword lists.
- Normalize amount signs per profile so credit-card statements (expenses printed as positives) do not import purchases as income.
- Add a preview step to `UploadDialog`: show parsed rows with count and sum, require confirmation before writing to the database.
- **BREAKING** (internal only): `parse_bofa_statement_pdf` and `parse_bofa_page` are removed. Sole caller is `upload.py:56`; no public API or database schema is affected.

## Impact
- **Affected specs**: New capability `statement-import`
- **Affected code**:
  - Rewritten: `expense_tracker/utils/extract.py` (~150 lines, single file)
  - Modified: `expense_tracker/gui/dialogs/upload.py` (preview table, confirm-before-import)
  - Rewritten: `tests/utils/test_extract.py` (row logic becomes testable without mocked PDF pages)
  - Updated: `openspec/project.md` (PDF Format constraint, File Structure notes)
- **Dependencies**: None added. Benchmarks rejected switching PDF engines — see `design.md`.
- **Unaffected**: `TransactionService.import_transactions` already owns categorization and duplicate detection (`services/transaction.py:62-77`), so the parser contract stays `list[{date, description, amount}]` and nothing downstream changes.
- **User Impact**: Non-BofA statements are attempted instead of silently mis-parsed; preview prevents bad imports. **No behavior change for the BofA checking statements in use** — the `BOFA_CHECKING` profile reproduces today's parsing exactly.
- **Performance**: Neutral. Preprocessing adds one `Counter` pass over already-extracted lines.
