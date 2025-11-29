# Project Context

## Purpose
Personal expense tracker desktop application that helps users manage their finances by importing Bank of America PDF statements, automatically categorizing transactions using fuzzy matching, and providing a graphical interface for manual expense management.

## Tech Stack
- **Language**: Python 3.11+
- **GUI Framework**: Tkinter with ttkbootstrap (darkly theme)
- **Database**: SQLite (two databases: transactions.db, merchant_categories.db)
- **PDF Parsing**: pdfplumber
- **Fuzzy Matching**: rapidfuzz (90% threshold for merchant categorization)
- **Package Manager**: uv
- **Testing**: pytest
- **Linting**: ruff

## Project Conventions

### Code Style
- **Linter**: ruff for code quality and formatting
- **Type Hints**: Use Python type hints (e.g., `list[Transaction]`, `str | None`)
- **Naming Conventions**:
  - Snake case for functions, variables, and file names (`add_transaction`, `merchant_key`)
  - PascalCase for classes (`TransactionRepository`, `MainWindow`)
  - Private methods prefixed with underscore (`_build_toolbar`, `_init_schema`)
- **String Formatting**: Use f-strings for string interpolation
- **Imports**: Group stdlib, third-party, and local imports separately

### Architecture Patterns
- **Repository Pattern**: Data access layer separated from business logic
  - `TransactionRepository` handles all transaction database operations
  - `MerchantCategoryRepository` handles merchant-category mappings
- **Service Layer**: Business logic encapsulated in service classes
  - `MerchantCategoryService` handles merchant normalization and fuzzy matching
- **MVC-like GUI**: Clear separation between UI (dialogs/windows) and data (repositories)
- **Dataclasses**: Simple data models using `@dataclass` decorator
- **Modal Dialogs**: Single active dialog pattern with `_active_dialog` tracking

### Testing Strategy
- **Framework**: pytest with test files in `tests/` directory
- **Test Structure**: Mirror source structure (`tests/core/test_repository.py`)
- **Running Tests**: `pytest` or `uv run pytest tests/ -v`
- **CI/CD**: GitHub Actions with matrix testing on Windows and macOS
- **Coverage**: Unit tests for repository methods, models, and core business logic

### Git Workflow
- **Main Branch**: `main`
- **Pull Requests**: Required for all changes
- **CI Checks**: Linting (ruff) and tests (pytest) must pass on PRs
- **Commit Style**: Descriptive messages with PR numbers (e.g., "Add Auto Categorize Feature After Merchant-Category is updated (#8)")
- **Paths Monitored**: `/expense_tracker/**`, `tests/**`, `.github/workflows/ci.yml`, `pyproject.toml`

## Domain Context

### Transaction Management
- **Transaction Model**: ID, date, amount (negative for expenses, positive for income), category, description
- **Default Category**: "Uncategorized" for new transactions
- **Date Format**: ISO format (YYYY-MM-DD) in database
- **Pagination**: 100 transactions per page, ordered by date DESC

### Merchant Categorization
- **Normalization**: Merchant names are normalized before lookup
  - Convert to uppercase
  - Remove digits, special characters, and common words (PENDING, MOBILE, etc.)
  - Strip state abbreviations
  - Normalized form is the key in merchant_categories table
- **Matching Strategy**: Exact match first, then fuzzy matching with rapidfuzz (90% threshold)
- **Auto-Categorization**: When merchant-category mapping is updated, all uncategorized transactions are automatically re-evaluated

### PDF Statement Import
- **Supported Format**: Bank of America PDF statements
- **Parsing Logic**: Custom parsing that groups words by y-position to rebuild table rows
- **Validation**: Rows validated by checking for date pattern at start and amount at end
- **Does NOT** rely on pdfplumber's table detection

## Important Constraints
- **Python Version**: Requires Python 3.11 or higher
- **GUI Framework**: Must use Tkinter (cross-platform compatibility)
- **Database**: SQLite only (no external database server)
- **PDF Format**: Currently only supports Bank of America statement format
- **Single User**: Desktop application designed for single-user local use
- **Thread Safety**: SQLite connections use `check_same_thread=False` for GUI compatibility

## External Dependencies
- **pdfplumber**: PDF text extraction and parsing
- **rapidfuzz**: Fuzzy string matching for merchant categorization
- **ttkbootstrap**: Modern themed Tkinter widgets (graceful fallback to standard ttk)
- **setuptools**: Build system
- **pytest**: Testing framework
- **ruff**: Linting and code quality

## File Structure
```
expense_tracker/
├── core/
│   ├── models.py           # Transaction and MerchantCategory dataclasses
│   └── repositories.py     # Database access layer
├── services/
│   └── merchant.py         # Merchant categorization business logic
├── utils/
│   ├── extract.py          # PDF statement parsing
│   └── merchant_normalizer.py  # Merchant name normalization
├── gui/
│   ├── main_window.py      # Main application window
│   └── dialogs/            # Modal dialogs (add, edit, upload, etc.)
└── app.py                  # Entry point
```
