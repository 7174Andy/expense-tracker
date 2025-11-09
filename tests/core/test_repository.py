import pytest
from expense_tracker.core.repository import TransactionRepository
from datetime import date

@pytest.fixture
def in_memory_repo():
    """
    Provides an in-memory TransactionRepository for testing.
    """
    repo = TransactionRepository(":memory:")
    yield repo
    repo.conn.close()

def test_add_transaction(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    transaction_id = repo.add_transaction(str(date.today()), 100.0, "Food", "Groceries")
    assert transaction_id is not None
    transaction = repo.get_transaction(transaction_id)
    assert transaction["amount"] == 100.0
    assert transaction["category"] == "Food"
    assert transaction["description"] == "Groceries"

def test_get_transaction(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    transaction_id = repo.add_transaction(str(date.today()), 50.0, "Transport", "Bus fare")
    transaction = repo.get_transaction(transaction_id)
    assert transaction is not None
    assert transaction["id"] == transaction_id
    assert transaction["amount"] == 50.0

def test_get_non_existent_transaction(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    transaction = repo.get_transaction(999) # ID that doesn't exist
    assert transaction is None

def test_get_all_transactions(in_memory_repo):
    repo = in_memory_repo
    repo.add_transaction("2023-01-01", 10.0, "Food", "Lunch")
    repo.add_transaction("2023-01-02", 20.0, "Utilities", "Electricity")
    transactions = repo.get_all_transactions()
    assert len(transactions) == 2
    assert transactions[0]["amount"] == 20.0 # Ordered by date DESC
    assert transactions[1]["amount"] == 10.0

def test_daily_summary(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction("2023-01-01", 10.0, "Food", "Lunch")
    repo.add_transaction("2023-01-01", 15.0, "Food", "Dinner")
    repo.add_transaction("2023-01-01", 5.0, "Transport", "Taxi")
    repo.add_transaction("2023-01-02", 20.0, "Utilities", "Electricity")

    summary = repo.daily_summary("2023-01-01")
    assert len(summary) == 2
    categories = {row["category"]: row["total"] for row in summary}
    assert categories["Food"] == 25.0
    assert categories["Transport"] == 5.0

def test_delete_transaction(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    transaction_id = repo.add_transaction(str(date.today()), 75.0, "Shopping", "New shirt")
    
    # Verify transaction exists
    transaction = repo.get_transaction(transaction_id)
    assert transaction is not None

    repo.delete_transaction(transaction_id)
    
    # Verify transaction is deleted
    transaction = repo.get_transaction(transaction_id)
    assert transaction is None
    
    # Ensure no other transactions were affected
    transactions = repo.get_all_transactions()
    assert len(transactions) == 0
