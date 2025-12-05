import logging
import sqlite3
from dataclasses import replace
from datetime import date

from expense_tracker.core.models import Transaction

logger = logging.getLogger(__name__)


class TransactionRepository:
    """
    A repository for managing transaction data.
    """

    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        logger.info("Initialized database schema")

    def _init_schema(self) -> None:
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL DEFAULT 'Uncategorized',
            description TEXT
        );
        """)

    def _row_to_transaction(self, row: sqlite3.Row | None) -> Transaction | None:
        if row is None:
            return None
        return Transaction(
            id=row["id"],
            date=date.fromisoformat(row["date"]),
            amount=row["amount"],
            category=row["category"],
            description=row["description"] or "",
        )

    def add_transaction(self, transaction: Transaction) -> Transaction:
        cursor = self.conn.execute(
            """
            INSERT INTO transactions (date, amount, category, description)
            VALUES (?, ?, ?, ?)
            """,
            (
                transaction.date.isoformat(),
                transaction.amount,
                transaction.category,
                transaction.description,
            ),
        )
        self.conn.commit()
        return replace(transaction, id=cursor.lastrowid)

    def get_transaction(self, transaction_id: int) -> Transaction | None:
        row = self.conn.execute(
            "SELECT * FROM transactions WHERE id = ?", (transaction_id,)
        )
        return self._row_to_transaction(row.fetchone())

    def get_all_transactions(
        self, limit: int = 100, offset: int = 0
    ) -> list[Transaction]:
        rows = self.conn.execute(
            "SELECT * FROM transactions ORDER BY date DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        transactions: list[Transaction] = []
        for row in rows.fetchall():
            transaction = self._row_to_transaction(row)
            if transaction:
                transactions.append(transaction)
        return transactions

    def get_all_transactions_by_category(self, category: str) -> list[Transaction]:
        rows = self.conn.execute(
            "SELECT * FROM transactions WHERE category = ? ORDER BY date DESC",
            (category,),
        )
        transactions: list[Transaction] = []
        for row in rows.fetchall():
            transaction = self._row_to_transaction(row)
            if transaction:
                transactions.append(transaction)
        return transactions

    def count_all_transactions(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) FROM transactions")
        return row.fetchone()[0]

    def search_by_keyword(
        self, keyword: str | None, limit: int = 100, offset: int = 0
    ) -> list[Transaction]:
        """
        Search transactions by keyword in description field (case-insensitive).
        Returns all transactions if keyword is None or empty.
        """
        if not keyword:
            return self.get_all_transactions(limit, offset)

        rows = self.conn.execute(
            "SELECT * FROM transactions WHERE description LIKE ? COLLATE NOCASE ORDER BY date DESC LIMIT ? OFFSET ?",
            (f"%{keyword}%", limit, offset),
        )
        transactions: list[Transaction] = []
        for row in rows.fetchall():
            transaction = self._row_to_transaction(row)
            if transaction:
                transactions.append(transaction)
        return transactions

    def count_search_results(self, keyword: str | None) -> int:
        """
        Count transactions matching the keyword.
        Returns total count if keyword is None or empty.
        """
        if not keyword:
            return self.count_all_transactions()

        row = self.conn.execute(
            "SELECT COUNT(*) FROM transactions WHERE description LIKE ? COLLATE NOCASE",
            (f"%{keyword}%",),
        )
        return row.fetchone()[0]

    def daily_summary(self, date: str):
        rows = self.conn.execute(
            """
        SELECT category, SUM(amount) as total
        FROM transactions
        WHERE date = ?
        GROUP BY category
        """,
            (date,),
        )
        return rows.fetchall()

    def delete_transaction(self, transaction_id: int) -> None:
        self.conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self.conn.commit()

    def delete_multiple_transactions(self, transaction_ids: list[int]) -> int:
        if not transaction_ids:
            return 0

        placeholders = ", ".join("?" for _ in transaction_ids)
        query = f"DELETE FROM transactions WHERE id IN ({placeholders})"
        cursor = self.conn.execute(query, transaction_ids)
        self.conn.commit()
        return cursor.rowcount

    def update_transaction(self, transaction_id: int, data: dict) -> None:
        """
        Updates a transaction in the database.
        """
        updates = ", ".join(f"{key} = ?" for key in data.keys())
        values: list[object] = []
        for key, value in data.items():
            if key == "date" and isinstance(value, date):
                values.append(value.isoformat())
            else:
                values.append(value)
        values.append(transaction_id)
        query = f"UPDATE transactions SET {updates} WHERE id = ?"
        self.conn.execute(query, values)
        self.conn.commit()

    def get_daily_spending_range(self, start_date: date, end_date: date) -> dict[int, float]:
        """
        Returns a dictionary mapping day-of-month (1-31) to total spending.
        Only includes expenses (negative amounts).
        """
        rows = self.conn.execute(
            """
            SELECT CAST(strftime('%d', date) AS INTEGER) as day,
                   SUM(ABS(amount)) as total
            FROM transactions
            WHERE date >= ? AND date < ?
              AND amount < 0
            GROUP BY day
            """,
            (start_date.isoformat(), end_date.isoformat()),
        )

        result: dict[int, float] = {}
        for row in rows.fetchall():
            result[row["day"]] = row["total"]
        return result
    
    def get_monthly_cashflow_trend(self, num_months: int) -> list[tuple[int, int, float]]:
        """
        Returns a list of (year, month, net_amount) tuples for the past num_months.
        Net amount is total income minus total expenses for each month.
        Ordered by year and month ascending.
        """
        rows = self.conn.execute(
            """
            SELECT 
                CAST(strftime('%Y', date) AS INTEGER) as year,
                CAST(strftime('%m', date) AS INTEGER) as month,
                SUM(amount) as net_amount
            FROM transactions
            GROUP BY year, month
            ORDER BY year DESC, month DESC
            LIMIT ?
            """,
            (num_months,),
        )

        result: list[tuple[int, int, float]] = []
        for row in reversed(rows.fetchall()):
            result.append((row["year"], row["month"], row["net_amount"]))
        return result

    def get_monthly_net_income(self, start_date: date, end_date: date) -> float:
        """
        Returns the net income (total income minus total expenses) for a specific month.
        Positive amount means more income than expenses, negative means more expenses than income.
        """
        # Create date range for the month
        row = self.conn.execute(
            """
            SELECT SUM(amount) as net_income
            FROM transactions
            WHERE date >= ? AND date < ?
            """,
            (start_date.isoformat(), end_date.isoformat()),
        )
        result = row.fetchone()
        return result["net_income"] if result["net_income"] is not None else 0.0

    def get_top_spending_category(self, start_date: date, end_date: date) -> tuple[str, float] | None:
        """
        Returns the category with the highest spending (sum of negative amounts) for a specific month.
        Returns tuple of (category_name, total_spending) or None if no expenses exist.
        """
        rows = self.conn.execute(
            """
            SELECT category, SUM(ABS(amount)) as total
            FROM transactions
            WHERE date >= ? AND date < ?
              AND amount < 0
            GROUP BY category
            ORDER BY total DESC
            LIMIT 1
            """,
            (start_date.isoformat(), end_date.isoformat()),
        )
        result = rows.fetchone()
        if result is None:
            return None
        return (result["category"], result["total"])

    def get_transactions_for_date(self, target_date: date) -> list[Transaction]:
        """
        Query transactions matching exact date.
        Order by amount DESC (largest expenses first).
        """
        rows = self.conn.execute(
            "SELECT * FROM transactions WHERE date = ? ORDER BY amount ASC",
            (target_date.isoformat(),),
        )
        transactions: list[Transaction] = []
        for row in rows.fetchall():
            transaction = self._row_to_transaction(row)
            if transaction:
                transactions.append(transaction)
        return transactions
    
    def get_latest_month_with_data(self) -> tuple[int, int]:
        """
        Get the most recent month that has transaction data.
        Falls back to current month if no transactions exist.
        """
        # Query for all months with transactions (ordered by most recent first)
        rows = self.conn.execute(
            """
            SELECT DISTINCT
                CAST(strftime('%Y', date) AS INTEGER) as year,
                CAST(strftime('%m', date) AS INTEGER) as month
            FROM transactions
            ORDER BY year DESC, month DESC
            LIMIT 1
            """
        )
        result = rows.fetchone()

        if result is None:
            # No transactions exist, default to current month
            today = date.today()
            return (today.year, today.month)

        return (result["year"], result["month"])
    

    def get_all_months_with_data(self) -> list[tuple[int, int]]:
        """
        Returns a list of (year, month) tuples for all months that have transaction data.
        Ordered by year and month descending (most recent first).
        """
        rows = self.conn.execute(
            """
            SELECT DISTINCT
                CAST(strftime('%Y', date) AS INTEGER) as year,
                CAST(strftime('%m', date) AS INTEGER) as month
            FROM transactions
            ORDER BY year DESC, month DESC
            """
        )
        return {(row["year"], row["month"]) for row in rows.fetchall()}

    def get_months_with_expenses(self) -> list[tuple[int, int]]:
        """
        Returns a list of (year, month) tuples for all months that have expenses.
        Only includes months with negative amounts (expenses).
        Ordered by year and month descending (most recent first).
        """
        rows = self.conn.execute(
            """
            SELECT DISTINCT
                CAST(strftime('%Y', date) AS INTEGER) as year,
                CAST(strftime('%m', date) AS INTEGER) as month
            FROM transactions
            WHERE amount < 0
            ORDER BY year DESC, month DESC
            """
        )
        result: list[tuple[int, int]] = []
        for row in rows.fetchall():
            result.append((row["year"], row["month"]))
        return result


