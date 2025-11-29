# Implementation Tasks

## Phase 1: Create Tab Component Structure

### Task 1.1: Create tabs directory
- **Work**: Create new directory for tab components
- **Details**:
  - Create `expense_tracker/gui/tabs/` directory
  - Create `expense_tracker/gui/tabs/__init__.py`
- **Validation**: Directory exists and is a valid Python package

### Task 1.2: Create TransactionsTab skeleton
- **File**: `expense_tracker/gui/tabs/transactions_tab.py` (new file)
- **Work**: Create TransactionsTab class structure
- **Details**:
  - Create class inheriting from `tk.Frame`
  - Constructor: `__init__(self, master, transaction_repo, merchant_repo, main_window)`
  - Initialize all state variables: `_current_page`, `_page_size`, `_total_transactions`, `_search_keyword`
  - Add stub methods: `_build_toolbar()`, `_build_body()`, `_build_footer()`, `refresh()`
- **Validation**: File can be imported, class instantiates without errors

## Phase 2: Extract Code from MainWindow

### Task 2.1: Copy _build_toolbar method
- **File**: `expense_tracker/gui/tabs/transactions_tab.py`
- **Work**: Copy `_build_toolbar()` from MainWindow
- **Details**:
  - Copy entire method implementation
  - Update `_open_dialog()` calls to `self.main_window._open_dialog()`
  - Ensure all button commands reference `self._add_transaction`, etc.
- **Validation**: Toolbar displays correctly when TransactionsTab is added to a test window

### Task 2.2: Copy _build_body method
- **File**: `expense_tracker/gui/tabs/transactions_tab.py`
- **Work**: Copy `_build_body()` from MainWindow
- **Details**:
  - Copy Treeview creation and configuration
  - Copy event bindings (double-click to edit)
  - Create `self.tree` instance variable
- **Validation**: Transaction table displays correctly

### Task 2.3: Copy _build_footer method
- **File**: `expense_tracker/gui/tabs/transactions_tab.py`
- **Work**: Copy `_build_footer()` from MainWindow
- **Details**:
  - Copy pagination controls (Previous, Next, page label)
  - Copy search indicator label
  - Ensure button commands reference `self._previous_page`, `self._next_page`
- **Validation**: Footer displays with pagination controls

### Task 2.4: Copy pagination methods
- **File**: `expense_tracker/gui/tabs/transactions_tab.py`
- **Work**: Copy `_previous_page()`, `_next_page()`, and `refresh()` methods
- **Details**:
  - Copy all three methods exactly as they are in MainWindow
  - Ensure `refresh()` uses `self.transaction_repo` correctly
  - Ensure pagination logic with `self._current_page`, `self._page_size` works
- **Validation**: Can navigate between pages, refresh loads data correctly

### Task 2.5: Copy CRUD operation methods
- **File**: `expense_tracker/gui/tabs/transactions_tab.py`
- **Work**: Copy `_add_transaction()`, `_edit_transaction()`, `_delete_transaction()` methods
- **Details**:
  - Copy all three methods
  - Update `self._open_dialog(...)` to `self.main_window._open_dialog(...)`
  - Copy `_get_selected_ids()` helper method
- **Validation**: Can add, edit, delete transactions via dialogs

### Task 2.6: Copy search methods
- **File**: `expense_tracker/gui/tabs/transactions_tab.py`
- **Work**: Copy `_search_transactions()` and `_clear_search()` methods
- **Details**:
  - Copy both methods
  - Ensure `self.qvar` (search entry variable) is created in `_build_toolbar()`
  - Ensure search indicator updates correctly
- **Validation**: Search and clear search work correctly

### Task 2.7: Copy upload statement method
- **File**: `expense_tracker/gui/tabs/transactions_tab.py`
- **Work**: Copy `_upload_statement()` method
- **Details**:
  - Copy method that opens UploadDialog
  - Update `self._open_dialog(...)` to `self.main_window._open_dialog(...)`
- **Validation**: Can open upload dialog and import PDF statement

### Task 2.8: Wire up __init__ method
- **File**: `expense_tracker/gui/tabs/transactions_tab.py`
- **Work**: Complete `__init__` to build UI and load data
- **Details**:
  - Call `self._build_toolbar()`
  - Call `self._build_body()`
  - Call `self._build_footer()`
  - Call `self.refresh()` to load initial data
  - Pack frame with `fill=tk.BOTH, expand=True`
- **Validation**: TransactionsTab displays fully functional UI on instantiation

## Phase 3: Update MainWindow

### Task 3.1: Update MainWindow imports
- **File**: `expense_tracker/gui/main_window.py`
- **Work**: Add imports for Notebook and TransactionsTab
- **Details**:
  - Add `from tkinter import ttk` (if not already imported)
  - Add `from expense_tracker.gui.tabs import TransactionsTab`
- **Validation**: Imports work without errors

### Task 3.2: Refactor MainWindow __init__
- **File**: `expense_tracker/gui/main_window.py`
- **Work**: Replace single-view layout with Notebook
- **Details**:
  - Remove calls to `_build_toolbar()`, `_build_body()`, `_build_footer()`
  - Remove `self.refresh()` call
  - Remove all state variables (`_current_page`, `_page_size`, etc.) - now in TransactionsTab
  - Create `self.notebook = ttk.Notebook(self)`
  - Pack notebook: `self.notebook.pack(fill=tk.BOTH, expand=True)`
  - Create `self.transactions_tab = TransactionsTab(self.notebook, transaction_repo, merchant_repo, self)`
  - Add tab: `self.notebook.add(self.transactions_tab, text="Transactions")`
  - Keep `self._active_dialog = None`
