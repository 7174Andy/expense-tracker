# Design: Tabbed Interface Refactor

## Architecture Overview

This refactor introduces a tabbed interface to the main window while preserving all existing functionality:
- **GUI Layer Refactor**: Convert `MainWindow` to use `ttk.Notebook` for tab management
- **Component Extraction**: Extract transaction table logic into `TransactionsTab` component
- **Extensibility**: Create framework for future tabs (visualizations, analytics, settings)
- **Zero Functional Change**: All existing features work identically

## Component Design

### 1. Current MainWindow Structure

**File**: `expense_tracker/gui/main_window.py`

**Current Layout**:
```
MainWindow(tk.Frame)
  → _build_toolbar()      # Buttons: Add, Edit, Delete, Refresh, Import, Search
  → _build_body()         # Transaction Treeview table
  → _build_footer()       # Pagination controls
```

**Current State**:
- `_current_page`, `_page_size`, `_total_transactions`, `_search_keyword`
- `tree` (Treeview widget)
- `_active_dialog` (modal dialog management)

### 2. New Directory Structure

Create `expense_tracker/gui/tabs/` for tab components:
```
expense_tracker/gui/
├── tabs/
│   ├── __init__.py           # Export TransactionsTab
│   └── transactions_tab.py   # Transactions table component
├── dialogs/                  # Existing dialogs (unchanged)
└── main_window.py            # Refactored to use Notebook
```

### 3. TransactionsTab Component

**File**: `expense_tracker/gui/tabs/transactions_tab.py` (new file)

**Purpose**: Encapsulate all transaction table functionality in a reusable tab component.

**Class Definition**:
```python
class TransactionsTab(tk.Frame):
    def __init__(self, master, transaction_repo, merchant_repo, main_window):
        super().__init__(master)
        self.transaction_repo = transaction_repo
        self.merchant_repo = merchant_repo
        self.main_window = main_window  # For dialog management

        # State variables (moved from MainWindow)
        self._current_page = 0
        self._page_size = 100
        self._total_transactions = 0
        self._search_keyword = None

        # Build UI
        self._build_toolbar()
        self._build_body()
        self._build_footer()

        # Initial load
        self.refresh()
```

**Methods** (all extracted from MainWindow):
- `_build_toolbar()`: Create toolbar with buttons
- `_build_body()`: Create Treeview table
- `_build_footer()`: Create pagination controls
- `refresh()`: Reload transaction data
- `_previous_page()`, `_next_page()`: Pagination
- `_add_transaction()`, `_edit_transaction()`, `_delete_transaction()`: CRUD operations
- `_search_transactions()`, `_clear_search()`: Search functionality
- `_upload_statement()`: Import PDF
- `_get_selected_ids()`: Helper for selection
- `_open_dialog()`: Delegate to `main_window._open_dialog()`

**Migration Notes**:
- This is mostly copy-paste from MainWindow
- Change `self._open_dialog(...)` to `self.main_window._open_dialog(...)`
- All instance variables remain the same
- No logic changes

### 4. Refactored MainWindow

**File**: `expense_tracker/gui/main_window.py`

**New Structure**:
```python
class MainWindow(tk.Frame):
    def __init__(self, master, transaction_repo, merchant_repo):
        super().__init__(master)
        self.transaction_repo = transaction_repo
        self.merchant_repo = merchant_repo
        self.master = master
        self._active_dialog = None  # Keep for modal dialog management

        # Create notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create Transactions tab
        self.transactions_tab = TransactionsTab(
            self.notebook, transaction_repo, merchant_repo, self
        )

        # Add tab to notebook
        self.notebook.add(self.transactions_tab, text="Transactions")

    def _open_dialog(self, dialog_class, *args, **kwargs):
        """Modal dialog management (unchanged from original)"""
        if self._active_dialog is not None and self._active_dialog.winfo_exists():
            self._active_dialog.lift()
            self._active_dialog.focus_set()
            return

        dialog = dialog_class(self.master, *args, **kwargs)
        self._active_dialog = dialog

        def on_close():
            if dialog.winfo_exists():
                dialog.destroy()
            self._active_dialog = None
            self.transactions_tab.refresh()  # Refresh active tab

        dialog.protocol("WM_DELETE_WINDOW", on_close)
        dialog.transient(self.master)
        dialog.grab_set()
        self.master.wait_window(dialog)
        self._active_dialog = None
        self.transactions_tab.refresh()
```

