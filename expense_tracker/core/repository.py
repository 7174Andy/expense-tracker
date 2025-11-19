import logging
import sqlite3
from dataclasses import replace
from datetime import date

from expense_tracker.core.model import Transaction

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
        row = self.conn.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        return self._row_to_transaction(row.fetchone())

    def get_all_transactions(self, limit: int = 100) -> list[Transaction]:
        rows = self.conn.execute("SELECT * FROM transactions ORDER BY date DESC LIMIT ?", (limit,))
        transactions: list[Transaction] = []
        for row in rows.fetchall():
            transaction = self._row_to_transaction(row)
            if transaction:
                transactions.append(transaction)
        return transactions

    def daily_summary(self, date: str):
        rows = self.conn.execute("""
        SELECT category, SUM(amount) as total
        FROM transactions
        WHERE date = ?
        GROUP BY category
        """, (date,))
        return rows.fetchall()

    def delete_transaction(self, transaction_id: int) -> None:
        self.conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self.conn.commit()
    
    def delete_multiple_transactions(self, transaction_ids: list[int]) -> int:
        if not transaction_ids:
            return 0
        
        placeholders = ', '.join('?' for _ in transaction_ids)
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

class MerchantCategoryRepository:
    """
    A repository for managing merchant categories.
    """
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        logger.info("Initialized merchant category database schema")

    def _init_schema(self) -> None:
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS merchant_categories (
                merchant_key TEXT PRIMARY KEY,
                category TEXT NOT NULL
            );
        """)

    def set_category(self, merchant_key: str, category: str) -> None:
        self.conn.execute("""
            INSERT INTO merchant_categories (merchant_key, category)
            VALUES (?, ?)
            ON CONFLICT(merchant_key) DO UPDATE SET category=excluded.category
        """, (merchant_key, category))
        self.conn.commit()

    def get_category(self, merchant_key: str) -> str | None:
        row = self.conn.execute("SELECT category FROM merchant_categories WHERE merchant_key = ?", (merchant_key,))
        result = row.fetchone()
        return result["category"] if result else None

    def get_all_merchants(self) -> list[str]:
        rows = self.conn.execute("SELECT merchant_key FROM merchant_categories")
        return [row["merchant_key"] for row in rows.fetchall()]