# Proposal: Add Monthly Net Cash Flow Trend Chart

## Why
Users need to visualize their financial trends over time to identify patterns and make informed decisions. A line chart showing monthly net cash flow (income minus expenses) provides a clear view of whether finances are improving or declining over multiple months.

## What Changes
- Add a line chart to the Statistics tab showing monthly net cash flow trend
- Display net income (income - expenses) for the last 12 months
- X-axis shows month labels (e.g., "Jan 2025", "Feb 2025")
- Y-axis shows dollar amounts with proper scaling
- Use Tkinter Canvas for drawing the chart (no external charting library required)
- Include horizontal gridlines and a zero-line indicator
- Add repository method to fetch monthly net income data for multiple months
- Chart updates when Statistics tab is refreshed

## Impact
- **Affected specs**: New capability `cashflow-visualization`
- **Affected code**:
  - Modified: `expense_tracker/gui/tabs/statistics_tab.py` (add chart rendering)
  - Modified: `expense_tracker/core/repositories.py` (add `get_monthly_cashflow_trend()` method)
- **Dependencies**:
  - **REQUIRES**: `add-statistics-tab-with-metrics` must be implemented first
  - Uses standard Tkinter Canvas (no new external dependencies)
- **User Impact**: Enhanced Statistics tab with visual trend analysis
- **No Breaking Changes**: Extends existing Statistics tab without affecting other functionality
- **Performance**: Minimal impact - single SQL query aggregating 12 months of data
