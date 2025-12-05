import logging
import sqlite3

from expense_tracker.core.models import MerchantCategory

logger = logging.getLogger(__name__)

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

    def _row_to_merchant_category(
        self, row: sqlite3.Row | None
    ) -> MerchantCategory | None:
        if row is None:
            return None
        return MerchantCategory(
            merchant_key=row["merchant_key"],
            category=row["category"],
        )

    def set_category(self, merchant_category: MerchantCategory) -> None:
        """Sets or updates the category for a given merchant key."""
        self.conn.execute(
            """
            INSERT INTO merchant_categories (merchant_key, category)
            VALUES (?, ?)
            ON CONFLICT(merchant_key) DO UPDATE SET category=excluded.category
        """,
            (merchant_category.merchant_key, merchant_category.category),
        )
        self.conn.commit()

    def get_category(self, merchant_key: str) -> MerchantCategory | None:
        """Retrieves the category for a given merchant key."""
        row = self.conn.execute(
            "SELECT * FROM merchant_categories WHERE merchant_key = ?", (merchant_key,)
        )
        return self._row_to_merchant_category(row.fetchone())

    def get_all_merchants(self) -> list[MerchantCategory]:
        """Retrieves all merchant categories."""
        rows = self.conn.execute("SELECT * FROM merchant_categories")
        merchants = []
        for row in rows.fetchall():
            merchant = self._row_to_merchant_category(row)
            if merchant:
                merchants.append(merchant)
        return merchants
