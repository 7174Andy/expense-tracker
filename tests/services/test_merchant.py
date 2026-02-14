from datetime import date

import pytest

from expense_tracker.core.models import MerchantCategory, Transaction
from expense_tracker.core.merchant_repository import MerchantCategoryRepository
from expense_tracker.core.transaction_repository import TransactionRepository
from expense_tracker.services.merchant import MerchantCategoryService
from expense_tracker.utils.merchant_normalizer import normalize_merchant


@pytest.fixture
def merchant_repo():
    repo = MerchantCategoryRepository(":memory:")
    yield repo
    repo.conn.close()


@pytest.fixture
def transaction_repo():
    repo = TransactionRepository(":memory:")
    yield repo
    repo.conn.close()


@pytest.fixture
def service(merchant_repo, transaction_repo):
    return MerchantCategoryService(
        merchant_repo=merchant_repo,
        transaction_repo=transaction_repo,
        normalizer=normalize_merchant,
    )


# --- update_category ---


def test_update_category_creates_mapping(service, merchant_repo):
    """update_category should store a normalized merchant-category mapping."""
    service.update_category("Starbucks Coffee #123", "Coffee")

    mapping = merchant_repo.get_category("STARBUCKS COFFEE")
    assert mapping is not None
    assert mapping.category == "Coffee"


def test_update_category_overwrites_existing(service, merchant_repo):
    """Calling update_category again for the same merchant should overwrite."""
    service.update_category("Starbucks Coffee", "Coffee")
    service.update_category("Starbucks Coffee", "Dining")

    mapping = merchant_repo.get_category("STARBUCKS COFFEE")
    assert mapping is not None
    assert mapping.category == "Dining"


# --- categorize_merchant ---


def test_categorize_merchant_income_amount(service):
    """Positive amounts should always return 'Income'."""
    category = service.categorize_merchant("Some Merchant", 500.0)
    assert category == "Income"


def test_categorize_merchant_exact_match(service, merchant_repo):
    """Should return the category from an exact merchant key match."""
    merchant_repo.set_category(MerchantCategory("WHOLE FOODS", "Groceries"))

    category = service.categorize_merchant("Whole Foods", -50.0)
    assert category == "Groceries"


def test_categorize_merchant_fuzzy_match(service, merchant_repo):
    """Should fall back to fuzzy matching when no exact match exists."""
    merchant_repo.set_category(MerchantCategory("STARBUCKS COFFEE", "Coffee"))

    # Slightly different description that normalizes differently but fuzzy-matches
    category = service.categorize_merchant("STARBUCKS COFFE", -5.0)
    assert category == "Coffee"


def test_categorize_merchant_uncategorized_fallback(service):
    """Should return 'Uncategorized' when no exact or fuzzy match exists."""
    category = service.categorize_merchant("Random Unknown Store", -25.0)
    assert category == "Uncategorized"


def test_categorize_merchant_no_fuzzy_match_below_threshold(service, merchant_repo):
    """Should return 'Uncategorized' when fuzzy score is below the threshold."""
    merchant_repo.set_category(MerchantCategory("STARBUCKS COFFEE", "Coffee"))

    # Completely different name should not fuzzy match
    category = service.categorize_merchant("WALMART GROCERY", -30.0)
    assert category == "Uncategorized"


# --- fuzzy_lookup_merchant ---


def test_fuzzy_lookup_finds_close_match(service, merchant_repo):
    """Should find a merchant with a close fuzzy match."""
    merchant_repo.set_category(MerchantCategory("TRADER JOES", "Groceries"))

    result = service.fuzzy_lookup_merchant("TRADER JOE'S")
    assert result == "TRADER JOES"


def test_fuzzy_lookup_returns_none_below_threshold(service, merchant_repo):
    """Should return None when the best match is below the threshold."""
    merchant_repo.set_category(MerchantCategory("STARBUCKS COFFEE", "Coffee"))

    result = service.fuzzy_lookup_merchant("COMPLETELY DIFFERENT")
    assert result is None


def test_fuzzy_lookup_empty_merchants(service):
    """Should return None when no merchants exist in the repository."""
    result = service.fuzzy_lookup_merchant("STARBUCKS")
    assert result is None


# --- update_uncategorized_transactions ---


def test_update_uncategorized_transactions_recategorizes(
    service, merchant_repo, transaction_repo
):
    """Should recategorize uncategorized transactions when a mapping exists."""
    # Add uncategorized transactions
    transaction_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=-50.0,
            category="Uncategorized",
            description="Whole Foods Market",
        )
    )
    transaction_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 10),
            amount=-30.0,
            category="Uncategorized",
            description="Target Store",
        )
    )
    # Add a categorized transaction that should not be touched
    transaction_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 15),
            amount=-100.0,
            category="Shopping",
            description="Amazon",
        )
    )

    # Add a merchant mapping for Whole Foods
    merchant_repo.set_category(MerchantCategory("WHOLE FOODS MARKET", "Groceries"))

    service.update_uncategorized_transactions()

    # Whole Foods should now be categorized
    uncategorized = transaction_repo.get_all_transactions_by_category("Uncategorized")
    assert len(uncategorized) == 1
    assert uncategorized[0].description == "Target Store"

    groceries = transaction_repo.get_all_transactions_by_category("Groceries")
    assert len(groceries) == 1
    assert groceries[0].description == "Whole Foods Market"

    # Already-categorized transaction should remain unchanged
    shopping = transaction_repo.get_all_transactions_by_category("Shopping")
    assert len(shopping) == 1


def test_update_uncategorized_transactions_no_matches(
    service, merchant_repo, transaction_repo
):
    """Should leave transactions uncategorized when no mappings match."""
    transaction_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=-50.0,
            category="Uncategorized",
            description="Random Unknown Store",
        )
    )

    service.update_uncategorized_transactions()

    uncategorized = transaction_repo.get_all_transactions_by_category("Uncategorized")
    assert len(uncategorized) == 1


def test_update_uncategorized_transactions_empty(service, transaction_repo):
    """Should handle case with no uncategorized transactions gracefully."""
    transaction_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=-50.0,
            category="Groceries",
            description="Whole Foods",
        )
    )

    # Should not raise
    service.update_uncategorized_transactions()

    # Nothing should change
    groceries = transaction_repo.get_all_transactions_by_category("Groceries")
    assert len(groceries) == 1
