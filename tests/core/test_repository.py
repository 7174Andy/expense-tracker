from datetime import date

import pytest

from expense_tracker.core.models import MerchantCategory, Transaction
from expense_tracker.core.transaction_repository import TransactionRepository
from expense_tracker.core.merchant_repository import MerchantCategoryRepository


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
        Transaction(
            id=None,
            date=date.today(),
            amount=100.0,
            category="Food",
            description="Groceries",
        )
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
        Transaction(
            id=None,
            date=date.today(),
            amount=50.0,
            category="Transport",
            description="Bus fare",
        )
    )
    assert saved.id is not None
    transaction = repo.get_transaction(saved.id)
    assert transaction is not None
    assert transaction.id == saved.id
    assert transaction.amount == 50.0


def test_get_non_existent_transaction(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    transaction = repo.get_transaction(999)  # ID that doesn't exist
    assert transaction is None


def test_get_all_transactions(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-01"),
            amount=10.0,
            category="Food",
            description="Lunch",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-02"),
            amount=20.0,
            category="Utilities",
            description="Electricity",
        )
    )
    transactions = repo.get_all_transactions()
    assert len(transactions) == 2
    assert transactions[0].amount == 20.0  # Ordered by date DESC
    assert transactions[1].amount == 10.0


def test_daily_summary(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-01"),
            amount=10.0,
            category="Food",
            description="Lunch",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-01"),
            amount=15.0,
            category="Food",
            description="Dinner",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-01"),
            amount=5.0,
            category="Transport",
            description="Taxi",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-02"),
            amount=20.0,
            category="Utilities",
            description="Electricity",
        )
    )

    summary = repo.daily_summary("2023-01-01")
    assert len(summary) == 2
    categories = {row["category"]: row["total"] for row in summary}
    assert categories["Food"] == 25.0
    assert categories["Transport"] == 5.0


def test_delete_transaction(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    saved = repo.add_transaction(
        Transaction(
            id=None,
            date=date.today(),
            amount=75.0,
            category="Shopping",
            description="New shirt",
        )
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
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-01"),
            amount=10.0,
            category="Food",
            description="Lunch",
        )
    )
    second = repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-01"),
            amount=15.0,
            category="Food",
            description="Dinner",
        )
    )
    third = repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-01"),
            amount=5.0,
            category="Transport",
            description="Taxi",
        )
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
        Transaction(
            id=None,
            date=date.today(),
            amount=100.0,
            category="Food",
            description="Groceries",
        )
    )
    assert saved.id is not None

    repo.update_transaction(saved.id, {"amount": 120.0, "category": "Shopping"})

    updated_transaction = repo.get_transaction(saved.id)
    assert updated_transaction is not None
    assert updated_transaction.amount == 120.0
    assert updated_transaction.category == "Shopping"
    assert updated_transaction.description == "Groceries"  # Should remain unchanged


def test_count_all_transactions(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    assert repo.count_all_transactions() == 0

    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-01"),
            amount=10.0,
            category="Food",
            description="Lunch",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-02"),
            amount=20.0,
            category="Utilities",
            description="Electricity",
        )
    )
    assert repo.count_all_transactions() == 2

    saved = repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-03"),
            amount=30.0,
            category="Fun",
            description="Movies",
        )
    )
    assert repo.count_all_transactions() == 3

    repo.delete_transaction(saved.id)
    assert repo.count_all_transactions() == 2


def test_search_by_keyword(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-01"),
            amount=-50.0,
            category="Shopping",
            description="AMAZON.COM",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-02"),
            amount=-30.0,
            category="Shopping",
            description="Amazon Prime",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-03"),
            amount=-20.0,
            category="Food",
            description="Walmart Grocery",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-04"),
            amount=-15.0,
            category="Food",
            description="Target",
        )
    )

    # Search for "amazon" (case-insensitive)
    results = repo.search_by_keyword("amazon")
    assert len(results) == 2
    assert all("amazon" in t.description.lower() for t in results)
    assert results[0].date > results[1].date  # Ordered by date DESC

    # Search for partial match
    results = repo.search_by_keyword("AMAZ")
    assert len(results) == 2

    # Search for "grocery"
    results = repo.search_by_keyword("grocery")
    assert len(results) == 1
    assert results[0].description == "Walmart Grocery"

    # Search for non-existent keyword
    results = repo.search_by_keyword("netflix")
    assert len(results) == 0


