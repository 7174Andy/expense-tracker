# Implementation Tasks

## 1. Data Layer

- [x] 1.1 Add `search_by_keyword` method to TransactionRepository that accepts keyword, limit, and offset parameters
- [x] 1.2 Implement SQL query with LIKE clause for case-insensitive description matching (use `description LIKE ? COLLATE NOCASE`)
- [x] 1.3 Add `count_search_results` method to TransactionRepository that accepts keyword and returns total count
- [x] 1.4 Ensure both methods return empty list/0 when keyword is None or empty string
- [x] 1.5 Write unit tests for repository search methods with various keywords

## 2. GUI - Main Window Integration

- [x] 2.1 Update MainWindow to store current search keyword state (None when no search active)
- [x] 2.2 Update `_search_transactions` method to capture keyword from `self.qvar.get()` and store in state
- [x] 2.3 Update `refresh` method to check if search is active and call `search_by_keyword` instead of `get_all_transactions`
- [x] 2.4 Update count logic in `refresh` to use `count_search_results` when search is active
- [x] 2.5 Add search indicator label in footer showing "Search: {keyword}" when search is active
- [x] 2.6 Add "Clear Search" button in toolbar that resets search keyword to None and refreshes display
- [x] 2.7 Ensure pagination works correctly with search results (preserve keyword across page navigation)
- [x] 2.8 Handle empty search field as "clear search" (reset to show all transactions)

## 3. Testing and Validation

- [x] 3.1 Test search with single keyword
- [x] 3.2 Test search with partial text matching
- [x] 3.3 Test case-insensitive matching (e.g., "amazon" matches "AMAZON")
- [x] 3.4 Test edge cases: empty results, empty search field, special characters in keyword
- [x] 3.5 Test pagination with search results
- [x] 3.6 Test clear search functionality
- [x] 3.7 Verify search state persists across page navigation
- [x] 3.8 Run pytest to ensure no regressions in existing functionality
