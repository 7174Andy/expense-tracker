# Change: Fix Database Location for Package Installation

## Why
When users install spendwise-tracker via `uv tool install spendwise-tracker`, the application fails to create or find database files because it uses hardcoded relative paths (`expense_tracker/data/transactions.db`) that assume execution from the source code directory. This breaks the application for users installing it as a tool package, as the working directory differs from the package installation location.

## What Changes
- Replace hardcoded relative database paths with platform-appropriate user data directory paths
- Use standard user data directory conventions:
  - **Linux/Unix**: `~/.local/share/spendwise-tracker/`
  - **macOS**: `~/Library/Application Support/spendwise-tracker/`
  - **Windows**: `%LOCALAPPDATA%\spendwise-tracker\`
- Automatically create the data directory if it doesn't exist
- Update database initialization to use the new path resolution logic
- Maintain backward compatibility by migrating existing databases from old location if found

## Impact
- **Affected specs**: database-location (new capability)
- **Affected code**:
  - [expense_tracker/app.py:15-17](expense_tracker/app.py#L15-L17) - Database path initialization
  - [expense_tracker/core/repositories.py:16](expense_tracker/core/repositories.py#L16) - Repository initialization
- **Breaking**: None - backward compatible migration for existing users
- **Benefits**: Application works correctly when installed via `uv tool install`
