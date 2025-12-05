# Category Spending Breakdown Visualization Specification

## ADDED Requirements

### Requirement: Category Spending Aggregation
The system SHALL calculate total spending for each expense category in a specified month, returning results sorted by spending amount in descending order.

#### Scenario: Calculate spending breakdown for month with multiple categories
- **GIVEN** a month has expenses: Groceries [-150.00, -50.00], Restaurants [-75.00], Transportation [-25.00]
- **WHEN** category spending breakdown is requested
- **THEN** the system returns [("Groceries", 200.00), ("Restaurants", 75.00), ("Transportation", 25.00)]

#### Scenario: Exclude income transactions
- **GIVEN** a month has transactions: Groceries [-100.00], Salary [2000.00], Restaurants [-50.00]
- **WHEN** category spending breakdown is requested
- **THEN** the system returns [("Groceries", 100.00), ("Restaurants", 50.00)] and excludes Salary

#### Scenario: Handle month with no expenses
- **GIVEN** a month has no expense transactions
- **WHEN** category spending breakdown is requested
- **THEN** the system returns an empty list

#### Scenario: Handle uncategorized expenses
- **GIVEN** a month has expenses with category "Uncategorized" [-100.00]
- **WHEN** category spending breakdown is requested
- **THEN** the system includes "Uncategorized" in the results

### Requirement: Horizontal Bar Chart Rendering
The system SHALL render a horizontal bar chart displaying category spending breakdown with labels and amounts.

#### Scenario: Render bar chart with multiple categories
- **GIVEN** category spending data contains multiple categories with varying amounts
- **WHEN** bar chart is rendered
- **THEN** the system displays horizontal bars:
  - Category name label on the left
  - Bar width proportional to spending amount
  - Dollar amount displayed at the end of each bar
  - Bars sorted from highest to lowest spending

#### Scenario: Color code category bars
- **GIVEN** bar chart is rendered with multiple categories
- **WHEN** displaying bars
- **THEN** each category uses a distinct color for visual differentiation

#### Scenario: Handle edge case with no expenses
- **GIVEN** selected month has no expenses
- **WHEN** bar chart rendering is requested
- **THEN** the system displays a message "No expenses for this month"

### Requirement: Bar Scaling and Layout
The system SHALL scale bar widths proportionally based on spending amounts to ensure proper visual representation.

#### Scenario: Scale bars relative to maximum spending
- **GIVEN** category spending values are [200.00, 100.00, 50.00]
- **WHEN** bars are rendered
- **THEN** the largest bar (200.00) uses full available width and others scale proportionally

#### Scenario: Format amounts as currency
- **GIVEN** category spending amounts are displayed on bars
- **WHEN** rendering amount labels
- **THEN** values are formatted with dollar signs and two decimal places (e.g., "$150.00")

#### Scenario: Maintain minimum bar width for small amounts
- **GIVEN** a category has very small spending compared to others
- **WHEN** bar is rendered
- **THEN** bar maintains a minimum visible width to show the category exists

### Requirement: Chart Integration in Statistics Tab
The system SHALL display the category spending bar chart in the Statistics tab, updating based on the selected month.

#### Scenario: Display chart on tab load
- **GIVEN** user switches to Statistics tab
- **WHEN** the tab refreshes
- **THEN** the category chart displays spending breakdown for the current selected month

#### Scenario: Update chart with month navigation
- **GIVEN** user is viewing Statistics tab for November 2025
- **WHEN** user navigates to December 2025
- **THEN** the category chart updates to show December's spending breakdown

#### Scenario: Chart coexists with other visualizations
- **GIVEN** Statistics tab contains multiple charts and metrics
- **WHEN** tab is displayed
- **THEN** category chart renders in its designated area without overlapping other content

### Requirement: Chart Scrolling for Many Categories
The system SHALL provide scrolling capability when the number of categories exceeds the visible area.

#### Scenario: Display scrollbar for many categories
- **GIVEN** selected month has more than 10 expense categories
- **WHEN** bar chart is rendered
- **THEN** a vertical scrollbar appears allowing user to view all categories

#### Scenario: Maintain chart readability with scrolling
- **GIVEN** category chart has scrolling enabled
- **WHEN** user scrolls through categories
- **THEN** category labels, bars, and amounts remain aligned and readable
