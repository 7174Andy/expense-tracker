# Implementation Tasks

## 1. Repository Layer
- [ ] 1.1 Add `get_monthly_cashflow_trend(num_months: int = 12) -> list[tuple[int, int, float]]` method to TransactionRepository
- [ ] 1.2 Method returns list of (year, month, net_income) tuples for the last N months
- [ ] 1.3 Write unit tests for cashflow trend calculation

## 2. Chart Rendering
- [ ] 2.1 Create `_render_cashflow_chart()` method in StatisticsTab
- [ ] 2.2 Implement chart layout: title, axes, gridlines, data points, and connecting lines
- [ ] 2.3 Add proper scaling for Y-axis based on min/max values
- [ ] 2.4 Format X-axis labels as "MMM YYYY" (e.g., "Jan 2025")
- [ ] 2.5 Add horizontal zero-line indicator for visual reference
- [ ] 2.6 Use color coding: positive values in green, negative values in red

## 3. Integration with Statistics Tab
- [ ] 3.1 Add Canvas widget to StatisticsTab layout below metrics cards
- [ ] 3.2 Update `refresh()` method to redraw chart when tab is activated
- [ ] 3.3 Ensure chart resizes properly with window

## 4. Testing and Validation
- [ ] 4.1 Run pytest to ensure all tests pass
- [ ] 4.2 Manual testing: verify chart displays correct trend over 12 months
- [ ] 4.3 Manual testing: verify chart handles edge cases (no data, all negative, all positive)
- [ ] 4.4 Run ruff linter and fix any issues
