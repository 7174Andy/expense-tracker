from tkinter import Tk, ttk
from expense_tracker.gui.main_window import MainWindow

from expense_tracker.version import versions
from expense_tracker.utils.path import get_database_path
from expense_tracker.utils.migration import migrate_legacy_databases
from expense_tracker.core.merchant_repository import MerchantCategoryRepository
from expense_tracker.core.transaction_repository import TransactionRepository
from expense_tracker.services.merchant import MerchantCategoryService
from expense_tracker.services.transaction import TransactionService
from expense_tracker.services.statistics import StatisticsService
from expense_tracker.utils.merchant_normalizer import normalize_merchant

def main():
    """Start the Expense Tracker application."""

    versions()

    # Migrate legacy databases if they exist
    migrate_legacy_databases()

    # Use platform-specific data directory for databases
    print("Using data directory for databases.")
    print(f" - Transactions DB: {get_database_path('transactions.db')}")
    print(f" - Merchant Categories DB: {get_database_path('merchant_categories.db')}")
    transaction_repo = TransactionRepository(str(get_database_path("transactions.db")))
    merchant_repo = MerchantCategoryRepository(
        str(get_database_path("merchant_categories.db"))
    )
    merchant_service = MerchantCategoryService(
        merchant_repo, transaction_repo, normalize_merchant
    )
    transaction_service = TransactionService(transaction_repo, merchant_service)
    statistics_service = StatisticsService(transaction_repo)

    root = Tk()
    root.title("Expense Tracker")
    root.geometry("1200x700")
    try:
        import ttkbootstrap as tb

        tb.Style("darkly")
    except Exception:
        ttk.Style()
    MainWindow(root, transaction_repo, transaction_service, statistics_service)
    root.focus_force()
    root.mainloop()
