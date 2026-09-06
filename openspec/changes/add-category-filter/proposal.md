# Change: Filter transactions by category

## Why
Users can search transactions by description keyword and filter by date, but there is no way to view all transactions in a category (e.g. everything in "Groceries", or every "Uncategorized" transaction that needs attention).

## What Changes
- Add a funnel button next to the search bar on the Transactions tab; clicking it opens a modal filter dialog with a Category picker ("All Categories" plus every category in use). Future filter options (date, amount, ...) become additional rows in the dialog.
- The funnel button shows filter state: blue (primary style) when a filter is active, transparent (link style) otherwise.
- Applying a category filters the table to that category, with pagination; the footer indicator names the active filter.
- "Clear Search" resets the filter options along with keyword/date filters.
- Category filter, keyword search, and date filter remain mutually exclusive (matching existing filter behavior).
- Extend `TransactionRepository.get_all_transactions_by_category()` with optional `limit`/`offset`, and add `count_transactions_by_category()` for pagination.

## Impact
- Affected specs: transaction-search (new capability)
- Affected code:
  - `expense_tracker/core/transaction_repository.py` (pagination params + count method)
  - `expense_tracker/gui/dialogs/filter.py` (new modal filter dialog)
  - `expense_tracker/gui/tabs/transactions_tab.py` (funnel button, filter state, refresh branch)
  - `tests/core/test_repository.py` (pagination/count tests)
