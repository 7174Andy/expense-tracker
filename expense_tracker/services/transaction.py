import logging
from dataclasses import replace

from expense_tracker.core.models import Transaction
from expense_tracker.core.transaction_repository import TransactionRepository
from expense_tracker.services.merchant import MerchantCategoryService

logger = logging.getLogger(__name__)


class TransactionService:
    """
    Service layer for transaction write operations.
    Ensures consistent auto-categorization across all entry points
    (manual add, PDF import, edit).
    """

    def __init__(
        self,
        transaction_repo: TransactionRepository,
        merchant_service: MerchantCategoryService,
    ):
        self.transaction_repo = transaction_repo
        self.merchant_service = merchant_service

    def add_transaction(self, transaction: Transaction) -> Transaction:
        """Add a transaction with auto-categorization.

        If the transaction's category is "Uncategorized", attempts to
        categorize it via the merchant category service.
        """
        if transaction.category == "Uncategorized":
            category = self.merchant_service.categorize_merchant(
                transaction.description, transaction.amount
            )
            transaction = replace(transaction, category=category)
        return self.transaction_repo.add_transaction(transaction)

    def get_transaction(self, transaction_id: int) -> Transaction | None:
        return self.transaction_repo.get_transaction(transaction_id)

    def update_transaction(self, transaction_id: int, data: dict) -> bool:
        """Update a transaction. If category changed, updates merchant mapping
        and re-categorizes uncategorized transactions.

        Returns True if merchant categories were updated, False otherwise.
        """
        prev = self.transaction_repo.get_transaction(transaction_id)
        self.transaction_repo.update_transaction(transaction_id, data)

        new_category = data.get("category")
        if prev and new_category and prev.category != new_category:
            self.merchant_service.update_category(prev.description, new_category)
            self.merchant_service.update_uncategorized_transactions()
            return True
        return False

    def suggest_category(self, description: str, amount: float) -> str:
        """Suggest a category for a transaction based on merchant mappings."""
        return self.merchant_service.categorize_merchant(description, amount)

    def import_transactions(self, transactions: list[Transaction]) -> int:
        """Import transactions with auto-categorization and duplicate detection.

        Returns the number of transactions imported (skipping duplicates).
        """
        imported = 0
        for transaction in transactions:
            category = self.merchant_service.categorize_merchant(
                transaction.description, transaction.amount
            )
            transaction = replace(transaction, category=category)
            if self.transaction_repo.transaction_exists(transaction):
                continue
            self.transaction_repo.add_transaction(transaction)
            imported += 1
        return imported

    def delete_transaction(self, transaction_id: int) -> None:
        self.transaction_repo.delete_transaction(transaction_id)

    def delete_multiple_transactions(self, transaction_ids: list[int]) -> int:
        return self.transaction_repo.delete_multiple_transactions(transaction_ids)