def test_search_by_keyword_empty(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-01"),
            amount=-50.0,
            category="Shopping",
            description="Amazon",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-02"),
            amount=-30.0,
            category="Food",
            description="Walmart",
        )
    )

    # Empty keyword returns all transactions
    results = repo.search_by_keyword("")
    assert len(results) == 2

    # None keyword returns all transactions
    results = repo.search_by_keyword(None)
    assert len(results) == 2


def test_search_by_keyword_with_pagination(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add multiple Amazon transactions
    for i in range(5):
        repo.add_transaction(
            Transaction(
                id=None,
                date=date.fromisoformat(f"2023-01-0{i + 1}"),
                amount=-10.0 * (i + 1),
                category="Shopping",
                description=f"Amazon order {i + 1}",
            )
        )

    # Get first page (limit 2)
    results = repo.search_by_keyword("amazon", limit=2, offset=0)
    assert len(results) == 2
    assert results[0].description == "Amazon order 5"  # Most recent

    # Get second page
    results = repo.search_by_keyword("amazon", limit=2, offset=2)
    assert len(results) == 2
    assert results[0].description == "Amazon order 3"


def test_count_search_results(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-01"),
            amount=-50.0,
            category="Shopping",
            description="AMAZON.COM",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-02"),
            amount=-30.0,
            category="Shopping",
            description="Amazon Prime",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-03"),
            amount=-20.0,
            category="Food",
            description="Walmart Grocery",
        )
    )

    # Count amazon results
    count = repo.count_search_results("amazon")
    assert count == 2

    # Count walmart results
    count = repo.count_search_results("walmart")
    assert count == 1

    # Count non-existent
    count = repo.count_search_results("netflix")
    assert count == 0

    # Empty keyword returns total count
    count = repo.count_search_results("")
    assert count == 3

    # None keyword returns total count
    count = repo.count_search_results(None)
    assert count == 3


def test_get_daily_spending_for_month_with_data(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add expenses and income for January 2023
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=-50.0,  # Expense
            category="Food",
            description="Groceries",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=-30.0,  # Another expense same day
            category="Transport",
            description="Taxi",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-100.0,  # Expense
            category="Shopping",
            description="Clothes",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=500.0,  # Income (should be excluded)
            category="Income",
            description="Salary",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-02-10"),
            amount=-25.0,  # Different month (should be excluded)
            category="Food",
            description="Lunch",
        )
    )

    spending = repo.get_daily_spending_range(date(2023, 1, 1), date(2023, 2, 1))

    # Should only include expenses from January 2023
    assert len(spending) == 2
    assert spending[5] == 80.0  # Day 5: 50 + 30
    assert spending[15] == 100.0  # Day 15: 100 (income excluded)
    assert 10 not in spending  # No transactions on day 10


def test_get_daily_spending_for_month_empty(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add transaction for different month
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )

    # Query for empty month
    spending = repo.get_daily_spending_range(date(2023, 3, 1), date(2023, 4, 1))
    assert len(spending) == 0
    assert spending == {}


def test_get_daily_spending_excludes_income(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add only income transactions
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=1000.0,  # Positive = income
            category="Income",
            description="Salary",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-10"),
            amount=500.0,  # Positive = income
            category="Income",
            description="Bonus",
        )
    )

    spending = repo.get_daily_spending_range(date(2023, 1, 1), date(2023, 2, 1))

    # Should return empty since only income (no expenses)
    assert len(spending) == 0
    assert spending == {}


