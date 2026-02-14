from datetime import date

import pytest

from expense_tracker.core.models import Transaction
from expense_tracker.core.transaction_repository import TransactionRepository
from expense_tracker.services.statistics import StatisticsService, MonthlyMetrics


@pytest.fixture
def in_memory_repo():
    """Provides an in-memory TransactionRepository for testing."""
    repo = TransactionRepository(":memory:")
    yield repo
    repo.conn.close()


@pytest.fixture
def statistics_service(in_memory_repo):
    """Provides a StatisticsService with an in-memory repository."""
    return StatisticsService(in_memory_repo)


def test_get_monthly_metrics_with_data(in_memory_repo, statistics_service):
    """Test get_monthly_metrics returns correct combined data."""
    # Add income and expenses for January 2023
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=2000.0,  # Income
            category="Income",
            description="Salary",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 10),
            amount=-500.0,  # Expense - Groceries
            category="Groceries",
            description="Whole Foods",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 15),
            amount=-300.0,  # Expense - Groceries
            category="Groceries",
            description="Trader Joes",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 20),
            amount=-100.0,  # Expense - Restaurants
            category="Restaurants",
            description="Dinner",
        )
    )

    metrics = statistics_service.get_monthly_metrics(2023, 1)

    assert isinstance(metrics, MonthlyMetrics)
    assert metrics.year == 2023
    assert metrics.month == 1
    assert metrics.net_income == 1100.0  # 2000 - 500 - 300 - 100
    assert metrics.top_category == "Groceries"
    assert metrics.top_category_spending == 800.0  # 500 + 300


def test_get_monthly_metrics_no_data(statistics_service):
    """Test get_monthly_metrics with no transactions."""
    metrics = statistics_service.get_monthly_metrics(2023, 1)

    assert metrics.year == 2023
    assert metrics.month == 1
    assert metrics.net_income == 0.0
    assert metrics.top_category is None
    assert metrics.top_category_spending is None


def test_get_monthly_metrics_only_income(in_memory_repo, statistics_service):
    """Test get_monthly_metrics with only income (no expenses)."""
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=1500.0,
            category="Income",
            description="Salary",
        )
    )

    metrics = statistics_service.get_monthly_metrics(2023, 1)

    assert metrics.net_income == 1500.0
    assert metrics.top_category is None  # No expenses
    assert metrics.top_category_spending is None


def test_get_spending_heatmap_data(in_memory_repo, statistics_service):
    """Test get_spending_heatmap_data returns daily spending."""
    # Add expenses for January 2023
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=-50.0,
            category="Food",
            description="Lunch",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=-30.0,
            category="Transport",
            description="Taxi",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 15),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )

    heatmap_data = statistics_service.get_spending_heatmap_data(2023, 1)

    assert isinstance(heatmap_data, dict)
    assert heatmap_data[5] == 80.0  # 50 + 30
    assert heatmap_data[15] == 100.0
    assert 10 not in heatmap_data


def test_get_available_months_all(in_memory_repo, statistics_service):
    """Test get_available_months returns all months with transactions."""
    # Add transactions for different months
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 2, 10),
            amount=1000.0,  # Income only
            category="Income",
            description="Salary",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 3, 15),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )

    months = statistics_service.get_available_months(expenses_only=False)

    assert len(months) == 3
    assert (2023, 1) in months
    assert (2023, 2) in months
    assert (2023, 3) in months


def test_get_available_months_expenses_only(in_memory_repo, statistics_service):
    """Test get_available_months with expenses_only filter."""
    # Add transactions for different months
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 2, 10),
            amount=1000.0,  # Income only - should be excluded
            category="Income",
            description="Salary",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 3, 15),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )

    months = statistics_service.get_available_months(expenses_only=True)

    assert len(months) == 2
    assert (2023, 1) in months
    assert (2023, 2) not in months  # Only income
    assert (2023, 3) in months


def test_get_latest_available_month(in_memory_repo, statistics_service):
    """Test get_latest_available_month returns most recent month."""
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 3, 15),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )

    year, month = statistics_service.get_latest_available_month()

    assert year == 2023
    assert month == 3


def test_get_latest_available_month_empty(statistics_service):
    """Test get_latest_available_month with no transactions defaults to current month."""
    year, month = statistics_service.get_latest_available_month()

    # Should default to current month
    today = date.today()
    assert year == today.year
    assert month == today.month


def test_get_yearly_heatmap_data(in_memory_repo, statistics_service):
    """Test get_yearly_heatmap_data returns daily spending keyed by ISO date."""
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 3, 15),
            amount=-75.0,
            category="Food",
            description="Groceries",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 3, 15),
            amount=-25.0,
            category="Transport",
            description="Taxi",
        )
    )

    data = statistics_service.get_yearly_heatmap_data(2023)

    assert isinstance(data, dict)
    assert data["2023-03-15"] == 100.0  # 75 + 25
    assert "2023-03-16" not in data


def test_get_available_years(in_memory_repo, statistics_service):
    """Test get_available_years returns years with expenses descending."""
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=-50.0,
            category="Food",
            description="Groceries",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2024, 6, 10),
            amount=-100.0,
            category="Shopping",
            description="Clothes",
        )
    )

    years = statistics_service.get_available_years()

    assert years == [2024, 2023]


def test_get_available_years_empty(statistics_service):
    """Test get_available_years with no data returns empty list."""
    years = statistics_service.get_available_years()
    assert years == []


def test_get_cashflow_trend(in_memory_repo, statistics_service):
    """Test get_cashflow_trend returns monthly net amounts."""
    # Add transactions for multiple months
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 5),
            amount=2000.0,
            category="Income",
            description="Salary",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 1, 10),
            amount=-500.0,
            category="Food",
            description="Groceries",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 2, 5),
            amount=2000.0,
            category="Income",
            description="Salary",
        )
    )
    in_memory_repo.add_transaction(
        Transaction(
            id=None,
            date=date(2023, 2, 10),
            amount=-800.0,
            category="Shopping",
            description="Clothes",
        )
    )

    trend = statistics_service.get_cashflow_trend(num_months=2)

    assert len(trend) == 2
    # Check January
    assert trend[0] == (2023, 1, 1500.0)  # 2000 - 500
    # Check February
    assert trend[1] == (2023, 2, 1200.0)  # 2000 - 800
