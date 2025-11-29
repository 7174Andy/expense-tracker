# Implementation Tasks

## Phase 1: Repository Layer (Foundation)

### Task 1.1: Add daily spending aggregation method
- **File**: `expense_tracker/core/repositories.py`
- **Work**: Implement `get_daily_spending_for_month(year: int, month: int) -> dict[int, float]`
- **Details**:
  - Write SQL query with date range filtering and GROUP BY day
  - Use `strftime('%d', date)` to extract day-of-month
  - Sum only negative amounts (expenses), exclude income
  - Convert results to dict with integer keys (1-31) and float values
  - Handle empty results (return empty dict)
- **Validation**: Write unit test in `tests/core/test_repository.py`
  - Test with typical month data (multiple transactions per day)
  - Test empty month
  - Test month with income and expenses (verify income excluded)
  - Verify performance < 50ms for 200 transactions

### Task 1.2: Add transactions by date retrieval method
- **File**: `expense_tracker/core/repositories.py`
- **Work**: Implement `get_transactions_for_date(target_date: date) -> list[Transaction]`
- **Details**:
  - Query transactions matching exact date
  - Order by amount DESC (largest expenses first)
  - Return empty list if no matches
  - Use existing `_row_to_transaction` helper
- **Validation**: Write unit test in `tests/core/test_repository.py`
  - Test with transactions on target date
  - Test with no transactions on target date
  - Test ordering (expenses before income, larger amounts first)

## Phase 2: Create Tab Components

### Task 2.1: Create tabs directory structure
- **Work**: Create new directory for tab components
- **Details**:
  - Create `expense_tracker/gui/tabs/` directory
  - Create `expense_tracker/gui/tabs/__init__.py`
- **Validation**: Directory exists and is a valid Python package

### Task 2.2: Extract TransactionsTab from MainWindow
- **File**: `expense_tracker/gui/tabs/transactions_tab.py` (new file)
- **Work**: Create `TransactionsTab` class by extracting existing MainWindow code
- **Details**:
  - Create class inheriting from `tk.Frame`
  - Constructor: `__init__(self, master, transaction_repo, merchant_repo, main_window)`
  - Move `_build_toolbar()`, `_build_body()`, `_build_footer()` from MainWindow
  - Move all transaction management methods: `_add_transaction()`, `_edit_transaction()`, `_delete_transaction()`, `_search_transactions()`, `_clear_search()`, etc.
  - Move pagination logic: `_previous_page()`, `_next_page()`, `refresh()`
  - Keep all instance variables: `_current_page`, `_page_size`, `_total_transactions`, `_search_keyword`, `tree`, etc.
  - Add new method: `filter_by_date(target_date: date)` for date filtering from heatmap
- **Migration Notes**: This is mostly copy-paste from MainWindow with minimal modifications
- **Validation**: TransactionsTab can be instantiated and displays correctly

### Task 2.3: Add date filter capability to TransactionsTab
- **File**: `expense_tracker/gui/tabs/transactions_tab.py`
- **Work**: Implement `filter_by_date(target_date: date)` method
- **Details**:
  - Store `_filter_date: date | None` instance variable
  - Update `refresh()` to use `get_transactions_for_date()` when filter is active
  - Update search indicator to show "Filtered by date: YYYY-MM-DD"
  - `_clear_search()` should also clear date filter
  - Reset `_current_page` to 0 when filter is applied
- **Validation**: Can filter by date and clear filter correctly

### Task 2.4: Create HeatmapTab skeleton
- **File**: `expense_tracker/gui/tabs/heatmap_tab.py` (new file)
- **Work**: Create `HeatmapTab` class structure
- **Details**:
  - Create class inheriting from `tk.Frame`
  - Constructor: `__init__(self, master, transaction_repo, main_window)`
  - Initialize state: `_current_year`, `_current_month` (default to current date)
  - Store reference to `main_window` for drill-down navigation
  - Add `refresh()` method (stub for now)
  - Pack frame with `fill=tk.BOTH, expand=True`
- **Validation**: HeatmapTab can be instantiated (empty frame)