def test_get_transactions_for_date_with_data(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    target = date.fromisoformat("2023-01-05")

    # Add transactions on target date
    repo.add_transaction(
        Transaction(
            id=None,
            date=target,
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=target,
            amount=-30.0,
            category="Transport",
            description="Taxi",
        )
    )
    # Add transaction on different date (should be excluded)
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-06"),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )

    transactions = repo.get_transactions_for_date(target)

    assert len(transactions) == 2
    # Verify all returned transactions have the target date
    assert all(t.date == target for t in transactions)


def test_get_transactions_for_date_empty(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add transaction on different date
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )

    # Query for date with no transactions
    transactions = repo.get_transactions_for_date(date.fromisoformat("2023-01-10"))
    assert len(transactions) == 0
    assert transactions == []


def test_get_transactions_for_date_ordering(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    target = date.fromisoformat("2023-01-05")

    # Add transactions with different amounts
    repo.add_transaction(
        Transaction(
            id=None,
            date=target,
            amount=-10.0,
            category="Food",
            description="Snack",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=target,
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=target,
            amount=-50.0,
            category="Transport",
            description="Taxi",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=target,
            amount=500.0,  # Income
            category="Income",
            description="Paycheck",
        )
    )

    transactions = repo.get_transactions_for_date(target)

    # Should be ordered by amount ASC (most negative first, then positive)
    assert len(transactions) == 4
    assert transactions[0].amount == -100.0  # Largest expense first
    assert transactions[1].amount == -50.0
    assert transactions[2].amount == -10.0
    assert transactions[3].amount == 500.0  # Income last


def test_get_months_with_expenses(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add expenses across different months
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-03-10"),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-20"),
            amount=-30.0,
            category="Transport",
            description="Taxi",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2024-02-05"),
            amount=-75.0,
            category="Food",
            description="Restaurant",
        )
    )
    # Add income (should be excluded)
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-02-01"),
            amount=1000.0,
            category="Income",
            description="Salary",
        )
    )

    months = repo.get_months_with_expenses()

    # Should return months with expenses only, most recent first
    assert len(months) == 3
    assert months[0] == (2024, 2)  # February 2024
    assert months[1] == (2023, 3)  # March 2023
    assert months[2] == (2023, 1)  # January 2023 (duplicate month, single entry)
    # February 2023 should NOT be included (only income)


def test_get_months_with_expenses_empty(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add only income
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=1000.0,
            category="Income",
            description="Salary",
        )
    )

    months = repo.get_months_with_expenses()

    # Should return empty list (no expenses)
    assert len(months) == 0
    assert months == []


def test_get_monthly_net_income_with_income_and_expenses(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add income and expenses for January 2023
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=1000.0,  # Income
            category="Income",
            description="Salary",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-10"),
            amount=-50.0,  # Expense
            category="Food",
            description="Groceries",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-25.0,  # Expense
            category="Transport",
            description="Taxi",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-20"),
            amount=200.0,  # Income
            category="Income",
            description="Bonus",
        )
    )

    net_income = repo.get_monthly_net_income(date(2023, 1, 1), date(2023, 2, 1))

    # Net income = 1000 + 200 - 50 - 25 = 1125
    assert net_income == 1125.0


def test_get_monthly_net_income_only_expenses(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add only expenses
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-10"),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-50.0,
            category="Food",
            description="Restaurant",
        )
    )

    net_income = repo.get_monthly_net_income(date(2023, 1, 1), date(2023, 2, 1))

    # Net income = -100 - 50 = -150
    assert net_income == -150.0


def test_get_monthly_net_income_no_transactions(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add transaction for different month
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-02-10"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )

    # Query for month with no transactions
    net_income = repo.get_monthly_net_income(date(2023, 1, 1), date(2023, 2, 1))

    # Should return 0.0 for empty month
    assert net_income == 0.0


def test_get_monthly_net_income_only_income(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add only income
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=2000.0,
            category="Income",
            description="Salary",
        )
    )

    net_income = repo.get_monthly_net_income(date(2023, 1, 1), date(2023, 2, 1))

    assert net_income == 2000.0


def test_get_top_spending_category_with_multiple_categories(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add expenses in different categories
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=-100.0,
            category="Groceries",
            description="Whole Foods",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-10"),
            amount=-50.0,
            category="Groceries",
            description="Trader Joes",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-75.0,
            category="Restaurants",
            description="Dinner",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-20"),
            amount=-25.0,
            category="Transportation",
            description="Uber",
        )
    )

    top_category = repo.get_top_spending_category(date(2023, 1, 1), date(2023, 2, 1))

    # Groceries has highest spending: 100 + 50 = 150
    assert top_category is not None
    assert top_category[0] == "Groceries"
    assert top_category[1] == 150.0


