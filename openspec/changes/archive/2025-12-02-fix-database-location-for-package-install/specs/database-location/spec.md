# Database Location Specification

## ADDED Requirements

### Requirement: Platform-Specific Data Directory Resolution
The application SHALL resolve database storage location using platform-appropriate user data directories, ensuring the application works correctly regardless of installation method (source code, pip install, uv tool install).

#### Scenario: macOS user data directory
- **WHEN** the application runs on macOS
- **THEN** database files SHALL be stored in `~/Library/Application Support/spendwise-tracker/`

#### Scenario: Linux/Unix user data directory
- **WHEN** the application runs on Linux or Unix systems
- **THEN** database files SHALL be stored in `~/.local/share/spendwise-tracker/`

#### Scenario: Windows user data directory
- **WHEN** the application runs on Windows
- **THEN** database files SHALL be stored in `%LOCALAPPDATA%\spendwise-tracker\`

### Requirement: Automatic Data Directory Creation
The application SHALL automatically create the data directory and any parent directories if they do not exist when initializing database connections.

#### Scenario: First-time application launch
- **WHEN** the application launches for the first time
- **THEN** the data directory SHALL be created automatically
- **AND** both database files (transactions.db and merchant_categories.db) SHALL be initialized in the data directory

#### Scenario: Missing data directory
- **WHEN** the data directory is deleted after initial setup
- **THEN** the application SHALL recreate the directory on next launch
- **AND** database files SHALL be re-initialized with empty schemas

### Requirement: Database File Path Resolution
The application SHALL construct absolute paths to database files by combining the platform-specific data directory with the database filename.

#### Scenario: Transaction database path resolution
- **WHEN** the TransactionRepository is initialized
- **THEN** the database path SHALL be `<platform_data_dir>/transactions.db`

#### Scenario: Merchant categories database path resolution
- **WHEN** the MerchantCategoryRepository is initialized
- **THEN** the database path SHALL be `<platform_data_dir>/merchant_categories.db`

### Requirement: Backward Compatibility Migration
The application SHALL detect and migrate existing databases from the legacy source code directory (`expense_tracker/data/`) to the new platform-specific location on first launch after upgrade.

#### Scenario: Existing user with legacy database location
- **WHEN** the application launches with existing databases in `expense_tracker/data/`
- **THEN** the application SHALL copy both database files to the new platform-specific location
- **AND** the application SHALL continue using the new location for all subsequent operations
- **AND** the legacy files SHALL remain untouched (manual cleanup by user)

#### Scenario: Fresh installation with no legacy databases
- **WHEN** the application launches with no existing databases
- **THEN** the application SHALL create new empty databases in the platform-specific location
- **AND** no migration SHALL occur

#### Scenario: Multiple application instances
- **WHEN** databases exist in both legacy and new locations
- **THEN** the application SHALL prefer the new platform-specific location
- **AND** ignore the legacy location databases
