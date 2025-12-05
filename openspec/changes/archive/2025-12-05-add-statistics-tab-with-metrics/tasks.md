# Implementation Tasks

## 1. Repository Layer
- [x] 1.1 Add `get_monthly_net_income(year: int, month: int) -> float` method to TransactionRepository
- [x] 1.2 Add `get_top_spending_category(year: int, month: int) -> tuple[str, float] | None` method to TransactionRepository
- [x] 1.3 Write unit tests for new repository methods

## 2. Statistics Tab UI
- [x] 2.1 Create `StatisticsTab` class in `expense_tracker/gui/tabs/statistics_tab.py`
- [x] 2.2 Implement card-based layout for displaying metrics
- [x] 2.3 Add month navigation controls (previous/next buttons, current month label)
- [x] 2.4 Implement `refresh()` method to reload statistics when tab is activated
- [x] 2.5 Add proper formatting for currency values (negative in red, positive in green)

## 3. Integration
- [x] 3.1 Export `StatisticsTab` from `expense_tracker/gui/tabs/__init__.py`
- [x] 3.2 Update `MainWindow` to create and add Statistics tab to notebook
- [x] 3.3 Update `_on_tab_changed()` in MainWindow to refresh Statistics tab when selected
- [x] 3.4 Test tab switching and lazy loading behavior

## 4. Testing and Validation
- [x] 4.1 Run pytest to ensure all tests pass
- [x] 4.2 Manual testing: verify metrics calculations are correct
- [x] 4.3 Manual testing: verify month navigation works properly
- [x] 4.4 Run ruff linter and fix any issues
