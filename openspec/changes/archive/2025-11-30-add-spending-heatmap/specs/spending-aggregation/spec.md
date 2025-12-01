# spending-aggregation Specification

## Purpose
Provide repository methods to aggregate transaction spending data by day for heatmap visualization.

## ADDED Requirements

### Requirement: Daily Spending Aggregation
The system SHALL provide a repository method to aggregate total spending by day for a given month.

#### Scenario: Get daily spending for current month
- **WHEN** repository method `get_daily_spending_for_month(year, month)` is called
- **THEN** method returns a dictionary mapping day-of-month (1-31) to total spending amount
- **AND** spending amounts are calculated by summing all negative transaction amounts (expenses only)
- **AND** positive amounts (income) are excluded from the aggregation
- **AND** only transactions matching the specified year and month are included
- **AND** days with no transactions are omitted from the returned dictionary (not included as $0)

#### Scenario: Aggregate expenses only
- **WHEN** a day has both expenses (negative amounts) and income (positive amounts)
- **THEN** only expense amounts are summed for that day
- **AND** income amounts are ignored
- **AND** returned value for that day represents total expenses only

#### Scenario: Multiple transactions on same day
- **WHEN** multiple transactions exist on the same day
- **THEN** all expense amounts for that day are summed
- **AND** returned dictionary has a single entry for that day with the total
- **EXAMPLE**: Day 15 has transactions: -$50.00, -$25.00, -$10.00
- **THEN** returned value for day 15 is $85.00 (absolute value)

#### Scenario: Handle empty month
- **WHEN** no transactions exist for the specified month
- **THEN** method returns an empty dictionary {}
- **AND** no error or exception is raised

#### Scenario: Query performance
- **WHEN** method is called for a typical month (< 200 transactions)
- **THEN** query executes in less than 50 milliseconds
- **AND** uses efficient SQL with date filtering and GROUP BY

### Requirement: Transactions by Date Retrieval
The system SHALL provide a repository method to retrieve all transactions for a specific date.

#### Scenario: Get transactions for specific date
- **WHEN** repository method `get_transactions_for_date(date)` is called
- **THEN** method returns a list of all transactions matching that exact date
- **AND** transactions are ordered by amount DESC (largest expenses first)
- **AND** list includes both expenses (negative) and income (positive) amounts
- **AND** empty list is returned if no transactions exist for that date

#### Scenario: Date parameter format
- **WHEN** method is called with a Python `date` object
- **THEN** method correctly converts date to ISO format for SQL query
- **AND** matches transactions stored as "YYYY-MM-DD" in the database

#### Scenario: Include all transaction details
- **WHEN** transactions are returned
- **THEN** each Transaction object includes all fields: id, date, amount, category, description
- **AND** transaction objects are fully hydrated (no missing fields)

### Requirement: SQL Query Optimization
The system SHALL implement efficient SQL queries for aggregation operations.

#### Scenario: Use date range filtering
- **WHEN** aggregating spending for a month
- **THEN** SQL query uses WHERE clause with date range:
  - `WHERE date >= 'YYYY-MM-01' AND date < 'YYYY-(MM+1)-01'`
- **AND** query leverages existing date column (no new index required)
- **AND** query avoids full table scans

#### Scenario: Group by day extraction
- **WHEN** aggregating by day-of-month
- **THEN** SQL query uses `strftime('%d', date)` to extract day component
- **AND** GROUP BY clause groups by day-of-month
- **AND** SUM aggregates only negative amounts (expenses)
- **EXAMPLE SQL**: `SELECT strftime('%d', date) as day, SUM(ABS(amount)) FROM transactions WHERE date >= ? AND date < ? AND amount < 0 GROUP BY day`

#### Scenario: Return type conversion
- **WHEN** SQL results are returned
- **THEN** results are converted to a Python dictionary with integer keys (day) and float values (spending)
- **AND** day values are integers in range 1-31
- **AND** spending values are positive floats (absolute values of negative amounts)
