import logging
import sqlite3

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

    def _init_schema(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL DEFAULT 'Uncategorized',
            description TEXT
        );
        """)

    def add_transaction(self, date: str, amount: float, category: str, description: str) -> int:
        self.conn.execute("""
        INSERT INTO transactions (date, amount, category, description)
        VALUES (?, ?, ?, ?)
        """, (date, amount, category, description))
        self.conn.commit()
        return self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    def get_transaction(self, transaction_id: int):
        row = self.conn.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        return row.fetchone()

    def get_all_transactions(self, limit: int = 100):
        rows = self.conn.execute("SELECT * FROM transactions ORDER BY date DESC LIMIT ?", (limit,))
        return rows.fetchall()

    def daily_summary(self, date: str):
        rows = self.conn.execute("""
        SELECT category, SUM(amount) as total
        FROM transactions
        WHERE date = ?
        GROUP BY category
        """, (date,))
        return rows.fetchall()

    def delete_transaction(self, transaction_id: int):
        self.conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self.conn.commit()