def test_get_top_spending_category_exclude_income(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add income and expenses
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=2000.0,  # Income (should be excluded)
            category="Income",
            description="Salary",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-10"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )

    top_category = repo.get_top_spending_category(date(2023, 1, 1), date(2023, 2, 1))

    # Should return Food, not Income
    assert top_category is not None
    assert top_category[0] == "Food"
    assert top_category[1] == 50.0


def test_get_top_spending_category_no_expenses(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add only income
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=1000.0,
            category="Income",
            description="Salary",
        )
    )

    top_category = repo.get_top_spending_category(date(2023, 1, 1), date(2023, 2, 1))

    # Should return None when no expenses exist
    assert top_category is None


def test_get_top_spending_category_empty_month(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add transaction for different month
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-02-10"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )

    # Query for month with no transactions
    top_category = repo.get_top_spending_category(date(2023, 1, 1), date(2023, 2, 1))

    # Should return None
    assert top_category is None


def test_get_latest_month_with_data(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add transactions across different months
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-03-10"),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2024-02-05"),
            amount=-75.0,
            category="Food",
            description="Restaurant",
        )
    )

    latest_year, latest_month = repo.get_latest_month_with_data()

    # Should return the most recent month (February 2024)
    assert latest_year == 2024
    assert latest_month == 2


def test_get_latest_month_with_data_empty(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # No transactions

    latest_year, latest_month = repo.get_latest_month_with_data()

    # Should return current month when no transactions exist
    today = date.today()
    assert latest_year == today.year
    assert latest_month == today.month


def test_get_all_months_with_data(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add transactions across different months
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-20"),
            amount=-30.0,
            category="Transport",
            description="Taxi",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-03-10"),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2024-02-05"),
            amount=-75.0,
            category="Food",
            description="Restaurant",
        )
    )

    months = repo.get_all_months_with_data()

    # Should return a set of all (year, month) tuples with data
    assert isinstance(months, set)
    assert len(months) == 3
    assert (2023, 1) in months  # January 2023 (two transactions)
    assert (2023, 3) in months  # March 2023
    assert (2024, 2) in months  # February 2024


def test_get_all_months_with_data_empty(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # No transactions

    months = repo.get_all_months_with_data()

    # Should return empty set
    assert isinstance(months, set)
    assert len(months) == 0


def test_get_all_months_with_data_single_month(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add multiple transactions in the same month
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-05-10"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-05-15"),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-05-25"),
            amount=-30.0,
            category="Transport",
            description="Taxi",
        )
    )

    months = repo.get_all_months_with_data()

    # Should return set with single month (no duplicates)
    assert isinstance(months, set)
    assert len(months) == 1
    assert (2023, 5) in months


def test_transaction_exists_returns_true_for_duplicate(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )

    assert repo.transaction_exists(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )


def test_transaction_exists_returns_false_when_not_found(in_memory_repo):
    repo: TransactionRepository = in_memory_repo

    assert not repo.transaction_exists(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )


def test_transaction_exists_different_date(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )

    assert not repo.transaction_exists(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-16"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )


def test_transaction_exists_different_amount(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )

    assert not repo.transaction_exists(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-75.0,
            category="Food",
            description="Groceries",
        )
    )


def test_get_daily_spending_for_year_with_data(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add expenses across different days in 2023
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-30.0,
            category="Transport",
            description="Taxi",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-06-20"),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )
    # Income should be excluded
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-03-01"),
            amount=2000.0,
            category="Income",
            description="Salary",
        )
    )
    # Different year should be excluded
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2024-01-15"),
            amount=-75.0,
            category="Food",
            description="Restaurant",
        )
    )

    spending = repo.get_daily_spending_for_year(2023)

    assert len(spending) == 2
    assert spending["2023-01-15"] == 80.0  # 50 + 30 aggregated
    assert spending["2023-06-20"] == 100.0
    assert "2023-03-01" not in spending  # Income excluded
    assert "2024-01-15" not in spending  # Different year excluded


def test_get_daily_spending_for_year_empty(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    spending = repo.get_daily_spending_for_year(2023)
    assert spending == {}


def test_get_years_with_expenses(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-05-10"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2024-02-15"),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )
    # Income-only year should be excluded
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2022-01-01"),
            amount=3000.0,
            category="Income",
            description="Salary",
        )
    )

    years = repo.get_years_with_expenses()

    assert years == [2024, 2023]  # Descending, income-only year excluded


def test_get_years_with_expenses_empty(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    years = repo.get_years_with_expenses()
    assert years == []


def test_transaction_exists_different_description(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )

    assert not repo.transaction_exists(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-50.0,
            category="Food",
            description="Restaurant",
        )
    )


