# Proposal: Add Spending Heatmap Visualization

## Overview
Add a new Heatmap tab to the main window for visualizing transaction spending patterns. The heatmap displays total spending per day in a monthly calendar-style grid, helping users identify spending behavior patterns over time.

## Dependencies
**DEPENDS ON**: `add-tabbed-interface` - This proposal requires the tabbed interface to be implemented first.

## Motivation
Users need visual tools to understand their spending habits and identify patterns. A heatmap visualization, similar to GitHub's contribution graph but adapted for expense tracking, provides an intuitive way to see:
- Which days of the month have the highest spending
- Spending patterns across weeks
- Visual comparison of spending intensity over time

## Scope
This change adds a new Heatmap tab to the existing tabbed interface:

**In Scope:**
- New "Heatmap" tab with monthly calendar grid visualization
- Monthly calendar grid layout (weeks as rows, days 1-31 as columns)
- Color-coded cells based on spending amount (darker = more spending)
- Month navigation controls (previous/next month)
- Tooltip showing exact spending amounts on hover
- Repository methods to aggregate spending by day and retrieve transactions by date
- Click interaction to switch to Transactions tab filtered by selected date
- Lazy loading: heatmap refreshes when tab becomes active

**Out of Scope:**
- Timestamp/hour-of-day data (current data model only stores dates)
- Category-based heatmap breakdown (future enhancement)
- Year-view heatmap (GitHub-style, future enhancement)
- Export/sharing of heatmap visualization
- Changes to transaction data model or database schema

## User Impact
- **New Feature**: Users gain a visual spending analysis tool accessible via Heatmap tab
- **No Breaking Changes**: All existing functionality remains unchanged
- **Improved Navigation**: Seamless switching between transaction list and heatmap visualization via tabs
- **Performance**: Minimal impact - aggregation queries are simple date-based GROUP BY, lazy loading ensures heatmap only refreshes when viewed
- **UI Changes**:
  - New "Heatmap" tab added to existing tab bar (alongside "Transactions" tab)
  - Click tab to view spending heatmap for current month
  - Click heatmap cells to filter transactions by date

## Dependencies
- **REQUIRES**: `add-tabbed-interface` change must be applied first
- No external library changes required (uses existing Tkinter/ttkbootstrap)
- Builds on existing TransactionRepository infrastructure
- Works with current SQLite schema (no migrations needed)
- Uses existing tabbed interface framework (MainWindow with ttk.Notebook)

## Success Criteria
1. Heatmap tab appears in the tab bar alongside Transactions tab
2. Heatmap tab displays monthly calendar grid showing spending for the current month
3. Users can navigate between months using previous/next buttons
4. Cell colors accurately represent relative spending intensity (percentile-based gradient)
5. Hovering over cells shows exact spending amounts in tooltips
6. Clicking a heatmap cell switches to Transactions tab filtered by that date
7. Heatmap refreshes when tab becomes active (lazy loading)
8. Tab switching is smooth and responsive (< 200ms to switch and render)
9. All existing tests pass, ensuring no regression

## Alternatives Considered
1. **Separate Modal Dialog**: Rejected in favor of tab-based approach for better user experience and seamless navigation
2. **Hour-of-day heatmap**: Rejected due to lack of timestamp data in current model (only dates stored)
3. **Category breakdown heatmap**: Deferred as future enhancement (more complex)
4. **Year-view GitHub-style**: Deferred for simpler monthly view first
5. **Side-by-side layout**: Embedding heatmap alongside transaction table. Rejected due to space constraints and complexity

## Open Questions
None - design approach confirmed with user.
