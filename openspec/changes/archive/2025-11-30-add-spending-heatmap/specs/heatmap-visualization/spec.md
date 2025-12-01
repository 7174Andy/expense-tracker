# heatmap-visualization Specification

## Purpose
Provide a visual calendar heatmap interface for analyzing spending patterns by day across a selected month, integrated as a tab in the main window.

## ADDED Requirements

### Requirement: Tabbed Interface
The system SHALL implement a tabbed interface in the main window to organize different views.

#### Scenario: Main window displays tabs
- **WHEN** application launches
- **THEN** main window displays a tab bar with at least two tabs: "Transactions" and "Heatmap"
- **AND** "Transactions" tab is selected by default
- **AND** tab bar uses ttk.Notebook widget

#### Scenario: Switch to Heatmap tab
- **WHEN** user clicks on the "Heatmap" tab
- **THEN** the tab content switches to display the heatmap view
- **AND** the heatmap displays the current month by default
- **AND** the heatmap is refreshed/loaded when tab becomes active

#### Scenario: Switch back to Transactions tab
- **WHEN** user clicks on the "Transactions" tab while viewing Heatmap
- **THEN** the tab content switches to display the transaction table
- **AND** transaction table maintains its previous state (page, search filter, etc.)

### Requirement: Monthly Calendar Display
The system SHALL display a calendar-style heatmap showing daily spending for a selected month within the Heatmap tab.

#### Scenario: View heatmap in tab
- **WHEN** user switches to Heatmap tab
- **THEN** the tab displays a calendar grid with days 1-31
- **AND** the tab shows the current month and year in the header
- **AND** heatmap uses full tab space (not a modal dialog)

#### Scenario: Calendar grid layout
- **WHEN** heatmap tab is active
- **THEN** the grid has 7 columns representing days of the week (Mon-Sun)
- **AND** the grid has up to 5 rows representing weeks of the month
- **AND** each cell is labeled with the day number (1-31)
- **AND** cells for days outside the current month are empty or grayed out
- **AND** the first day of the month aligns with the correct day-of-week column

#### Scenario: Color-coded spending intensity
- **WHEN** heatmap is rendered
- **THEN** each day cell has a background color representing spending amount
- **AND** days with no spending are light gray or white
- **AND** days with low spending (< 25th percentile) are light green
- **AND** days with medium spending (25th-75th percentile) are medium green
- **AND** days with high spending (> 75th percentile) are dark green
- **AND** color intensity reflects relative spending within the displayed month

#### Scenario: Empty month display
- **WHEN** selected month has no transactions
- **THEN** all day cells are light gray
- **AND** a message indicates "No transactions this month"

### Requirement: Month Navigation
The system SHALL allow users to navigate between different months to view historical spending patterns.

#### Scenario: Navigate to next month
- **WHEN** user clicks "Next Month" button (or ">" arrow)
- **THEN** heatmap refreshes to display the next month
- **AND** header updates to show new month and year
- **AND** calendar grid updates with correct day alignment
- **AND** colors recalculate based on new month's spending data

#### Scenario: Navigate to previous month
- **WHEN** user clicks "Previous Month" button (or "<" arrow)
- **THEN** heatmap refreshes to display the previous month
- **AND** header updates to show new month and year
- **AND** calendar grid updates with correct day alignment
- **AND** colors recalculate based on new month's spending data

#### Scenario: Persist month selection across tab switches
- **WHEN** user navigates to a different month in Heatmap tab
- **AND** user switches to Transactions tab
- **AND** user switches back to Heatmap tab
- **THEN** heatmap displays the previously selected month (state is preserved)
- **AND** month selection does not reset to current month

#### Scenario: Navigate to future months
- **WHEN** user navigates to a future month (beyond current date)
- **THEN** heatmap displays the calendar grid with all cells light gray
- **AND** system does not prevent viewing future months
- **AND** future months will populate once transactions are added

### Requirement: Day Detail Interaction
The system SHALL allow users to view detailed transaction information for a specific day by interacting with heatmap cells and switching to the Transactions tab.

#### Scenario: Hover over day cell
- **WHEN** user hovers mouse over a day cell in Heatmap tab
- **THEN** a tooltip appears showing the exact spending amount for that day
- **AND** tooltip format is clear (e.g., "March 15: $125.50")
- **AND** tooltip disappears when mouse moves away

#### Scenario: Click day cell to view transactions
- **WHEN** user clicks on a day cell in Heatmap tab
- **THEN** application switches to the Transactions tab
- **AND** transaction table is filtered to show only transactions from that specific date
- **AND** a filter indicator displays the selected date (e.g., "Filtered by date: 2025-01-15")
- **AND** user can clear the filter to view all transactions again

#### Scenario: Click empty day cell
- **WHEN** user clicks on a day cell with no transactions ($0 spending)
- **THEN** application switches to the Transactions tab
- **AND** transaction table shows empty results with message "No transactions on 2025-01-15"
- **AND** filter indicator displays the selected date

### Requirement: Transactions Tab Refactoring
The system SHALL move existing transaction table functionality into a dedicated Transactions tab without losing any features.

#### Scenario: Transactions tab contains all existing features
- **WHEN** user views the Transactions tab
- **THEN** tab displays the transaction table (Treeview)
- **AND** toolbar with buttons (Add, Edit, Delete, Refresh, Import, Search, Clear Search) is visible
- **AND** search functionality works as before
- **AND** pagination footer is visible with Previous/Next buttons and page indicator
- **AND** all existing functionality (add, edit, delete, search, pagination) works identically to the original single-view design

#### Scenario: Modal dialogs work from Transactions tab
- **WHEN** user clicks "Add Transaction" button in Transactions tab
- **THEN** Add Transaction dialog opens as a modal window
- **AND** dialog behavior is identical to original implementation
- **WHEN** user closes the dialog
- **THEN** Transactions tab refreshes to show updated data

#### Scenario: Date filter integration
- **WHEN** user clicks a day cell in Heatmap tab (triggering date filter)
- **AND** switches to Transactions tab
- **THEN** transaction table is filtered by the selected date
- **AND** search indicator shows "Filtered by date: YYYY-MM-DD"
- **WHEN** user clicks "Clear Search" button
- **THEN** date filter is cleared and all transactions are shown

### Requirement: Visual Clarity and Accessibility
The system SHALL ensure the heatmap is visually clear and readable.

#### Scenario: Day number visibility
- **WHEN** heatmap is rendered
- **THEN** day numbers are clearly visible on all cells
- **AND** text color contrasts with background color (white text on dark cells, dark text on light cells)
- **AND** font size is readable (at least 10pt)

#### Scenario: Cell size and spacing
- **WHEN** heatmap is rendered
- **THEN** cells are evenly sized and spaced
- **AND** cells are large enough to display day number and optionally spending amount
- **AND** cell borders or spacing clearly separates adjacent days

#### Scenario: Legend or color key
- **WHEN** heatmap is displayed
- **THEN** a legend or color key explains the color gradient
- **AND** legend shows sample colors with spending ranges or percentile labels
- **OR** legend is omitted if tooltips provide sufficient context
