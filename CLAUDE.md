<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based desktop expense tracker application with a Tkinter GUI. It allows users to import Bank of America PDF statements, automatically categorize transactions using fuzzy matching, and manually manage expenses through a graphical interface.

## Development Commands

### Environment Setup
```bash
# Install dependencies (including dev dependencies)
uv sync --extra dev

# Activate virtual environment
source .venv/bin/activate
```

### Running the Application
```bash
# Run the expense tracker GUI
expense-tracker

# Or via Python module
python -m expense_tracker.app
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/core/test_repository.py

# Run with verbose output
pytest -v
```

### Linting
```bash
# Run ruff linter
ruff check .

# Auto-fix linting issues
ruff check --fix .
```

## Architecture

### Core Data Flow

The application follows a repository pattern with clear separation of concerns:

1. **Models** ([expense_tracker/core/models.py](expense_tracker/core/models.py)) - Simple dataclasses for `Transaction` and `MerchantCategory`
2. **Repositories** ([expense_tracker/core/repositories.py](expense_tracker/core/repositories.py)) - SQLite data access for transactions and merchant categories
3. **Services** ([expense_tracker/services/merchant.py](expense_tracker/services/merchant.py)) - Business logic for merchant categorization
4. **GUI** ([expense_tracker/gui/](expense_tracker/gui/)) - Tkinter-based user interface

### Key Components

**Transaction Management:**
- `TransactionRepository` handles CRUD operations for expenses
- Uses SQLite with two separate databases:
  - `transactions.db` - stores all expense/income transactions
  - `merchant_categories.db` - stores merchant-to-category mappings

**Merchant Categorization System:**
- `normalize_merchant()` ([expense_tracker/utils/merchant_normalizer.py](expense_tracker/utils/merchant_normalizer.py)) standardizes merchant names by:
  - Converting to uppercase
  - Removing digits, special chars, and common words (PENDING, MOBILE, etc.)
  - Stripping state abbreviations
- `MerchantCategoryService` uses exact matching first, then falls back to fuzzy matching (rapidfuzz with 90% threshold)
- Auto-categorization: When a merchant-category mapping is updated, all uncategorized transactions are automatically re-evaluated

**PDF Statement Import:**
- `parse_bofa_statement_pdf()` ([expense_tracker/utils/extract.py](expense_tracker/utils/extract.py)) extracts transactions from Bank of America PDFs
- Custom parsing logic groups words by y-position to rebuild table rows (doesn't rely on pdfplumber's table detection)
- Validates rows by checking for date pattern at start and amount at end

### GUI Architecture

The application uses a tabbed interface to organize different views:

- `MainWindow` ([expense_tracker/gui/main_window.py](expense_tracker/gui/main_window.py)) - Tab container using ttk.Notebook
  - Manages modal dialogs via `_open_dialog()` method
  - Currently contains one tab: "Transactions"
- Tabs in `gui/tabs/`:
  - `TransactionsTab` - Transaction table with toolbar, search, and pagination
- Dialogs in `gui/dialogs/`:
  - `AddExpenseDialog` - Manual transaction entry
  - `EditExpenseDialog` - Edit existing transaction and optionally update merchant-category mapping
  - `UploadDialog` - Import PDF statements
- Uses ttkbootstrap for "darkly" theme if available, falls back to standard ttk

### Database Schema

**transactions table:**
- `id` (INTEGER PRIMARY KEY)
- `date` (TEXT, ISO format)
- `amount` (REAL, negative for expenses, positive for income)
- `category` (TEXT, defaults to "Uncategorized")
- `description` (TEXT)

**merchant_categories table:**
- `merchant_key` (TEXT PRIMARY KEY) - normalized merchant name
- `category` (TEXT)

## Important Patterns

### Merchant Normalization
Always use `normalize_merchant()` before looking up or storing merchant categories. The normalized form is the key used in the merchant_categories database.

### Auto-Categorization Trigger
When editing a transaction in `EditExpenseDialog`, if the user updates the category, the system:
1. Updates the merchant-category mapping in the database
2. Calls `update_uncategorized_transactions()` to re-categorize all uncategorized transactions

### Pagination
The Transactions tab uses offset-based pagination with a page size of 100 transactions. Transactions are ordered by date DESC.

### Dialog Management
`MainWindow` uses `_active_dialog` to ensure only one dialog is open at a time. Dialogs are modal and refresh the active tab on close.

### Tabbed Interface
The main window uses `ttk.Notebook` to organize views into tabs. Each tab is a `tk.Frame` subclass that encapsulates its own functionality. The `TransactionsTab` contains all transaction management features (search, CRUD operations, pagination).
