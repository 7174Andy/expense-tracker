## ADDED Requirements

### Requirement: Bank Profile Configuration
The system SHALL express bank-specific statement parsing rules as declarative, immutable profiles rather than per-bank parsing functions. A profile SHALL define the bank name, detection substrings, accepted date formats, description prefixes to skip, and the statement's amount sign convention.

Adding support for a new bank SHALL require only registering an additional profile, with no new parsing function, module, or conditional branch in the parser.

#### Scenario: Profile drives parsing rules
- **WHEN** a statement is parsed with a given bank profile
- **THEN** the profile's date formats, skip prefixes, and sign convention are the only bank-specific inputs to row interpretation

#### Scenario: Adding a new bank
- **WHEN** a developer adds support for an additional bank whose statements follow the date-then-amount row layout
- **THEN** the change is limited to registering one new profile entry
- **AND** no existing parsing function is modified

#### Scenario: Profiles are immutable
- **WHEN** code attempts to mutate a registered profile's fields
- **THEN** the attempt raises an error

### Requirement: Bank Detection with Generic Fallback
The system SHALL identify the bank profile for a statement by matching the profile's detection substrings against the PDF's document metadata, then against the text of the first page. A profile SHALL be considered a match when **any** of its detection substrings is found. A profile declaring no detection substrings SHALL never match. When no profile matches, the system SHALL fall back to a generic profile rather than rejecting the file.

#### Scenario: Recognized bank via metadata
- **WHEN** a statement's PDF metadata contains a substring registered by a bank profile
- **THEN** that profile is selected for parsing

#### Scenario: Recognized bank via page text
- **WHEN** no profile matches the PDF metadata but the first page's text contains a profile's detection substring
- **THEN** that profile is selected for parsing

#### Scenario: Unrecognized bank
- **WHEN** a statement matches no registered profile in either metadata or first-page text
- **THEN** the generic profile is used
- **AND** parsing proceeds instead of raising an error

#### Scenario: Profile with no detection substrings
- **WHEN** a profile declares an empty set of detection substrings
- **THEN** it is never selected by detection

### Requirement: Bank-Agnostic Layout Reconstruction
The system SHALL rebuild statement table rows from word positions rather than relying on the PDF library's table detection, because statement tables frequently lack ruling lines. Words SHALL be grouped into lines by vertical position within a tolerance and ordered by horizontal position within each line.

Layout reconstruction SHALL contain no bank-specific logic and SHALL be the only component that depends on the PDF library's API.

#### Scenario: Words grouped into a row
- **WHEN** a page contains words at differing horizontal positions sharing approximately the same vertical position
- **THEN** those words are returned as a single ordered line, left to right

#### Scenario: Separate rows kept separate
- **WHEN** a page contains words whose vertical positions differ by more than the grouping tolerance
- **THEN** those words are returned as separate lines

#### Scenario: Engine isolation
- **WHEN** the underlying PDF library is replaced
- **THEN** only layout reconstruction requires modification

### Requirement: Boilerplate Line Removal
The system SHALL discard lines that appear on every page of a statement before interpreting rows, treating them as headers and footers. Detection SHALL be computed from the statement's own content, without per-bank keyword lists.

#### Scenario: Repeated footer removed
- **WHEN** a multi-page statement carries an identical footer line on every page
- **THEN** that line is excluded from row interpretation

#### Scenario: Footer resembling a transaction
- **WHEN** a repeated header or footer begins with a date and ends with an amount
- **THEN** it is excluded and produces no transaction

#### Scenario: Line on some pages retained
- **WHEN** a line appears on some but not all pages of a statement
- **THEN** it is retained for row interpretation

#### Scenario: Single-page statement
- **WHEN** a statement has exactly one page
- **THEN** no lines are discarded as boilerplate

### Requirement: Transaction Row Extraction
The system SHALL interpret a reconstructed line as a transaction when the line begins with a token matching one of the profile's date formats and contains a token matching a monetary amount. The rightmost matching amount token SHALL be taken as the transaction amount, and the tokens between the date and that amount SHALL form the description. Lines whose description begins with one of the profile's skip prefixes SHALL be discarded.

