# Implementation Tasks

## 1. Create Database Path Utilities
- [x] 1.1 Create new module `expense_tracker/utils/path.py`
- [x] 1.2 Implement `get_data_directory()` function using `pathlib.Path` and platform detection
- [x] 1.3 Add platform-specific path logic for macOS, Linux, and Windows
- [x] 1.4 Implement directory creation with `mkdir(parents=True, exist_ok=True)`
- [x] 1.5 Implement `get_database_path(filename: str) -> Path` helper function
- [x] 1.6 Write unit tests for path resolution on all platforms

## 2. Implement Database Migration Logic
- [x] 2.1 Create `expense_tracker/utils/migration.py` module
- [x] 2.2 Implement `migrate_legacy_databases()` function to detect and copy legacy databases
- [x] 2.3 Add logic to check if legacy path exists and new path doesn't have databases
- [x] 2.4 Implement safe file copying with error handling
- [x] 2.5 Write tests for migration scenarios (legacy exists, fresh install, both exist)

## 3. Update Application Entry Point
- [x] 3.1 Modify `expense_tracker/app.py` to use `get_database_path()` for both repositories
- [x] 3.2 Call `migrate_legacy_databases()` before initializing repositories
- [x] 3.3 Remove hardcoded `"expense_tracker/data/transactions.db"` paths
- [x] 3.4 Test application startup with and without legacy databases

## 4. Update Tests and Documentation
- [x] 4.1 Update repository tests to use temporary database paths (existing tests still pass)
- [x] 4.2 Add integration tests for database initialization with new paths
- [x] 4.3 Update CLAUDE.md to document new database location behavior
- [x] 4.4 Update openspec/project.md with new database location conventions

## 5. Test Package Installation
- [x] 5.1 Build package with `uv build`
- [x] 5.2 Test installation with `uv tool install .`
- [x] 5.3 Verify application launches and creates databases in correct location
- [x] 5.4 Test migration from legacy location to new location
- [x] 5.5 Test on multiple platforms via CI (macOS, Linux, Windows)

## 6. Cleanup
- [x] 6.1 Run linter (`ruff check .`) and fix any issues
- [x] 6.2 Run full test suite (`pytest`) and ensure all tests pass (58 tests passed)
- [x] 6.3 Update change status in tasks.md to mark all items complete