### Task 2.5: Build heatmap header with month navigation
- **File**: `expense_tracker/gui/tabs/heatmap_tab.py`
- **Work**: Implement `_build_header()` method
- **Details**:
  - Create frame for header row
  - Add Previous Month button ("<") on left
  - Add month/year label in center (e.g., "January 2025")
  - Add Next Month button (">") on right
  - Wire buttons to `_previous_month()` and `_next_month()` methods
  - Call `_build_header()` in `__init__`
- **Validation**: Header displays with buttons (implement stub navigation methods)

### Task 2.6: Implement month navigation logic
- **File**: `expense_tracker/gui/tabs/heatmap_tab.py`
- **Work**: Implement `_previous_month()`, `_next_month()`, and update `refresh()` method
- **Details**:
  - `_previous_month()`: Decrement month, handle year rollover (Jan → Dec of previous year)
  - `_next_month()`: Increment month, handle year rollover (Dec → Jan of next year)
  - `refresh()`: Query data and re-render calendar grid
  - Update header label with new month/year
- **Validation**: Navigate between months, verify correct month/year displayed

### Task 2.7: Build calendar grid structure
- **File**: `expense_tracker/gui/tabs/heatmap_tab.py`
- **Work**: Implement `_build_calendar_grid()` method
- **Details**:
  - Create frame for calendar grid
  - Add day-of-week header row (Mon, Tue, Wed, Thu, Fri, Sat, Sun)
  - Use Python `calendar` module to determine first day of month and total days
  - Create 5 rows (weeks) x 7 columns (days) grid using `tk.Label` widgets
  - Label each cell with day number (1-31)
  - Store cell widgets in `_day_cells` dict for later color updates
  - Leave cells empty for days outside current month (grayed out)
  - Call `_build_calendar_grid()` in `__init__` after header
- **Validation**: Calendar renders for different months (Jan, Feb, Dec), verify alignment

### Task 2.8: Fetch and display spending data
- **File**: `expense_tracker/gui/tabs/heatmap_tab.py`
- **Work**: Integrate repository query into `refresh()`
- **Details**:
  - Call `self.transaction_repo.get_daily_spending_for_month(year, month)`
  - Store results in `_spending_data` dict
  - Clear previous calendar grid if it exists
  - Rebuild calendar grid with new data
  - Display "No transactions this month" message if data is empty
- **Validation**: Spending data displays for months with transactions, empty state for future months

### Task 2.9: Implement color gradient algorithm
- **File**: `expense_tracker/gui/tabs/heatmap_tab.py`
- **Work**: Implement `_calculate_percentiles()` and `_get_color_for_spending()` methods
- **Details**:
  - `_calculate_percentiles(spending_values: list[float])`: Calculate 25th and 75th percentiles
  - `_get_color_for_spending(spending: float, p25: float, p75: float) -> str`: Return color code
  - Color mapping:
    - $0: `#F5F5F5` (light gray)
    - < 25th percentile: `#C6E8C3` (light green)
    - < 75th percentile: `#7BC77D` (medium green)
    - >= 75th percentile: `#2E7D32` (dark green)
  - Handle edge case: all days have same spending (use medium green)
- **Validation**: Test with various spending distributions, verify colors assigned correctly

### Task 2.10: Apply colors to calendar cells
- **File**: `expense_tracker/gui/tabs/heatmap_tab.py`
- **Work**: Update `_build_calendar_grid()` to apply background colors
- **Details**:
  - Calculate percentiles from `_spending_data` before building grid
  - For each day cell, look up spending amount from `_spending_data`
  - Calculate color using `_get_color_for_spending()`
  - Set cell background color using `.config(bg=color)`
  - Adjust text color for readability (white on dark green, black on light colors)
  - Display day number prominently
- **Validation**: View heatmap for various months, verify color gradient is visually clear

### Task 2.11: Add cell hover tooltips
- **File**: `expense_tracker/gui/tabs/heatmap_tab.py`
- **Work**: Implement tooltip on hover showing exact spending amount
- **Details**:
  - Create `_show_tooltip(event, day, amount)` and `_hide_tooltip(event)` methods
  - Bind `<Enter>` event to show tooltip
  - Bind `<Leave>` event to hide tooltip
  - Tooltip displays "Month Day: $XX.XX" (e.g., "March 15: $125.50")
  - Use `tk.Label` with `Toplevel` for tooltip widget
  - Position tooltip near cursor
