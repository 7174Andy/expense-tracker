# Getting Started

This guide walks you through launching Spendwise for the first time, importing your first bank statement, and navigating the interface.

## Launching the Application

After [installing](installation.md) Spendwise, start it from your terminal:

```bash
expense-tracker
```

The main window opens with three tabs: **Transactions**, **Statistics**, and **Heatmap**.

## Importing a Bank Statement

The fastest way to populate Spendwise is by importing a Bank of America PDF statement.

### 1. Download Your Statement

Log in to your Bank of America account and download a monthly statement as a PDF.

!!! note
    Only Bank of America PDF statements are supported at this time. Other bank formats will not be parsed correctly.

### 2. Import the PDF

1. In the **Transactions** tab, click **Import Statement** (top-right of the toolbar)
2. Click **Browse** and select your downloaded PDF
3. Click **Upload**

Spendwise extracts each transaction from the PDF and automatically categorizes them using its [merchant categorization system](categorization.md). A success message confirms the import.

### 3. Review Your Transactions

After importing, your transactions appear in the table with the following columns:

| Column      | Description                                      |
|-------------|--------------------------------------------------|
| Date        | Transaction date                                 |
| Amount      | Negative for expenses, positive for income       |
| Category    | Auto-assigned category (or "Uncategorized")      |
| Description | Original merchant description from the statement |

## Adding a Transaction Manually

You can also add transactions by hand:

1. Click **Add Transaction** in the toolbar
2. Fill in the amount, category, and description (the date defaults to today)
3. Click **Save**

## Editing a Transaction

To correct a transaction's details or update its category:

1. **Double-click** a transaction in the table (or select it and click **Edit Transaction**)
2. Modify the amount, category, or description
3. Click **Save**

!!! tip
    When you change a transaction's category, Spendwise remembers the mapping and automatically applies it to other uncategorized transactions from the same merchant. See [Categorization](categorization.md) for details.

## Deleting Transactions

1. Select one or more transactions in the table
2. Click **Delete Transaction**
3. Confirm the deletion in the dialog

## Searching Transactions

Use the search bar in the toolbar to filter transactions by keyword:

1. Type a keyword (e.g., a merchant name or category) into the search field
2. Press ++enter++ or click **Search**
3. Click **Clear Search** to remove the filter

## Browsing Pages

Transactions are displayed 100 per page, sorted by date (newest first). Use the **Previous** and **Next** buttons at the bottom to navigate between pages.

## Viewing Statistics

Switch to the **Statistics** tab to see monthly summaries:

- **Net income** for the selected month
- **Top spending categories** ranked by total amount
- Use the **<** and **>** buttons to browse between months

## Viewing the Spending Heatmap

Switch to the **Heatmap** tab for a calendar visualization of your daily spending:

- Darker colors indicate higher spending days
- Click on any day to jump to the **Transactions** tab filtered to that date

## Next Steps

- Learn how [Categorization](categorization.md) works to keep your transactions organized automatically
