from expense_tracker.core.repository import TransactionRepository, MerchantCategoryRepository
from tkinter import Tk, ttk
from gui.main_window import MainWindow
from expense_tracker.version import versions

def main():
    # Get the absolute path to the database file
    transaction_repo = TransactionRepository("expense_tracker/data/transactions.db")
    merchant_repo = MerchantCategoryRepository("expense_tracker/data/merchant_categories.db")
    root = Tk()
    root.title("Expense Tracker")
    root.geometry("1100x600")
    try:
        import ttkbootstrap as tb
        tb.Style("darkly")
    except Exception:
        ttk.Style()
    MainWindow(root, transaction_repo, merchant_repo)
    root.mainloop()



if __name__ == "__main__":
    versions()
    main()
