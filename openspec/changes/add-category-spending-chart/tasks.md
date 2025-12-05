# Implementation Tasks

## 1. Repository Layer
- [ ] 1.1 Add `get_category_spending_breakdown(year: int, month: int) -> list[tuple[str, float]]` method to TransactionRepository
- [ ] 1.2 Method returns list of (category, total_spending) tuples sorted by amount descending
- [ ] 1.3 Only include expenses (negative amounts), exclude income transactions
- [ ] 1.4 Write unit tests for category breakdown calculation

## 2. Chart Rendering
- [ ] 2.1 Create `_render_category_chart()` method in StatisticsTab
- [ ] 2.2 Implement horizontal bar chart layout with category labels and bars
- [ ] 2.3 Add proper scaling for bar widths based on max spending value
- [ ] 2.4 Display spending amount at the end of each bar (formatted as currency)
- [ ] 2.5 Use distinct colors for bars to improve visual differentiation
- [ ] 2.6 Handle edge case: display message when no expenses exist for the month

## 3. Integration with Statistics Tab
- [ ] 3.1 Add Canvas widget to StatisticsTab layout for category chart
- [ ] 3.2 Update `refresh()` method to redraw category chart based on selected month
- [ ] 3.3 Ensure chart layout works well with other visualizations on the tab
- [ ] 3.4 Add scrolling if many categories exist (more than can fit in visible area)

## 4. Testing and Validation
- [ ] 4.1 Run pytest to ensure all tests pass
- [ ] 4.2 Manual testing: verify chart displays correct category breakdown
- [ ] 4.3 Manual testing: verify chart handles edge cases (no expenses, single category, many categories)
- [ ] 4.4 Manual testing: verify chart updates correctly with month navigation
- [ ] 4.5 Run ruff linter and fix any issues
