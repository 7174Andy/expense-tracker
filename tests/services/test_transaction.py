from datetime import date

import pytest

from expense_tracker.core.models import Transaction, MerchantCategory
from expense_tracker.core.transaction_repository import TransactionRepository
from expense_tracker.core.merchant_repository import MerchantCategoryRepository
from expense_tracker.services.merchant import MerchantCategoryService
from expense_tracker.services.transaction import TransactionService
from expense_tracker.utils.merchant_normalizer import normalize_merchant


@pytest.fixture
def in_memory_repo():
    repo = TransactionRepository(":memory:")
    yield repo
    repo.conn.close()


@pytest.fixture
def merchant_repo():
    repo = MerchantCategoryRepository(":memory:")
    yield repo
    repo.conn.close()


@pytest.fixture
def transaction_service(in_memory_repo, merchant_repo):
    merchant_service = MerchantCategoryService(
        merchant_repo, in_memory_repo, normalize_merchant
    )
    return TransactionService(in_memory_repo, merchant_service)


def test_add_transaction_auto_categorizes(transaction_service, merchant_repo):
    """Uncategorized transactions get auto-categorized via merchant mappings."""
    merchant_repo.set_category(MerchantCategory("WHOLE FOODS", "Groceries"))

    txn = Transaction(
        id=None,
        date=date(2023, 1, 5),
        amount=-50.0,
        category="Uncategorized",
        description="WHOLE FOODS MARKET #123",
    )
    saved = transaction_service.add_transaction(txn)

    assert saved.category == "Groceries"
    assert saved.id is not None


def test_add_transaction_preserves_explicit_category(transaction_service, merchant_repo):
    """Transactions with an explicit category are not re-categorized."""
    merchant_repo.set_category(MerchantCategory("WHOLE FOODS", "Groceries"))

    txn = Transaction(
        id=None,
        date=date(2023, 1, 5),
        amount=-50.0,
        category="Food",
        description="WHOLE FOODS MARKET #123",
    )
    saved = transaction_service.add_transaction(txn)

    assert saved.category == "Food"


def test_add_transaction_income_auto_categorized(transaction_service):
    """Positive amounts get categorized as Income."""
    txn = Transaction(
        id=None,
        date=date(2023, 1, 5),
        amount=2000.0,
        category="Uncategorized",
        description="EMPLOYER DIRECT DEP",
    )
    saved = transaction_service.add_transaction(txn)

    assert saved.category == "Income"


def test_add_transaction_no_mapping_stays_uncategorized(transaction_service):
    """Transactions with no merchant mapping stay Uncategorized."""
    txn = Transaction(
        id=None,
        date=date(2023, 1, 5),
        amount=-25.0,
        category="Uncategorized",
        description="RANDOM SHOP XYZ",
    )
    saved = transaction_service.add_transaction(txn)

    assert saved.category == "Uncategorized"


def test_update_transaction_updates_merchant_categories(
    transaction_service, in_memory_repo, merchant_repo
):
    """Changing category on update should update merchant mapping and recategorize."""
    # Add an uncategorized transaction
    txn1 = in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=-50.0,
            category="Uncategorized",
            description="WHOLE FOODS MARKET",
        )
    )
    # Add another uncategorized transaction with similar description
    txn2 = in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 10),
            amount=-30.0,
            category="Uncategorized",
            description="WHOLE FOODS",
        )
    )

    # Update txn1's category — should trigger merchant mapping update
    categories_updated = transaction_service.update_transaction(
        txn1.id, {"category": "Groceries"}
    )

    assert categories_updated is True

    # txn2 should now be auto-categorized
    updated_txn2 = in_memory_repo.get_transaction(txn2.id)
    assert updated_txn2.category == "Groceries"


def test_update_transaction_no_category_change(transaction_service, in_memory_repo):
    """Updating without changing category should not trigger merchant update."""
    txn = in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=-50.0,
            category="Food",
            description="Lunch",
        )
    )

    categories_updated = transaction_service.update_transaction(
        txn.id, {"amount": -60.0, "category": "Food"}
    )

    assert categories_updated is False
    updated = in_memory_repo.get_transaction(txn.id)
    assert updated.amount == -60.0


def test_import_transactions_categorizes_and_deduplicates(
    transaction_service, in_memory_repo, merchant_repo
):
    """Import should auto-categorize and skip duplicates."""
    merchant_repo.set_category(MerchantCategory("AMAZON", "Shopping"))

    # Pre-existing transaction (will be a duplicate)
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=-50.0,
            category="Shopping",
            description="AMAZON.COM",
        )
    )

    transactions = [
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=-50.0,
            category="Uncategorized",
            description="AMAZON.COM",
        ),
        Transaction(
            id=None,
            date=date(2023, 1, 10),
            amount=-30.0,
            category="Uncategorized",
            description="AMAZON PRIME",
        ),
        Transaction(
            id=None,
            date=date(2023, 1, 15),
            amount=2000.0,
            category="Uncategorized",
            description="EMPLOYER PAYROLL",
        ),
    ]

    imported = transaction_service.import_transactions(transactions)

    assert imported == 2  # first one skipped as duplicate

    # Check that imported transactions were categorized
    all_txns = in_memory_repo.get_all_transactions()
    assert len(all_txns) == 3  # 1 existing + 2 imported

    # Find the Amazon Prime transaction
    prime_txn = next(t for t in all_txns if "PRIME" in t.description)
    assert prime_txn.category == "Shopping"

    # Find the income transaction
    income_txn = next(t for t in all_txns if "PAYROLL" in t.description)
    assert income_txn.category == "Income"


def test_import_transactions_empty_list(transaction_service):
    """Importing empty list returns 0."""
    imported = transaction_service.import_transactions([])
    assert imported == 0


def test_suggest_category(transaction_service, merchant_repo):
    """suggest_category delegates to merchant service."""
    merchant_repo.set_category(MerchantCategory("STARBUCKS", "Coffee"))

    result = transaction_service.suggest_category("STARBUCKS COFFEE #123", -5.0)
    assert result == "Coffee"


def test_suggest_category_no_match(transaction_service):
    """suggest_category returns Uncategorized when no match."""
    result = transaction_service.suggest_category("UNKNOWN MERCHANT", -10.0)
    assert result == "Uncategorized"


def test_delete_multiple_transactions(transaction_service, in_memory_repo):
    """delete_multiple_transactions delegates to repository."""
    txn1 = in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=-50.0,
            category="Food",
            description="Lunch",
        )
    )
    txn2 = in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 10),
            amount=-30.0,
            category="Food",
            description="Dinner",
        )
    )

    deleted = transaction_service.delete_multiple_transactions([txn1.id, txn2.id])
    assert deleted == 2
    assert in_memory_repo.get_transaction(txn1.id) is None
    assert in_memory_repo.get_transaction(txn2.id) is None