- **Validation**: Hover over cells, verify tooltip shows correct amounts

### Task 2.12: Implement day cell click handler
- **File**: `expense_tracker/gui/tabs/heatmap_tab.py`
- **Work**: Add click handler to switch to Transactions tab with date filter
- **Details**:
  - Create `_on_day_click(day: int)` method
  - Bind `<Button-1>` event on day cells to this handler
  - Construct full date from `_current_year`, `_current_month`, and clicked `day`
  - Call `self.main_window.show_transactions_for_date(date)`
  - Handle clicks on empty cells (days with $0 spending) gracefully
- **Validation**: Click day cells, verify switch to Transactions tab with correct filter

## Phase 3: Refactor MainWindow to Use Tabs

### Task 3.1: Update MainWindow to create Notebook
- **File**: `expense_tracker/gui/main_window.py`
- **Work**: Replace single-view layout with ttk.Notebook
- **Details**:
  - Import `from tkinter import ttk`
  - Import `TransactionsTab` and `HeatmapTab`
  - Remove `_build_toolbar()`, `_build_body()`, `_build_footer()` methods (now in TransactionsTab)
  - Remove all transaction-related instance variables (now in TransactionsTab)
  - In `__init__`, create `ttk.Notebook` and pack it
  - Create `TransactionsTab` and `HeatmapTab` instances
  - Add tabs to notebook: `self.notebook.add(self.transactions_tab, text="Transactions")`
  - Keep `_active_dialog` for managing Add/Edit/Upload dialogs
  - Remove old `refresh()` method (now handled by tabs)
- **Validation**: App launches with two tabs visible

### Task 3.2: Add tab change event handler
- **File**: `expense_tracker/gui/main_window.py`
- **Work**: Implement `_on_tab_changed()` to refresh tabs on switch
- **Details**:
  - Bind `<<NotebookTabChanged>>` event to `_on_tab_changed()`
  - In handler, detect which tab is active using `self.notebook.index(self.notebook.select())`
  - If Heatmap tab (index 1), call `self.heatmap_tab.refresh()`
  - Lazy loading pattern: only refresh when tab becomes active
- **Validation**: Switching tabs triggers refresh correctly

### Task 3.3: Add show_transactions_for_date method
- **File**: `expense_tracker/gui/main_window.py`
- **Work**: Implement method to switch to Transactions tab with date filter
- **Details**:
  - Create `show_transactions_for_date(target_date: date)` method
  - Switch to Transactions tab: `self.notebook.select(0)`
  - Call `self.transactions_tab.filter_by_date(target_date)`
- **Validation**: Heatmap cell click successfully filters transactions

### Task 3.4: Update TransactionsTab dialog integration
- **File**: `expense_tracker/gui/tabs/transactions_tab.py`
- **Work**: Ensure modal dialogs work correctly from TransactionsTab
- **Details**:
  - Dialogs (Add, Edit, Upload) should reference `main_window._active_dialog`
  - Pass `main_window` reference to dialog methods
  - Dialog `_open_dialog()` method should be in MainWindow, called via `self.main_window._open_dialog(...)`
  - After dialog closes, `TransactionsTab.refresh()` is called
- **Validation**: Add, Edit, Delete, Upload dialogs work from Transactions tab

## Phase 4: Testing and Validation

### Task 4.1: Write repository unit tests
- **File**: `tests/core/test_repository.py`
- **Work**: Add test cases for new repository methods
- **Details**:
  - `test_get_daily_spending_for_month_with_data()`
  - `test_get_daily_spending_for_month_empty()`
  - `test_get_daily_spending_excludes_income()`
  - `test_get_transactions_for_date_with_data()`
  - `test_get_transactions_for_date_empty()`
  - `test_get_transactions_for_date_ordering()`
- **Validation**: Run `pytest tests/core/test_repository.py -v`, all tests pass

### Task 4.2: Manual testing - Tab navigation
- **Work**: Verify tab switching and state preservation
- **Details**:
  - Switch between Transactions and Heatmap tabs multiple times
  - Verify Transactions tab preserves page number, search filter
  - Verify Heatmap tab preserves selected month across switches
  - Test performance: tab switches should be < 200ms
- **Validation**: Tab navigation is smooth and state is preserved

