# Design: Spending Heatmap Visualization

## Architecture Overview

The spending heatmap feature introduces a tabbed interface to the main window, replacing the current single-view design:
- **Repository Layer**: Add aggregation method to `TransactionRepository`
- **GUI Layer Refactor**: Convert `MainWindow` to use `ttk.Notebook` for tabbed interface
  - **Transactions Tab**: Current transaction table view (existing functionality)
  - **Heatmap Tab**: New calendar heatmap visualization
  - **Extensible**: Framework for future tabs (metrics, charts, etc.)
- **Integration**: Tab switching via notebook widget, no separate dialogs

## Component Design

### 1. Repository Extension
**File**: `expense_tracker/core/repositories.py`

Add method to `TransactionRepository`:
```python
def get_daily_spending_for_month(self, year: int, month: int) -> dict[int, float]:
    """
    Returns a dictionary mapping day-of-month (1-31) to total spending.
    Only includes expenses (negative amounts).
    """
```

**Query Strategy**:
- Filter transactions by year/month using date range
- Group by day-of-month using SQLite's `strftime('%d', date)`
- Sum only negative amounts (expenses, not income)
- Return dictionary with day as key, total spending as value

**Performance Considerations**:
- Simple query with date range filter and GROUP BY
- No new indexes needed (date column already used in ORDER BY clauses)
- Expected < 50ms for typical monthly data (< 200 transactions)

### 2. Main Window Tabbed Interface Refactor
**File**: `expense_tracker/gui/main_window.py`

**Current Structure** (single view):
```
MainWindow(tk.Frame)
  → Toolbar
  → Transaction Table (Treeview)
  → Footer (pagination)
```

**New Structure** (tabbed):
```
MainWindow(tk.Frame)
  → ttk.Notebook (tab container)
    → Tab 1: "Transactions" (TransactionTab)
      → Toolbar
      → Transaction Table (Treeview)
      → Footer (pagination + search indicator)
    → Tab 2: "Heatmap" (HeatmapTab)
      → Month navigation header
      → Calendar grid
```

### 3. Transactions Tab Component
**File**: `expense_tracker/gui/tabs/transactions_tab.py` (new file)

New `TransactionsTab` class:
- Inherits from `tk.Frame`
- Extracts existing transaction table logic from `MainWindow`
- Encapsulates:
  - Toolbar with buttons (Add, Edit, Delete, Refresh, Import, Search)
  - Transaction Treeview table
  - Pagination footer
  - Search functionality
- Constructor takes `master`, `transaction_repo`, `merchant_repo`
- Public methods:
  - `refresh()`: Reload transaction data
  - `_add_transaction()`, `_edit_transaction()`, etc. (existing methods)

**Migration Strategy**: Move existing code from `MainWindow` to `TransactionsTab` with minimal changes.

### 4. Heatmap Tab Component
**File**: `expense_tracker/gui/tabs/heatmap_tab.py` (new file)

New `HeatmapTab` class:
- Inherits from `tk.Frame`
- Constructor takes `master`, `transaction_repo`
- Internal state: `_current_year`, `_current_month`

**Layout Structure**:
```
┌─────────────────────────────────────┐
│  [<]  January 2025  [>]             │  ← Header with navigation
├─────────────────────────────────────┤
│      Mon Tue Wed Thu Fri Sat Sun   │  ← Day-of-week labels
│  W1   1   2   3   4   5   6   7    │
│  W2   8   9  10  11  12  13  14    │  ← Week rows with day cells
│  W3  15  16  17  18  19  20  21    │
│  W4  22  23  24  25  26  27  28    │
│  W5  29  30  31                    │
└─────────────────────────────────────┘
```

**Cell Rendering**:
- Each day is a `tk.Label` or `tk.Frame` with background color
- Color gradient based on spending amount:
  - White/light gray: $0 (no spending)
  - Light green: Low spending (< 25th percentile)
  - Medium green: Medium spending (25th-75th percentile)
  - Dark green: High spending (> 75th percentile)
- Text shows day number and optionally spending amount
- Tooltip shows exact amount on hover
- Click handler to view transactions for that day

**Month Navigation**:
- Previous/Next buttons adjust `_current_year` and `_current_month`
- Month/Year picker (dropdown or entry field)
- Auto-refresh heatmap when month changes

**Calendar Logic**:
- Use Python's `calendar` module to determine:
  - First day of month (Mon=0, Sun=6)
  - Number of days in month
  - Week offsets for proper grid alignment
- Empty cells for days outside the current month (grayed out)

### 5. Refactored Main Window
**File**: `expense_tracker/gui/main_window.py`

Updated `MainWindow` class becomes a tab container:

```python
class MainWindow(tk.Frame):
    def __init__(self, master, transaction_repo, merchant_repo):
        super().__init__(master)
        self.transaction_repo = transaction_repo
        self.merchant_repo = merchant_repo
        self.master = master
        self._active_dialog = None  # Keep for other dialogs (add, edit, upload)

        # Create notebook (tab container)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.transactions_tab = TransactionsTab(
            self.notebook, transaction_repo, merchant_repo, self
        )
        self.heatmap_tab = HeatmapTab(
            self.notebook, transaction_repo
        )

        # Add tabs to notebook
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.notebook.add(self.heatmap_tab, text="Heatmap")

        # Bind tab change event for lazy loading/refresh
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event):
        """Refresh tab content when user switches tabs"""
        current_tab = self.notebook.select()
        tab_index = self.notebook.index(current_tab)
        if tab_index == 1:  # Heatmap tab
            self.heatmap_tab.refresh()
```