**Removed Methods**:
- `_build_toolbar()`, `_build_body()`, `_build_footer()` → Moved to TransactionsTab
- `refresh()`, `_previous_page()`, `_next_page()` → Moved to TransactionsTab
- All transaction CRUD methods → Moved to TransactionsTab
- Search methods → Moved to TransactionsTab

**Kept Methods**:
- `_open_dialog()`: Still needed for modal dialog management

### 5. Tab Initialization and Lazy Loading

**Current Behavior**:
- MainWindow calls `self.refresh()` in `__init__` to load initial data

**New Behavior**:
- TransactionsTab calls `self.refresh()` in `__init__` to load initial data
- Future tabs can implement lazy loading (only refresh when tab becomes active)

**No Lazy Loading Yet**: For this refactor, we keep the same behavior (immediate load on startup). Lazy loading will be added when a second tab is introduced.

## Data Flow

```
App Launch
  → MainWindow.__init__()
  → Create ttk.Notebook
  → Create TransactionsTab (with transaction_repo, merchant_repo, main_window)
  → TransactionsTab.__init__()
    → _build_toolbar()
    → _build_body()
    → _build_footer()
    → refresh() # Load initial data
  → Add TransactionsTab to Notebook with text="Transactions"

User clicks "Add Transaction"
  → TransactionsTab._add_transaction()
  → Calls self.main_window._open_dialog(AddExpenseDialog, ...)
  → MainWindow._open_dialog() opens modal dialog
  → On dialog close, MainWindow calls self.transactions_tab.refresh()

User clicks "Search"
  → TransactionsTab._search_transactions()
  → Updates self._search_keyword
  → Calls self.refresh()
  → Treeview updates with filtered results
```

## Migration Checklist

### Phase 1: Create TransactionsTab
1. Create `expense_tracker/gui/tabs/__init__.py`
2. Create `expense_tracker/gui/tabs/transactions_tab.py`
3. Copy `_build_toolbar()`, `_build_body()`, `_build_footer()` from MainWindow
4. Copy all state variables (`_current_page`, etc.)
5. Copy all methods (`refresh()`, `_previous_page()`, CRUD methods, search methods)
6. Update `_open_dialog()` calls to `self.main_window._open_dialog()`

### Phase 2: Update MainWindow
1. Remove all methods copied to TransactionsTab
2. Keep only `_open_dialog()` method
3. Create `ttk.Notebook` in `__init__`
4. Create `TransactionsTab` instance
5. Add tab to notebook

### Phase 3: Update Imports
1. Add `from expense_tracker.gui.tabs import TransactionsTab` to main_window.py
2. Export TransactionsTab in `expense_tracker/gui/tabs/__init__.py`

### Phase 4: Testing
1. Run application, verify Transactions tab displays
2. Test all CRUD operations (Add, Edit, Delete)
3. Test Search functionality
4. Test Pagination (Previous/Next)
5. Test Import Statement (Upload)
6. Run pytest to ensure no regressions

## Edge Cases

1. **Dialog Refresh**: When a dialog closes, the active tab must refresh. MainWindow now calls `self.transactions_tab.refresh()` instead of `self.refresh()`.
2. **Tab Bar with One Tab**: The notebook will show a tab bar even with only one tab. This is expected and provides visual consistency for when future tabs are added.
3. **Window Resize**: The notebook automatically handles resize events, so no changes needed.
4. **Theme Compatibility**: ttk.Notebook is compatible with ttkbootstrap "darkly" theme (used in the app).

## Performance Considerations

- **No Performance Impact**: The refactor doesn't change data loading or rendering logic
- **Memory**: Minimal increase (~1-2KB for Notebook widget)
- **Startup Time**: Identical to original (single tab loads on startup)
- **Future Optimization**: Lazy loading can be added when second tab is introduced

## Testing Strategy

1. **Manual Testing**: Verify all features work identically to original
   - Add Transaction
   - Edit Transaction
   - Delete Transaction
   - Search functionality
   - Pagination (Previous/Next)
   - Import Statement (Upload PDF)

2. **Automated Testing**: Run existing test suite
   - All existing tests should pass without modification
   - If tests import MainWindow directly, they may need import path updates

3. **Visual Testing**: Ensure UI looks correct
   - Tab bar displays at top
   - "Transactions" tab is selected by default
   - Transaction table displays correctly

## Rollback Plan

If issues arise, this refactor can be easily rolled back:
1. Git revert the changes
2. All original code is preserved in TransactionsTab
3. No data migrations or schema changes to undo