### Task 4.3: Manual testing - Calendar accuracy
- **Work**: Verify calendar grid alignment for edge cases
- **Details**:
  - Test February in leap year (2024) and non-leap year (2025)
  - Test months starting on Sunday vs Monday
  - Test December → January year rollover
  - Test January → December reverse year rollover
- **Validation**: Calendar days align correctly with day-of-week headers

### Task 4.4: Manual testing - Color gradient
- **Work**: Verify color gradient with real transaction data
- **Details**:
  - Import PDF statement with varied spending across the month
  - View heatmap and verify high-spending days are darker
  - Navigate to empty month, verify all cells are light gray
  - Check text contrast on all color backgrounds
- **Validation**: Colors are visually distinct and meaningful

### Task 4.5: Manual testing - Drill-down interaction
- **Work**: Verify clicking heatmap cells filters Transactions tab
- **Details**:
  - Click various day cells in Heatmap tab
  - Verify switch to Transactions tab occurs
  - Verify correct date filter is applied
  - Verify filter indicator shows correct date
  - Clear filter and verify all transactions shown
- **Validation**: Drill-down navigation works seamlessly

### Task 4.6: Manual testing - Existing functionality regression
- **Work**: Verify all existing features still work in Transactions tab
- **Details**:
  - Test Add Transaction dialog
  - Test Edit Transaction dialog
  - Test Delete Transaction
  - Test Search functionality
  - Test Pagination (Previous/Next buttons)
  - Test Import Statement (Upload dialog)
- **Validation**: No regression in existing functionality

### Task 4.7: Run existing test suite
- **Work**: Ensure all existing tests still pass
- **Details**:
  - Run `pytest tests/ -v`
  - Fix any broken tests due to MainWindow refactoring
  - Update test imports if needed (TransactionsTab vs MainWindow)
- **Validation**: All existing tests pass

## Phase 5: Documentation and Polish

### Task 5.1: Update CLAUDE.md
- **File**: `CLAUDE.md`
- **Work**: Document tabbed interface and heatmap feature
- **Details**:
  - Update GUI Architecture section to describe tabbed layout
  - Add `TransactionsTab` and `HeatmapTab` to component list
  - Document new repository methods in Key Components section
  - Add usage note: "Heatmap uses percentile-based color gradient for relative spending visualization"
  - Update file structure diagram to include `gui/tabs/` directory
- **Validation**: Review documentation for accuracy

### Task 5.2: Add __init__.py imports
- **File**: `expense_tracker/gui/tabs/__init__.py`
- **Work**: Add convenient imports for tab classes
- **Details**:
  - Add: `from .transactions_tab import TransactionsTab`
  - Add: `from .heatmap_tab import HeatmapTab`
  - Add: `__all__ = ["TransactionsTab", "HeatmapTab"]`
- **Validation**: Can import via `from expense_tracker.gui.tabs import TransactionsTab, HeatmapTab`

## Dependencies and Parallelization

**Can be done in parallel:**
- Task 1.1 and Task 1.2 (both repository methods are independent)
- Task 2.2 and Task 2.4 (TransactionsTab and HeatmapTab skeletons are independent)
- Task 2.9 (color algorithm) can be written independently of grid building

**Must be done sequentially:**
- Task 2.1 must complete before Task 2.2 and Task 2.4 (need directory structure)
- Task 1.1 must complete before Task 2.8 (fetch data depends on repository method)
- Task 2.4 must complete before Task 2.5-2.12 (need HeatmapTab skeleton)
- Task 2.2 must complete before Task 3.4 (TransactionsTab must exist)
- Phase 3 should come after Phase 2 is complete (tabs must exist before MainWindow refactor)
- Phase 4 (testing) should come after Phases 1-3 are complete

**Critical path:**
Task 2.1 → Task 2.2 → Task 2.3 → Task 3.1 → Task 3.4 → Task 4.6

**Estimated timeline:**
- Phase 1: 2-3 hours
- Phase 2: 8-10 hours (largest phase due to tab components)
- Phase 3: 2-3 hours (refactoring MainWindow)
- Phase 4: 3-4 hours (comprehensive testing)
- Phase 5: 1 hour (documentation)
- **Total: 16-21 hours of development work**
