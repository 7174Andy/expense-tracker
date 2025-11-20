from datetime import date

import pytest

from expense_tracker.core.model import MerchantCategory, Transaction
from expense_tracker.core.repository import (
    MerchantCategoryRepository,
    TransactionRepository,
)


@pytest.fixture
def in_memory_repo():
    """
    Provides an in-memory TransactionRepository for testing.
    """
    repo = TransactionRepository(":memory:")
    yield repo
    repo.conn.close()


@pytest.fixture
def in_memory_merchant_repo():
    """
    Provides an in-memory MerchantCategoryRepository for testing.
    """
    repo = MerchantCategoryRepository(":memory:")
    yield repo
    repo.conn.close()


def test_set_and_get_category(in_memory_merchant_repo):
    repo: MerchantCategoryRepository = in_memory_merchant_repo
    repo.set_category(MerchantCategory("Amazon", "Shopping"))
    merchant_category = repo.get_category("Amazon")
    assert merchant_category is not None
    assert merchant_category.category == "Shopping"


def test_update_category(in_memory_merchant_repo):
    repo: MerchantCategoryRepository = in_memory_merchant_repo
    repo.set_category(MerchantCategory("Netflix", "Entertainment"))
    repo.set_category(MerchantCategory("Netflix", "Streaming"))
    merchant_category = repo.get_category("Netflix")
    assert merchant_category is not None
    assert merchant_category.category == "Streaming"


def test_get_non_existent_category(in_memory_merchant_repo):
    repo: MerchantCategoryRepository = in_memory_merchant_repo
    assert repo.get_category("Unknown") is None


def test_get_all_merchants(in_memory_merchant_repo):
    repo: MerchantCategoryRepository = in_memory_merchant_repo
    repo.set_category(MerchantCategory("MerchantA", "Category1"))
    repo.set_category(MerchantCategory("MerchantB", "Category2"))
    merchants = repo.get_all_merchants()
    assert len(merchants) == 2
    merchant_keys = [m.merchant_key for m in merchants]
    assert "MerchantA" in merchant_keys
    assert "MerchantB" in merchant_keys



def test_add_transaction(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    saved = repo.add_transaction(
        Transaction(id=None, date=date.today(), amount=100.0, category="Food", description="Groceries")
    )
    assert saved.id is not None
    transaction = repo.get_transaction(saved.id)
    assert transaction is not None
    assert transaction.amount == 100.0
    assert transaction.category == "Food"
    assert transaction.description == "Groceries"

def test_get_transaction(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    saved = repo.add_transaction(
        Transaction(id=None, date=date.today(), amount=50.0, category="Transport", description="Bus fare")
    )
    assert saved.id is not None
    transaction = repo.get_transaction(saved.id)
    assert transaction is not None
    assert transaction.id == saved.id
    assert transaction.amount == 50.0

def test_get_non_existent_transaction(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    transaction = repo.get_transaction(999) # ID that doesn't exist
    assert transaction is None

def test_get_all_transactions(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(Transaction(id=None, date=date.fromisoformat("2023-01-01"), amount=10.0, category="Food", description="Lunch"))
    repo.add_transaction(Transaction(id=None, date=date.fromisoformat("2023-01-02"), amount=20.0, category="Utilities", description="Electricity"))
    transactions = repo.get_all_transactions()
    assert len(transactions) == 2
    assert transactions[0].amount == 20.0 # Ordered by date DESC
    assert transactions[1].amount == 10.0

def test_daily_summary(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(Transaction(id=None, date=date.fromisoformat("2023-01-01"), amount=10.0, category="Food", description="Lunch"))
    repo.add_transaction(Transaction(id=None, date=date.fromisoformat("2023-01-01"), amount=15.0, category="Food", description="Dinner"))
    repo.add_transaction(Transaction(id=None, date=date.fromisoformat("2023-01-01"), amount=5.0, category="Transport", description="Taxi"))
    repo.add_transaction(Transaction(id=None, date=date.fromisoformat("2023-01-02"), amount=20.0, category="Utilities", description="Electricity"))

    summary = repo.daily_summary("2023-01-01")
    assert len(summary) == 2
    categories = {row["category"]: row["total"] for row in summary}
    assert categories["Food"] == 25.0
    assert categories["Transport"] == 5.0

def test_delete_transaction(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    saved = repo.add_transaction(
        Transaction(id=None, date=date.today(), amount=75.0, category="Shopping", description="New shirt")
    )
    assert saved.id is not None
    
    # Verify transaction exists
    transaction = repo.get_transaction(saved.id)
    assert transaction is not None

    repo.delete_transaction(saved.id)
    
    # Verify transaction is deleted
    transaction = repo.get_transaction(saved.id)
    assert transaction is None
    
    # Ensure no other transactions were affected
    transactions = repo.get_all_transactions()
    assert len(transactions) == 0

def test_delete_multiple_transactions(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    first = repo.add_transaction(
        Transaction(id=None, date=date.fromisoformat("2023-01-01"), amount=10.0, category="Food", description="Lunch")
    )
    second = repo.add_transaction(
        Transaction(id=None, date=date.fromisoformat("2023-01-01"), amount=15.0, category="Food", description="Dinner")
    )
    third = repo.add_transaction(
        Transaction(id=None, date=date.fromisoformat("2023-01-01"), amount=5.0, category="Transport", description="Taxi")
    )
    assert first.id is not None and second.id is not None and third.id is not None
    id1, id2, id3 = first.id, second.id, third.id
    
    # Test deleting multiple transactions
    deleted_rows = repo.delete_multiple_transactions([id1, id3])
    assert deleted_rows == 2
    
    assert repo.get_transaction(id1) is None
    assert repo.get_transaction(id2) is not None
    assert repo.get_transaction(id3) is None
    
    remaining_transactions = repo.get_all_transactions()
    assert len(remaining_transactions) == 1
    assert remaining_transactions[0].id == id2
    
    # Test deleting with an empty list
    deleted_rows = repo.delete_multiple_transactions([])
    assert deleted_rows == 0
    assert len(repo.get_all_transactions()) == 1

def test_update_transaction(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    saved = repo.add_transaction(
        Transaction(id=None, date=date.today(), amount=100.0, category="Food", description="Groceries")
    )
    assert saved.id is not None
    
    repo.update_transaction(saved.id, {"amount": 120.0, "category": "Shopping"})
    
    updated_transaction = repo.get_transaction(saved.id)
    assert updated_transaction is not None
    assert updated_transaction.amount == 120.0
    assert updated_transaction.category == "Shopping"
    assert updated_transaction.description == "Groceries" # Should remain unchanged


def test_count_all_transactions(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    assert repo.count_all_transactions() == 0
    
    repo.add_transaction(Transaction(id=None, date=date.fromisoformat("2023-01-01"), amount=10.0, category="Food", description="Lunch"))
    repo.add_transaction(Transaction(id=None, date=date.fromisoformat("2023-01-02"), amount=20.0, category="Utilities", description="Electricity"))
    assert repo.count_all_transactions() == 2
    
    saved = repo.add_transaction(Transaction(id=None, date=date.fromisoformat("2023-01-03"), amount=30.0, category="Fun", description="Movies"))
    assert repo.count_all_transactions() == 3

    repo.delete_transaction(saved.id)
    assert repo.count_all_transactions() == 2
