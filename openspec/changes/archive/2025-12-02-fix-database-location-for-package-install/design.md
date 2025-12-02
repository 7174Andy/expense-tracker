# Design Document: Database Location for Package Installation

## Context
The current implementation uses hardcoded relative paths (`expense_tracker/data/transactions.db`) that only work when the application is run from the source directory. When users install the package via `uv tool install spendwise-tracker`, the working directory is different from the package location, causing the application to fail when trying to create or access database files.

This is a common issue with Python desktop applications that need persistent data storage. The solution must:
- Follow platform conventions for user data storage
- Work with multiple installation methods (source, pip, uv tool install)
- Provide backward compatibility for existing users
- Remain simple and maintainable

## Goals / Non-Goals

### Goals
- Store databases in platform-appropriate user data directories
- Automatically create data directories on first launch
- Migrate existing databases from legacy location seamlessly
- Work correctly with `uv tool install`, `pip install`, and source execution
- Maintain zero-configuration setup for users

### Non-Goals
- Supporting custom database locations via configuration files
- Environment variable overrides for database paths
- Multi-user database sharing (remains single-user desktop app)
- Backing up or removing legacy database files automatically
- Supporting portable/USB installation modes

## Decisions

### Decision 1: Use Standard Platform Directories
**Choice**: Use platform-specific standard user data directories via Python's `pathlib` and platform detection.

**Alternatives considered**:
1. **Current working directory**: Doesn't work with tool installations
2. **Package installation directory**: Not writable in many installation scenarios
3. **Environment variable**: Adds configuration complexity, not user-friendly
4. **XDG/platformdirs library**: Adds external dependency for simple functionality

**Rationale**: Standard directories are expected by users on each platform, don't require additional dependencies, and work with all installation methods. We can implement this with stdlib `pathlib` and `sys.platform`.

**Implementation**:
```python
# expense_tracker/utils/paths.py
from pathlib import Path
import sys

def get_data_directory() -> Path:
    if sys.platform == "darwin":  # macOS
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":  # Windows
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:  # Linux and other Unix
        base = Path.home() / ".local" / "share"

    data_dir = base / "spendwise-tracker"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def get_database_path(filename: str) -> Path:
    return get_data_directory() / filename
```

### Decision 2: Automatic Migration on First Launch
**Choice**: Detect legacy databases and copy them to new location on first launch after upgrade.

**Alternatives considered**:
1. **No migration**: Existing users lose data
2. **Manual migration instructions**: Poor user experience
3. **In-place database location**: Doesn't solve the tool installation problem
4. **Move instead of copy**: Risk of data loss if migration fails

**Rationale**: Seamless migration provides the best user experience. Copying (instead of moving) legacy files is safer and allows users to roll back if needed. Migration logic runs once on first launch and has minimal performance impact.

**Implementation**:
```python
# expense_tracker/utils/migration.py
from pathlib import Path
import shutil

def migrate_legacy_databases() -> None:
    legacy_dir = Path("expense_tracker/data")
    if not legacy_dir.exists():
        return

    new_dir = get_data_directory()
    for db_file in ["transactions.db", "merchant_categories.db"]:
        legacy_path = legacy_dir / db_file
        new_path = new_dir / db_file

        if legacy_path.exists() and not new_path.exists():
            shutil.copy2(legacy_path, new_path)
```

### Decision 3: Directory Creation on Initialization
**Choice**: Create data directory with `mkdir(parents=True, exist_ok=True)` when getting the data directory path.

**Alternatives considered**:
1. **Manual directory creation**: Adds user friction
2. **Check and fail if missing**: Poor user experience
3. **Lazy creation on first write**: More complex, fails on read operations

**Rationale**: Automatic creation is the expected behavior for desktop applications. The `exist_ok=True` flag makes it safe to call repeatedly, and `parents=True` ensures parent directories are created if needed.

### Decision 4: No External Dependencies for Path Resolution
**Choice**: Use stdlib `pathlib`, `sys.platform`, and `os.environ` for path resolution.

**Alternatives considered**:
1. **platformdirs library**: Popular but adds external dependency
2. **appdirs library**: Older, less maintained
3. **XDG library**: Linux-only

**Rationale**: The path resolution logic is simple enough to implement with stdlib. Avoiding an external dependency reduces package size, installation complexity, and potential version conflicts. The implementation is ~20 lines of code.

## Risks / Trade-offs

### Risk 1: Platform Detection Edge Cases
**Risk**: Uncommon platforms (FreeBSD, exotic Unix variants) might not be handled correctly.

**Mitigation**: Default to Unix-style `~/.local/share` for unknown platforms. This is a sensible fallback that works on most Unix-like systems.

### Risk 2: Migration Failure
**Risk**: Copying legacy databases might fail due to permissions or disk space.

**Mitigation**:
- Wrap migration in try-except and log errors
- Allow application to continue with fresh databases if migration fails
- Don't delete legacy files so users can manually recover

### Risk 3: Hardcoded Paths in Tests
**Risk**: Existing tests might break due to changed database paths.

**Mitigation**: Update tests to use temporary directories or mock the path resolution functions. Use pytest fixtures for database setup.

### Trade-off: No Custom Database Location
**Trade-off**: Users cannot configure a custom database location via config file or environment variable.

**Rationale**: Adds complexity for minimal benefit in a single-user desktop application. Users who need this can modify the source code. Can be added later if there's demand.

## Migration Plan

### Phase 1: Implementation
1. Create path utilities module (`expense_tracker/utils/paths.py`)
2. Create migration module (`expense_tracker/utils/migration.py`)
3. Update `expense_tracker/app.py` to use new path resolution
4. Update tests to use new path resolution

### Phase 2: Testing
1. Unit tests for path resolution on all platforms
2. Integration tests for migration scenarios
3. Manual testing with `uv tool install`
4. Test on macOS, Linux, and Windows if possible

### Phase 3: Deployment
1. Update documentation (CLAUDE.md, README, project.md)
2. Create release notes mentioning database location change
3. Deploy via PyPI/GitHub release

### Rollback Plan
If critical issues are discovered:
1. Users can downgrade to previous version
2. Legacy databases remain in `expense_tracker/data/`
3. No data loss occurs because migration copies (doesn't move) files

## Open Questions

### Q1: Should we add logging for migration events?
**Status**: Yes - add INFO level logging when migration occurs, showing source and destination paths. Helps with debugging user issues.

### Q2: Should we provide a CLI command to show database location?
**Status**: Not in this change - can be added later as a separate feature if needed. Users can find databases in platform-standard locations.

### Q3: Should we handle the case where both legacy and new databases exist with different data?
**Status**: No - the spec says to prefer new location and ignore legacy. This scenario should be rare and users can manually merge if needed.