- **Validation**: MainWindow creates Notebook with Transactions tab

### Task 3.3: Update _open_dialog method
- **File**: `expense_tracker/gui/main_window.py`
- **Work**: Update `_open_dialog()` to refresh TransactionsTab
- **Details**:
  - Keep entire `_open_dialog()` method as-is
  - Change `self.refresh()` to `self.transactions_tab.refresh()` in the `on_close()` handler
  - Change final `self.refresh()` to `self.transactions_tab.refresh()`
- **Validation**: Dialogs close and refresh the Transactions tab correctly

### Task 3.4: Remove unused methods from MainWindow
- **File**: `expense_tracker/gui/main_window.py`
- **Work**: Delete all methods moved to TransactionsTab
- **Details**:
  - Remove `_build_toolbar()`, `_build_body()`, `_build_footer()`
  - Remove `refresh()`, `_previous_page()`, `_next_page()`
  - Remove `_add_transaction()`, `_edit_transaction()`, `_delete_transaction()`, `_get_selected_ids()`
  - Remove `_search_transactions()`, `_clear_search()`
  - Remove `_upload_statement()`
  - Keep only `__init__()` and `_open_dialog()`
- **Validation**: MainWindow is now minimal (< 50 lines)

## Phase 4: Update Exports

### Task 4.1: Export TransactionsTab from tabs package
- **File**: `expense_tracker/gui/tabs/__init__.py`
- **Work**: Add exports for tab classes
- **Details**:
  - Add `from .transactions_tab import TransactionsTab`
  - Add `__all__ = ["TransactionsTab"]`
- **Validation**: Can import via `from expense_tracker.gui.tabs import TransactionsTab`

## Phase 5: Testing

### Task 5.1: Manual testing - Basic functionality
- **Work**: Verify all features work in Transactions tab
- **Details**:
  - Launch application
  - Verify Transactions tab displays
  - Verify transaction table shows data
  - Test Add Transaction dialog
  - Test Edit Transaction dialog
  - Test Delete Transaction
- **Validation**: All CRUD operations work correctly

### Task 5.2: Manual testing - Search and pagination
- **Work**: Verify search and pagination work correctly
- **Details**:
  - Test Search functionality (enter keyword, click Search)
  - Test Clear Search button
  - Test Previous/Next pagination buttons
  - Test pagination with search results
- **Validation**: Search and pagination work identically to original

### Task 5.3: Manual testing - Import functionality
- **Work**: Verify PDF import works
- **Details**:
  - Click "Import Statement" button
  - Select a Bank of America PDF
  - Verify transactions are imported
  - Verify Transactions tab refreshes
- **Validation**: Import works correctly

### Task 5.4: Manual testing - UI appearance
- **Work**: Verify visual consistency
- **Details**:
  - Check that tab bar displays at top
  - Verify "Transactions" tab is selected by default
  - Verify theme (ttkbootstrap "darkly") applies correctly
  - Resize window and verify layout adapts
- **Validation**: UI looks correct and theme works

### Task 5.5: Run existing test suite
- **Work**: Ensure all existing tests pass
- **Details**:
  - Run `pytest tests/ -v`
  - Fix any broken tests (likely import path changes only)
  - No functional test changes should be needed
- **Validation**: All tests pass

## Phase 6: Documentation

### Task 6.1: Update CLAUDE.md
- **File**: `CLAUDE.md`
- **Work**: Document tabbed interface architecture
- **Details**:
  - Update GUI Architecture section to mention tabbed layout
  - Add `TransactionsTab` to component list
  - Document that MainWindow is now a tab container
  - Update file structure to include `gui/tabs/` directory
- **Validation**: Documentation accurately reflects new architecture

## Dependencies and Parallelization

**Must be done sequentially:**
- Task 1.1 must complete before Task 1.2 (need directory structure)
- Task 1.2 must complete before Phase 2 (need skeleton class)
- Phase 2 must complete before Phase 3 (TransactionsTab must exist before MainWindow refactor)
- Phase 3 must complete before Phase 5 (need refactored MainWindow to test)

**Can be done in parallel within Phase 2:**
- Task 2.1-2.7 can be done in any order (all are independent extractions)

**Critical path:**
Task 1.1 → Task 1.2 → Task 2.8 → Task 3.2 → Task 5.1

**Estimated timeline:**
- Phase 1: 30 minutes
- Phase 2: 2-3 hours (extraction and testing)
- Phase 3: 1-2 hours (MainWindow refactor)
- Phase 4: 15 minutes
- Phase 5: 2-3 hours (comprehensive testing)
- Phase 6: 30 minutes
- **Total: 6-9 hours of development work**

## Risk Mitigation

- **Low Risk**: This is a pure refactoring with no logic changes
- **Easy Rollback**: Git revert can undo all changes cleanly
- **Incremental Testing**: Test each method extraction individually
- **No Data Risk**: No database changes, no data loss risk