**Key Changes**:
- Remove `_build_toolbar()`, `_build_body()`, `_build_footer()` (moved to TransactionsTab)
- Keep `_active_dialog` management for Add/Edit/Upload dialogs (still modal)
- Notebook widget manages tab switching
- Each tab is self-contained with its own logic

### 6. Drill-Down Interaction
When user clicks a cell in the heatmap:
1. Capture the selected date (year, month, day)
2. Switch to Transactions tab
3. Apply date filter to transaction table showing only that date's transactions
4. Update search indicator to show "Filtered by date: YYYY-MM-DD"

**Implementation**:
- `HeatmapTab` gets reference to parent `MainWindow` via constructor
- Cell click handler calls `self.main_window.show_transactions_for_date(date)`
- `MainWindow` switches to Transactions tab and delegates filter to `TransactionsTab`
- `TransactionsTab` adds new method `filter_by_date(date)` to apply date filter

**Advantages over dialog**:
- Seamless navigation between visualization and data
- User can edit/delete transactions directly after drilling down
- Maintains context (can return to heatmap tab easily)
- No modal dialog interruption

## Data Flow

```
App Launch
  → MainWindow creates Notebook with two tabs
  → TransactionsTab loads (displays current page of transactions)
  → HeatmapTab created but not populated (lazy load)

User switches to "Heatmap" tab
  → Notebook <<NotebookTabChanged>> event fires
  → MainWindow._on_tab_changed() detects Heatmap tab
  → HeatmapTab.refresh() called
  → HeatmapTab queries repository.get_daily_spending_for_month(current_year, current_month)
  → Repository executes SQL aggregation
  → HeatmapTab receives dict[day, spending_amount]
  → HeatmapTab calculates color gradient thresholds
  → HeatmapTab renders calendar grid with colored cells

User clicks [Next Month] in Heatmap tab
  → Increment month, call HeatmapTab.refresh()

User clicks a day cell in Heatmap
  → HeatmapTab captures selected date
  → Calls self.main_window.show_transactions_for_date(date)
  → MainWindow switches to Transactions tab (index 0)
  → MainWindow delegates to TransactionsTab.filter_by_date(date)
  → TransactionsTab displays filtered transactions for that date

User switches back to "Heatmap" tab
  → HeatmapTab.refresh() re-renders with current month (no state lost)
```

## Color Gradient Algorithm

**Approach**: Percentile-based gradient for relative comparison within the month.

```python
def calculate_color(spending: float, percentiles: dict) -> str:
    if spending == 0:
        return "#F5F5F5"  # Light gray (no spending)
    elif spending < percentiles[25]:
        return "#C6E8C3"  # Light green
    elif spending < percentiles[75]:
        return "#7BC77D"  # Medium green
    else:
        return "#2E7D32"  # Dark green
```

**Rationale**: Percentile-based ensures meaningful color distribution even when spending varies widely month-to-month. Absolute thresholds ($0-50, $50-200, etc.) would be less flexible.

## Alternative Designs Considered

### Alt 1: Separate Modal Dialog (Original Design)
**Pros**: Simple to implement, no need to refactor MainWindow
**Cons**: Disrupts workflow, requires opening/closing dialog, harder to navigate between views
**Decision**: Rejected - tabbed interface is more modern and user-friendly

### Alt 2: Embedded Heatmap in Main Window (Side-by-Side)
**Pros**: No need for tabs, always visible alongside transactions
**Cons**: Clutters main window, reduces transaction table space, harder to implement responsive layout
**Decision**: Rejected - tabs provide better space management

### Alt 3: Canvas-Based Rendering
**Pros**: More flexible drawing, custom shapes, gradients
**Cons**: More complex code, harder to add click handlers and tooltips
**Decision**: Rejected - Tkinter Labels/Frames are simpler and sufficient

### Alt 4: matplotlib or Plotly Integration
**Pros**: Professional visualizations, zoom/pan, export
**Cons**: Heavy dependencies, embedding in Tkinter is complex, slower startup
**Decision**: Rejected - Keep dependencies minimal, Tkinter-only solution

### Alt 5: Absolute Color Thresholds
**Pros**: Consistent colors across months
**Cons**: May result in all dark cells (expensive month) or all light cells (cheap month)
**Decision**: Rejected - Percentile-based provides better relative insights

## Edge Cases

1. **Empty Month**: All cells light gray, message "No transactions this month"
2. **First/Last Day of Month**: Ensure proper calendar alignment
3. **February Leap Years**: Use `calendar.monthrange()` to handle correctly
4. **Future Months**: Allow viewing future months (will be empty until transactions exist)
5. **Large Spending Days**: Ensure text is readable on dark backgrounds (white text)
6. **No Expenses, Only Income**: Show $0 for days with only positive amounts

## Performance Targets

- **Query Time**: < 50ms for typical month (< 200 transactions)
- **Render Time**: < 150ms for full calendar grid (31 cells)
- **Total Load Time**: < 200ms from button click to visible heatmap
- **Memory**: Negligible impact (< 1MB for dialog and data)

## Testing Strategy

1. **Unit Tests**: Repository aggregation method with various date ranges
2. **Integration Tests**: Heatmap dialog creation and month navigation
3. **Manual Tests**: Visual verification of color gradients and calendar layout
4. **Edge Case Tests**: Empty months, leap years, boundary dates
