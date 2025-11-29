# Transaction Search

## ADDED Requirements

### Requirement: Keyword Search
The system SHALL allow users to search transactions by keyword matching against the description field.

#### Scenario: Search by keyword
- **WHEN** user enters a keyword in the search field and clicks Search
- **THEN** only transactions containing the keyword (case-insensitive) in the description are returned
- **AND** results are ordered by date DESC

#### Scenario: Empty search field
- **WHEN** user clicks Search with an empty search field
- **THEN** all transactions are returned (same as clearing search)

#### Scenario: No matching results
- **WHEN** user searches for a keyword with no matches
- **THEN** an empty transaction list is displayed
- **AND** pagination shows "Page 0 of 0" or appropriate empty state

#### Scenario: Partial text matching
- **WHEN** user enters partial text (e.g., "AMAZ")
- **THEN** transactions with descriptions containing that text are returned (e.g., "AMAZON", "AMAZON.COM")

### Requirement: Search State Management
The system SHALL maintain search state and provide visual indication when search is active.

#### Scenario: Display search results
- **WHEN** search is performed
- **THEN** main window shows only transactions matching the keyword
- **AND** pagination works correctly with search results
- **AND** page count reflects filtered result set

#### Scenario: Search indicator
- **WHEN** search is active
- **THEN** a visual indicator shows that results are filtered
- **AND** the current search keyword is displayed

#### Scenario: Clear search
- **WHEN** user clears the search field and clicks Search
- **THEN** search state is reset
- **AND** main window displays all transactions
- **AND** search indicator is removed

#### Scenario: Preserve search across pagination
- **WHEN** search is active and user navigates to next/previous page
- **THEN** search remains applied to the new page
- **AND** page count reflects search result set

### Requirement: Repository Search Method
The system SHALL provide a repository method that accepts a keyword and returns matching transactions with pagination support.

#### Scenario: Search with keyword
- **WHEN** repository search method is called with a keyword
- **THEN** SQL query uses LIKE with wildcards for case-insensitive matching
- **AND** results are ordered by date DESC
- **AND** pagination (limit/offset) is applied to search results

#### Scenario: Count search results
- **WHEN** repository count method is called with a keyword
- **THEN** total count of matching transactions is returned
- **AND** count is used to calculate total pages for pagination