Row interpretation SHALL operate on lists of text tokens, independent of any PDF library type, so it can be tested without constructing PDF objects.

#### Scenario: Valid transaction line
- **WHEN** a line begins with a date in a profile-accepted format and ends with an amount
- **THEN** a transaction is produced with that date, amount, and the intervening tokens as its description

#### Scenario: Line without a leading date
- **WHEN** a line does not begin with a token matching a profile-accepted date format
- **THEN** no transaction is produced

#### Scenario: Line without an amount
- **WHEN** a line begins with a valid date but contains no token matching a monetary amount
- **THEN** no transaction is produced

#### Scenario: Description containing a number
- **WHEN** a transaction line's description contains a numeric token before the final amount
- **THEN** the rightmost amount token is used as the amount
- **AND** the numeric token remains part of the description

#### Scenario: Summary line skipped
- **WHEN** a line's description begins with a skip prefix defined by the profile
- **THEN** no transaction is produced

#### Scenario: Testable without PDF objects
- **WHEN** row interpretation is tested
- **THEN** it accepts plain lists of text tokens as input

### Requirement: Amount Sign Normalization
The system SHALL normalize parsed amounts to the application's convention, in which expenses are negative and income is positive. The system SHALL recognize amounts formatted with currency symbols, thousands separators, leading minus signs, and surrounding parentheses. When a profile declares that its statements print expenses as positive values, the system SHALL invert the sign of parsed amounts.

#### Scenario: Parenthesized amount is an expense
- **WHEN** an amount is written in parentheses
- **THEN** it is parsed as a negative value

#### Scenario: Currency symbols and separators
- **WHEN** an amount includes a currency symbol, thousands separators, or surrounding whitespace
- **THEN** those characters are ignored and the numeric value is parsed

#### Scenario: Statement printing expenses as positives
- **WHEN** the selected profile declares that expenses are printed as positive values
- **THEN** parsed amounts are inverted so purchases are stored as negative

#### Scenario: Statement printing expenses as negatives
- **WHEN** the selected profile does not declare that expenses are printed as positive values
- **THEN** parsed amounts retain the sign shown on the statement

### Requirement: Year Inference for Year-Less Dates
When a profile's date formats omit a year, the system SHALL determine each transaction's year from the statement period printed on the statement. When a transaction's month is later than the statement's month, the system SHALL assign the preceding year.

#### Scenario: Year taken from statement period
- **WHEN** a statement prints transaction dates without a year and its statement period identifies a year
- **THEN** each parsed transaction is assigned that year

#### Scenario: Rollover across a year boundary
- **WHEN** a statement's period falls in January and a transaction line is dated in December
- **THEN** that transaction is assigned the preceding year

#### Scenario: Statement year not found
- **WHEN** a statement's dates omit a year and no statement period year can be located
- **THEN** parsing fails with an error identifying the cause

### Requirement: Import Preview and Confirmation
The system SHALL present the transactions parsed from a statement to the user for review before writing any of them to the database. The preview SHALL show each parsed transaction's date, description, and amount, together with the total count and the sum of amounts. The system SHALL write transactions only after the user confirms, and SHALL write none if the user cancels.

#### Scenario: User confirms an import
- **WHEN** the user reviews the parsed transactions and confirms the import
- **THEN** the transactions are submitted for categorization and duplicate detection
- **AND** the number imported is reported

#### Scenario: User cancels an import
- **WHEN** the user reviews the parsed transactions and cancels
- **THEN** no transaction is written to the database

#### Scenario: Statement yields no transactions
- **WHEN** parsing a statement produces no transactions
- **THEN** the user is told that none were found
- **AND** no transaction is written to the database

#### Scenario: Misparsed statement is visible
- **WHEN** an unrecognized bank's statement is parsed with the generic profile and yields incorrect rows
- **THEN** those rows and their sum are shown to the user before any write occurs
