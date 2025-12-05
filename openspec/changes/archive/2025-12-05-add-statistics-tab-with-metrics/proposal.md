# Proposal: Add Statistics Tab with Key Metrics

## Why
Users need a quick overview of their financial health without diving into detailed transactions. A statistics dashboard showing key metrics like monthly net income and top spending category provides immediate insights into spending patterns and financial trends.

## What Changes
- Add new "Statistics" tab to the main window's tabbed interface
- Display key metrics in a clean, card-based layout:
  - **Monthly Net Income**: Shows total income minus expenses for the current month
  - **Top Spending Category**: Identifies which category has the highest spending this month
- Add repository methods to calculate monthly aggregated statistics
- Implement month navigation controls (previous/next month) to view historical metrics
- Use lazy loading pattern: statistics refresh when tab becomes active
- Create `StatisticsTab` component in `expense_tracker/gui/tabs/statistics_tab.py`

## Impact
- **Affected specs**: New capability `statistics-metrics`
- **Affected code**:
  - New: `expense_tracker/gui/tabs/statistics_tab.py` (Statistics tab UI component)
  - Modified: `expense_tracker/gui/main_window.py` (add Statistics tab to notebook)
  - Modified: `expense_tracker/gui/tabs/__init__.py` (export StatisticsTab)
  - Modified: `expense_tracker/core/repositories.py` (add aggregation methods)
- **User Impact**: New Statistics tab provides quick financial overview
- **No Breaking Changes**: All existing functionality remains unchanged
- **Dependencies**: Builds on existing tabbed interface (ttk.Notebook)
- **Performance**: Minimal impact - simple SQL aggregation queries with lazy loading
