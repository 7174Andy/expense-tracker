## 1. Repository
- [x] 1.1 Tests: pagination and count for category queries
- [x] 1.2 Add optional `limit`/`offset` params to `get_all_transactions_by_category` (defaults keep existing callers unchanged)
- [x] 1.3 Add `count_transactions_by_category(category)`

## 2. GUI
- [x] 2.1 Add funnel button next to the search bar; clicking opens a modal `FilterDialog` (Category combobox: "All Categories" + `TransactionService.get_categories()`); button styled blue when a filter is active, transparent otherwise
- [x] 2.2 Add `_filter_category` state and a `refresh()` branch mirroring the keyword-search branch (count + paginated fetch + footer indicator)
- [x] 2.3 Wire mutual exclusivity: selecting a category clears keyword/date; search/date filter and "Clear Search" reset the category filter

## 3. Validation
- [x] 3.1 Run `pytest` and `ruff check .`
