
from typing import Callable
import logging

from expense_tracker.core.repositories import TransactionRepository, MerchantCategoryRepository
from expense_tracker.core.models import MerchantCategory

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MerchantCategoryService:
    def __init__(self, merchant_repo: MerchantCategoryRepository, transaction_repo: TransactionRepository, normalizer: Callable[[str], str]):
        self.merchant_repo = merchant_repo
        self.transaction_repo = transaction_repo
        self.normalizer = normalizer

    def update_category(self, description: str, category: str) -> None:
        """Updates the category for a given merchant description."""
        normalized_merchant = self.normalizer(description)
        merchant_category = MerchantCategory(normalized_merchant, category)
        self.merchant_repo.set_category(merchant_category)
    
    def fuzzy_lookup_merchant(self, merchant: str, threshold: int = 90) -> str | None:
        """Attempts to find the closest matching merchant name using fuzzy string matching.

        Args:
            merchant (str): The normalized merchant name to look up.
            threshold (int, optional): The minimum score for a match to be considered valid. Defaults to 90.

        Returns:
            str | None: The best matching merchant name if found, otherwise None.
        """
        from rapidfuzz import process

        merchants = self.merchant_repo.get_all_merchants()
        if not merchants:
            return None
        
        merchant_keys = [m.merchant_key for m in merchants]
        
        match = process.extractOne(merchant, merchant_keys, score_cutoff=threshold)
        if match:
            return match[0]
        return None

    def categorize_merchant(self, description: str, amount: float) -> str:
        """Categorizes the merchant based on the description and amount.

        Args:
            description (str): The raw description from the transaction.
            amount (float): The transaction amount.

        Returns:
            str: The category of the merchant.
        """
        merchant = self.normalizer(description)

        # If the amount is positive, it's likely an income, so we can categorize it as "Income"
        if amount > 0:
            return "Income"

        # First try exact match
        merchant_category = self.merchant_repo.get_category(merchant)
        if merchant_category:
            return merchant_category.category
        
        # If no exact match, try fuzzy matching
        fuzzy_match = self.fuzzy_lookup_merchant(merchant)
        if fuzzy_match:
            merchant_category = self.merchant_repo.get_category(fuzzy_match)
            if merchant_category:
                return merchant_category.category

        return "Uncategorized"

    def update_uncategorized_transactions(self) -> None:
        # Get all uncategorized transactions
        transactions = self.transaction_repo.get_all_transactions_by_category("Uncategorized")

        # For each transaction, update the category if the normalized merchant matches the updated category
        for transaction in transactions:
            # Check if the normalized merchant matches the updated category's merchant key
            category = self.categorize_merchant(transaction.description, transaction.amount)

            # If the category is not "Uncategorized", update the transaction category
            if category != "Uncategorized":
                self.transaction_repo.update_transaction(transaction.id, {"category": category})