# Monthly Cash Flow Visualization Specification

## ADDED Requirements

### Requirement: Monthly Cash Flow Trend Calculation
The system SHALL calculate monthly net cash flow (income minus expenses) for a specified number of months, returning results in chronological order.

#### Scenario: Calculate trend for 12 months
- **GIVEN** the current month is December 2025
- **WHEN** monthly cashflow trend for 12 months is requested
- **THEN** the system returns net income values for Jan 2025 through Dec 2025 as list of (year, month, amount) tuples

#### Scenario: Handle months with no transactions
- **GIVEN** some months in the requested range have no transactions
- **WHEN** monthly cashflow trend is requested
- **THEN** the system returns 0.00 for months with no transactions

#### Scenario: Calculate trend across year boundary
- **GIVEN** the current month is February 2026 and trend for 12 months is requested
- **WHEN** monthly cashflow trend is calculated
- **THEN** the system returns data from March 2025 through February 2026

### Requirement: Line Chart Rendering
The system SHALL render a line chart displaying monthly net cash flow trend with proper axes, labels, and gridlines.

#### Scenario: Render chart with positive and negative values
- **GIVEN** monthly cashflow data contains both positive and negative values
- **WHEN** chart is rendered
- **THEN** the system displays a line chart with:
  - X-axis showing month labels (e.g., "Jan 2025")
  - Y-axis showing dollar amounts
  - Data points connected by lines
  - Horizontal gridlines for readability
  - Zero-line highlighted for reference

#### Scenario: Color code data points
- **GIVEN** monthly cashflow data is displayed
- **WHEN** rendering data points and lines
- **THEN** positive values are displayed in green and negative values in red

#### Scenario: Handle edge case with all zero values
- **GIVEN** all months have zero net income
- **WHEN** chart is rendered
- **THEN** the system displays a flat line at zero with appropriate axes

### Requirement: Axis Scaling
The system SHALL automatically scale chart axes based on the data range to ensure all values are visible and readable.

#### Scenario: Scale Y-axis for large values
- **GIVEN** monthly cashflow values range from -5000 to 10000
- **WHEN** chart is rendered
- **THEN** Y-axis scales to include both min and max values with appropriate padding

#### Scenario: Format Y-axis labels as currency
- **GIVEN** chart is rendering Y-axis labels
- **WHEN** axis labels are displayed
- **THEN** values are formatted with dollar signs (e.g., "$1000", "-$500")

#### Scenario: Format X-axis as month/year
- **GIVEN** chart is rendering X-axis labels
- **WHEN** axis labels are displayed
- **THEN** months are formatted as "MMM YYYY" (e.g., "Jan 2025", "Feb 2025")

### Requirement: Chart Integration in Statistics Tab
The system SHALL display the monthly cashflow chart in the Statistics tab below the metrics cards.

#### Scenario: Display chart on tab load
- **GIVEN** user switches to Statistics tab
- **WHEN** the tab refreshes
- **THEN** the cashflow chart is rendered with current data

#### Scenario: Chart updates with month navigation
- **GIVEN** user navigates to a different month using navigation controls
- **WHEN** the refresh occurs
- **THEN** the chart recalculates the 12-month window relative to the selected month

### Requirement: Chart Responsiveness
The system SHALL ensure the chart renders properly within the available space and maintains readability.

#### Scenario: Fit chart in available space
- **GIVEN** Statistics tab is displayed
- **WHEN** chart is rendered
- **THEN** chart fits within the tab's content area without horizontal scrolling

#### Scenario: Maintain minimum readability
- **GIVEN** chart is rendered in limited space
- **WHEN** window is resized
- **THEN** chart maintains minimum readable size for labels and data points
