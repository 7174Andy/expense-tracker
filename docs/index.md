# Spendwise Expense Tracker

**Spendwise** is an open-source desktop application to track expenses by importing Bank of America PDF statements. It features intelligent merchant categorization, monthly spending statistics, and interactive heatmap visualizations to help you understand your spending patterns.

## Features

- **PDF Statement Import** - Import Bank of America PDF statements with automatic transaction extraction
- **Smart Categorization** - Intelligent merchant recognition with fuzzy matching (90% accuracy threshold)
- **Transaction Management** - Add, edit, delete, and search transactions with pagination
- **Monthly Statistics** - View net income and top spending categories by month
- **Spending Heatmap** - Interactive calendar showing daily spending intensity with color-coded visualization
- **Auto-Recategorization** - Update a merchant's category once, and similar transactions are automatically recategorized

## Installation

Spendwise is installed as a Python package. It is strongly recommended to install the package via [uv](https://docs.astral.sh/uv/).

Latest versions of Spendwise can be seen in the [Release](https://github.com/7174Andy/expense-tracker/releases) page.

### Requirements

- Python 3.11 or higher
- macOS, Linux, or Windows

### Quick Install

First, install `uv` if you haven't already:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then, install Spendwise Tracker:

```bash
uv tool install spendwise-tracker
```

Run the GUI after installation:

```bash
expense-tracker
```

## Quick Start

### Importing Transactions

1. Click the **Import Statement** button in the Transactions tab
2. Select a Bank of America PDF statement
3. Transactions are automatically parsed and categorized

### Managing Transactions

- **View**: Browse transactions with pagination (100 per page)
- **Search**: Use the search bar to filter transactions by keyword
- **Add**: Click "Add Transaction" to manually enter a transaction
- **Edit**: Double-click a transaction or select and click "Edit Transaction"
- **Delete**: Select a transaction and click "Delete Transaction"

### Viewing Statistics

1. Navigate to the **Statistics** tab
2. Use the `<` and `>` buttons to browse months with transaction data
3. View monthly net income and top spending category

### Analyzing Spending Patterns

1. Navigate to the **Heatmap** tab
2. View daily spending amounts on an interactive calendar
3. Darker colors indicate higher spending
4. Click on any day to filter transactions by that date

## License

Spendwise is released under MIT License.
