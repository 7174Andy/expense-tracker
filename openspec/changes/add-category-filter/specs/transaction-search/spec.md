## ADDED Requirements

### Requirement: Filter transactions by category
The Transactions tab SHALL provide a funnel button next to the search bar that opens a modal filter dialog, letting the user filter the transaction table to a single category chosen from the categories currently in use. The dialog SHALL accommodate additional filter dimensions (e.g. date, amount) as future form rows. The funnel button SHALL indicate filter state: blue when a filter is active, transparent otherwise.

#### Scenario: User selects a category
- **WHEN** the user opens the filter dialog, picks a category, and applies
- **THEN** the table shows only transactions in that category, ordered by date descending, paginated at the standard page size, the footer indicator names the active category filter, and the funnel button turns blue

#### Scenario: User selects "All Categories"
- **WHEN** the user picks "All Categories" (the default entry) and applies
- **THEN** the category filter is removed, the table shows all transactions, and the funnel button returns to transparent

#### Scenario: Clearing filters
- **WHEN** the user clicks "Clear Search"
- **THEN** the category filter is reset to "All Categories" along with the keyword search and date filter

#### Scenario: Filters are mutually exclusive
- **WHEN** the user selects a category while a keyword search or date filter is active
- **THEN** the previous filter is cleared and only the category filter applies
