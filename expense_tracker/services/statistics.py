import logging
from typing import NamedTuple
from datetime import date

from expense_tracker.core.transaction_repository import TransactionRepository

logger = logging.getLogger(__name__)


class MonthlyMetrics(NamedTuple):
    """Monthly statistics metrics"""
    year: int
    month: int
    net_income: float
    top_category: str | None
    top_category_spending: float | None
    total_expenses: float
    transaction_count: int
    avg_transaction: float
    prev_month_expenses: float
    month_over_month_pct: float | None


class StatisticsService:
    """
    Service layer for transaction statistics and analytics.
    Combines repository calls to provide higher-level business logic.
    """

    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    @staticmethod
    def _get_month_date_range(year: int, month: int) -> tuple[date, date]:
        """Helper to get start and end date for a given month."""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        return start_date, end_date

    def get_monthly_metrics(self, year: int, month: int) -> MonthlyMetrics:
        """
        Get comprehensive monthly metrics by combining multiple repository queries.

        Returns:
            MonthlyMetrics with net income, top spending category, and additional stats
        """
        start_date, end_date = self._get_month_date_range(year, month)
        net_income = self.transaction_repo.get_monthly_net_income(start_date, end_date)
        top_category_data = self.transaction_repo.get_top_spending_category(start_date, end_date)

        if top_category_data:
            top_category, top_spending = top_category_data
        else:
            top_category, top_spending = None, None

        total_expenses = self.get_monthly_total_expense(year, month)
        transaction_count = self.get_monthly_transaction_count(year, month)
        avg_transaction = total_expenses / transaction_count if transaction_count > 0 else 0.0

        # Previous month calculations
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1
        prev_month_expenses = self.get_monthly_total_expense(prev_year, prev_month)

        if prev_month_expenses > 0:
            month_over_month_pct = ((total_expenses - prev_month_expenses) / prev_month_expenses) * 100
        else:
            month_over_month_pct = None

        return MonthlyMetrics(
            year=year,
            month=month,
            net_income=net_income,
            top_category=top_category,
            top_category_spending=top_spending,
            total_expenses=total_expenses,
            transaction_count=transaction_count,
            avg_transaction=avg_transaction,
            prev_month_expenses=prev_month_expenses,
            month_over_month_pct=month_over_month_pct,
        )

    def get_spending_heatmap_data(self, year: int, month: int) -> dict[int, float]:
        """
        Get daily spending data formatted for heatmap visualization.

        Returns:
            Dictionary mapping day (1-31) to spending amount
        """
        # Create date range for the month
        start_date, end_date = self._get_month_date_range(year, month)
        return self.transaction_repo.get_daily_spending_range(start_date, end_date)

    def get_available_months(self, expenses_only: bool = False) -> list[tuple[int, int]]:
        """
        Get list of months with transaction data.

        Args:
            expenses_only: If True, only return months with expenses

        Returns:
            List of (year, month) tuples
        """
        if expenses_only:
            return self.transaction_repo.get_months_with_expenses()
        return list(self.transaction_repo.get_all_months_with_data())

    def get_latest_available_month(self) -> tuple[int, int]:
        """
        Get the most recent month with transaction data.

        Returns:
            Tuple of (year, month)
        """
        return self.transaction_repo.get_latest_month_with_data()

    def get_cashflow_trend(self, num_months: int = 6) -> list[tuple[int, int, float]]:
        """
        Get cashflow trend for visualization.

        Args:
            num_months: Number of months to retrieve (default: 6)

        Returns:
            List of (year, month, net_amount) tuples
        """
        return self.transaction_repo.get_monthly_cashflow_trend(num_months)

    def get_yearly_heatmap_data(self, year: int) -> dict[str, float]:
        """
        Get daily spending data for a full year, formatted for heatmap visualization.

        Returns:
            Dictionary mapping ISO date string to spending amount
        """
        return self.transaction_repo.get_daily_spending_for_year(year)

    def get_available_years(self) -> list[int]:
        """
        Get list of years with expense data, sorted descending.

        Returns:
            List of years (e.g. [2024, 2023])
        """
        return self.transaction_repo.get_years_with_expenses()

    def get_monthly_total_expense(self, year: int, month: int) -> float:
        """
        Get total expenses for a given month.

        Returns:
            Total expense amount (positive value)
        """
        start_date, end_date = self._get_month_date_range(year, month)
        return self.transaction_repo.get_total_expense(start_date, end_date)
    
    def get_monthly_transaction_count(self, year: int, month: int) -> int:
        """
        Get total number of transactions for a given month.

        Returns:
            Total transaction count
        """
        start_date, end_date = self._get_month_date_range(year, month)
        return self.transaction_repo.get_transaction_count(start_date, end_date)