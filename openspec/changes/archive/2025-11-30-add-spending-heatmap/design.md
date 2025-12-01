# Design: Spending Heatmap Visualization

## Architecture Overview

The spending heatmap feature adds a new tab to the existing tabbed interface:
- **Repository Layer**: Add aggregation method to `TransactionRepository`
- **GUI Layer**: Add new `HeatmapTab` to the existing `ttk.Notebook`
  - **Heatmap Tab**: New calendar heatmap visualization
- **Integration**: Tab switching via existing notebook widget, no separate dialogs

**Note**: The tabbed UI refactor (MainWindow with ttk.Notebook and TransactionsTab extraction) has already been completed and is in production.

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

### 2. Heatmap Tab Component
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

### 3. Main Window Integration
**File**: `expense_tracker/gui/main_window.py`

Add the HeatmapTab to the existing MainWindow:

```python
# In __init__ method, after creating TransactionsTab:
self.heatmap_tab = HeatmapTab(
    self.notebook, transaction_repo
)
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

**Changes Required**:
- Import `HeatmapTab` from `expense_tracker.gui.tabs`
- Instantiate HeatmapTab and add to notebook
- Add `_on_tab_changed` event handler for lazy loading

### 4. Drill-Down Interaction
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
  → MainWindow creates Notebook (already has Transactions tab)
  → HeatmapTab created and added to notebook
  → HeatmapTab not populated until first viewed (lazy load)

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

### Alt 1: Separate Modal Dialog
**Pros**: Simple to implement, no changes to existing MainWindow structure
**Cons**: Disrupts workflow, requires opening/closing dialog, harder to navigate between views
**Decision**: Rejected - leveraging existing tab infrastructure is more user-friendly and consistent

### Alt 2: Embedded Heatmap in Transactions Tab (Side-by-Side)
**Pros**: Always visible alongside transactions
**Cons**: Clutters transaction view, reduces table space, harder to implement responsive layout
**Decision**: Rejected - separate tab provides better space management

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
- **Total Load Time**: < 200ms from tab switch to visible heatmap
- **Memory**: Negligible impact (< 1MB for tab and data)

## Testing Strategy

1. **Unit Tests**: Repository aggregation method with various date ranges
2. **Integration Tests**: HeatmapTab creation, month navigation, and drill-down
3. **Manual Tests**: Visual verification of color gradients and calendar layout
4. **Edge Case Tests**: Empty months, leap years, boundary dates