def test_get_total_expense(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add expenses and income for January 2023
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-10"),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )
    # Income should be excluded
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=2000.0,
            category="Income",
            description="Salary",
        )
    )

    total = repo.get_total_expense(date(2023, 1, 1), date(2023, 2, 1))

    # Only negative amounts summed as absolute values: 50 + 100 = 150
    assert total == 150.0


def test_get_total_expense_no_data(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    total = repo.get_total_expense(date(2023, 1, 1), date(2023, 2, 1))
    assert total == 0.0


def test_get_transaction_count(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-10"),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=2000.0,
            category="Income",
            description="Salary",
        )
    )

    count = repo.get_transaction_count(date(2023, 1, 1), date(2023, 2, 1))

    # All transactions counted (including income)
    assert count == 3


def test_get_transaction_count_no_data(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    count = repo.get_transaction_count(date(2023, 1, 1), date(2023, 2, 1))
    assert count == 0


def test_get_all_transactions_by_category(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-10"),
            amount=-30.0,
            category="Food",
            description="Restaurant",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )

    food_transactions = repo.get_all_transactions_by_category("Food")
    assert len(food_transactions) == 2
    assert all(t.category == "Food" for t in food_transactions)
    # Ordered by date DESC
    assert food_transactions[0].date > food_transactions[1].date

    shopping_transactions = repo.get_all_transactions_by_category("Shopping")
    assert len(shopping_transactions) == 1
    assert shopping_transactions[0].description == "Clothes"


def test_get_all_transactions_by_category_empty(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )

    result = repo.get_all_transactions_by_category("NonExistent")
    assert result == []


def test_get_monthly_cashflow_trend_with_data(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    # Add transactions across 3 months
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=2000.0,
            category="Income",
            description="Salary",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-15"),
            amount=-500.0,
            category="Food",
            description="Groceries",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-02-05"),
            amount=2000.0,
            category="Income",
            description="Salary",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-02-15"),
            amount=-800.0,
            category="Shopping",
            description="Clothes",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-03-05"),
            amount=2000.0,
            category="Income",
            description="Salary",
        )
    )
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-03-15"),
            amount=-300.0,
            category="Food",
            description="Lunch",
        )
    )

    trend = repo.get_monthly_cashflow_trend(3)

    # Ordered ascending by year/month
    assert len(trend) == 3
    assert trend[0] == (2023, 1, 1500.0)  # 2000 - 500
    assert trend[1] == (2023, 2, 1200.0)  # 2000 - 800
    assert trend[2] == (2023, 3, 1700.0)  # 2000 - 300


def test_get_monthly_cashflow_trend_limits_results(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    for month in range(1, 7):
        repo.add_transaction(
            Transaction(
                id=None,
                date=date(2023, month, 10),
                amount=-100.0,
                category="Food",
                description="Groceries",
            )
        )

    # Request only 3 most recent months
    trend = repo.get_monthly_cashflow_trend(3)

    assert len(trend) == 3
    # Should return the 3 most recent months ascending
    assert trend[0][1] == 4
    assert trend[1][1] == 5
    assert trend[2][1] == 6


def test_get_monthly_cashflow_trend_empty(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    trend = repo.get_monthly_cashflow_trend(6)
    assert trend == []


def test_get_all_transactions_pagination_offset_beyond_count(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )

    # Offset beyond available data
    result = repo.get_all_transactions(limit=100, offset=999)
    assert result == []


def test_get_all_transactions_limit_zero(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )

    result = repo.get_all_transactions(limit=0, offset=0)
    assert result == []


def test_search_by_keyword_offset_beyond_count(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=-50.0,
            category="Shopping",
            description="Amazon Order",
        )
    )

    result = repo.search_by_keyword("Amazon", limit=100, offset=999)
    assert result == []


def test_search_by_keyword_limit_zero(in_memory_repo):
    repo: TransactionRepository = in_memory_repo
    repo.add_transaction(
        Transaction(
            id=None,
            date=date.fromisoformat("2023-01-05"),
            amount=-50.0,
            category="Shopping",
            description="Amazon Order",
        )
    )

    result = repo.search_by_keyword("Amazon", limit=0, offset=0)
    assert result == []
