# Proposal: Add Monthly Spending by Category Chart

## Why
Users need to understand how their spending is distributed across different categories to identify areas for potential savings. A bar chart showing spending breakdown by category provides clear visual insight into spending priorities and helps users make informed budget decisions.

## What Changes
- Add a horizontal bar chart to the Statistics tab showing spending breakdown by category for the selected month
- Display all expense categories with their total spending amounts
- Bars sorted by spending amount (highest to lowest)
- Each bar labeled with category name and dollar amount
- Use color-coded bars for visual distinction between categories
- Add repository method to fetch category spending aggregation for a specific month
- Chart updates when Statistics tab is refreshed or month navigation is used

## Impact
- **Affected specs**: New capability `category-breakdown-visualization`
- **Affected code**:
  - Modified: `expense_tracker/gui/tabs/statistics_tab.py` (add bar chart rendering)
  - Modified: `expense_tracker/core/repositories.py` (add `get_category_spending_breakdown()` method)
- **Dependencies**:
  - **REQUIRES**: `add-statistics-tab-with-metrics` must be implemented first
  - Uses standard Tkinter Canvas (no new external dependencies)
- **User Impact**: Enhanced Statistics tab with category spending breakdown
- **No Breaking Changes**: Extends existing Statistics tab without affecting other functionality
- **Performance**: Minimal impact - single SQL query with GROUP BY on category field
