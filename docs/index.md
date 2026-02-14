# Spendwise Expense Tracker

**Take control of your spending.** Spendwise is an open-source desktop app that imports your Bank of America PDF statements, automatically categorizes transactions, and visualizes your spending patterns -- all locally on your machine.

[Get Started](getting-started.md){ .md-button .md-button--primary }
[Installation](installation.md){ .md-button }

---

## Features

<div class="grid cards" markdown>

-   :material-file-pdf-box:{ .lg .middle } **PDF Statement Import**

    ---

    Import Bank of America PDF statements and automatically extract every transaction -- no manual data entry needed.

-   :material-tag-text:{ .lg .middle } **Smart Categorization**

    ---

    Intelligent merchant recognition using fuzzy matching with a 90% accuracy threshold. Categorize once, and Spendwise remembers.

    [:octicons-arrow-right-24: How it works](categorization.md)

-   :material-table-edit:{ .lg .middle } **Transaction Management**

    ---

    Add, edit, delete, and search transactions with a clean tabular interface and pagination.

-   :material-chart-bar:{ .lg .middle } **Monthly Statistics**

    ---

    View net income and top spending categories by month to understand where your money goes.

-   :material-calendar-month:{ .lg .middle } **Spending Heatmap**

    ---

    Interactive calendar visualization with color-coded daily spending. Click any day to drill into its transactions.

-   :material-sync:{ .lg .middle } **Auto-Recategorization**

    ---

    Update a merchant's category once, and all matching uncategorized transactions are instantly recategorized.

</div>

## Quick Install

Install with [uv](https://docs.astral.sh/uv/) in two commands:

=== "macOS / Linux"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    uv tool install spendwise-tracker
    ```

=== "Windows"

    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    uv tool install spendwise-tracker
    ```

Then launch the app:

```bash
expense-tracker
```

!!! tip "Need more details?"
    See the full [Installation Guide](installation.md) for version pinning, troubleshooting, and uninstall instructions.

## Quick Start

<div class="grid cards" markdown>

-   :material-numeric-1-circle:{ .lg .middle } **Import a statement**

    ---

    Click **Import Statement** in the toolbar, select a Bank of America PDF, and your transactions appear instantly.

-   :material-numeric-2-circle:{ .lg .middle } **Review & categorize**

    ---

    Double-click any transaction to edit its category. Spendwise learns and applies the mapping to future imports.

-   :material-numeric-3-circle:{ .lg .middle } **Search & browse**

    ---

    Use the search bar to filter by keyword. Navigate pages with **Previous** / **Next** (100 transactions per page).

-   :material-numeric-4-circle:{ .lg .middle } **Explore your data**

    ---

    Switch to the **Statistics** tab for monthly summaries or the **Heatmap** tab for a calendar view of daily spending.

</div>

## Requirements

| | Requirement |
|---|---|
| :material-language-python: | Python 3.11 or higher |
| :material-desktop-classic: | macOS, Linux, or Windows |

## License

Spendwise is released under the [MIT License](https://github.com/7174Andy/expense-tracker/blob/main/LICENSE).
