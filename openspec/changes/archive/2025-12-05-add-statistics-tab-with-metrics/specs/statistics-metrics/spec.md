# Statistics Metrics Specification

## ADDED Requirements

### Requirement: Monthly Net Income Calculation
The system SHALL calculate and display monthly net income by summing all income (positive amounts) and subtracting all expenses (negative amounts) for a specified month.

#### Scenario: Calculate net income for month with both income and expenses
- **GIVEN** a month has transactions with amounts [100.00, -50.00, -25.00, 200.00]
- **WHEN** monthly net income is calculated
- **THEN** the system returns 225.00 (100 + 200 - 50 - 25)

#### Scenario: Calculate net income for month with only expenses
- **GIVEN** a month has only expense transactions [-100.00, -50.00]
- **WHEN** monthly net income is calculated
- **THEN** the system returns -150.00

#### Scenario: Calculate net income for month with no transactions
- **GIVEN** a month has no transactions
- **WHEN** monthly net income is calculated
- **THEN** the system returns 0.00

### Requirement: Top Spending Category Identification
The system SHALL identify and display the category with the highest total spending (sum of negative amounts) for a specified month.

#### Scenario: Identify top spending category
- **GIVEN** a month has expenses: Groceries [-100.00, -50.00], Restaurants [-75.00], Transportation [-25.00]
- **WHEN** top spending category is requested
- **THEN** the system returns ("Groceries", 150.00)

#### Scenario: Handle month with no expenses
- **GIVEN** a month has no expense transactions or only income transactions
- **WHEN** top spending category is requested
- **THEN** the system returns None

#### Scenario: Handle tie between categories
- **GIVEN** a month has expenses: Groceries [-100.00], Restaurants [-100.00]
- **WHEN** top spending category is requested
- **THEN** the system returns one of the tied categories (deterministic ordering by category name)

### Requirement: Statistics Tab Display
The system SHALL provide a Statistics tab in the main window that displays monthly financial metrics in a card-based layout.

#### Scenario: Display statistics for current month
- **GIVEN** user opens the Statistics tab
- **WHEN** the tab loads
- **THEN** the system displays net income and top spending category for the current month

#### Scenario: Navigate to previous month
- **GIVEN** user is viewing statistics for November 2025
- **WHEN** user clicks the "Previous" button
- **THEN** the system displays statistics for October 2025

#### Scenario: Navigate to next month
- **GIVEN** user is viewing statistics for November 2025
- **WHEN** user clicks the "Next" button
- **THEN** the system displays statistics for December 2025

### Requirement: Lazy Loading for Statistics Tab
The system SHALL refresh statistics data only when the Statistics tab becomes active, not continuously.

#### Scenario: Statistics refresh on tab activation
- **GIVEN** user is viewing the Transactions tab
- **WHEN** user switches to the Statistics tab
- **THEN** the system queries the database and refreshes displayed metrics

#### Scenario: No refresh when tab is inactive
- **GIVEN** user is viewing the Transactions tab
- **WHEN** transactions are added or modified
- **THEN** the Statistics tab does not refresh until user switches to it

### Requirement: Currency Formatting
The system SHALL display monetary values with proper currency formatting and color coding based on positive/negative values.

#### Scenario: Display positive net income
- **GIVEN** monthly net income is 500.00
- **WHEN** displayed in the Statistics tab
- **THEN** the value is shown as "$500.00" in green color

#### Scenario: Display negative net income
- **GIVEN** monthly net income is -150.00
- **WHEN** displayed in the Statistics tab
- **THEN** the value is shown as "-$150.00" in red color

#### Scenario: Display zero net income
- **GIVEN** monthly net income is 0.00
- **WHEN** displayed in the Statistics tab
- **THEN** the value is shown as "$0.00" in default color
