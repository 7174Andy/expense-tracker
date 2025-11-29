# Change: Add Transaction Keyword Search

## Why

The application currently has a search UI (search entry field and button in the toolbar) but no functional implementation. Users need the ability to search transactions by keyword to quickly find specific expenses by description without manually browsing through paginated results.

## What Changes

- Add keyword search functionality to the repository layer
- Implement search method that searches across transaction descriptions (case-insensitive)
- Update main window to display search results and allow users to clear search
- Add pagination support for search results

## Impact

- Affected specs: transaction-search (new capability)
- Affected code:
  - [expense_tracker/core/repositories.py](expense_tracker/core/repositories.py) - Add search_by_keyword method to TransactionRepository
  - [expense_tracker/gui/main_window.py](expense_tracker/gui/main_window.py) - Update search button handler and add search state management
