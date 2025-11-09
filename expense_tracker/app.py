from expense_tracker.core.repository import TransactionRepository
from tkinter import Tk, ttk
from gui.main_window import MainWindow
from expense_tracker.version import versions

def main():
    # Get the absolute path to the database file
    repo = TransactionRepository("expense_tracker/data/transactions.db")
    root = Tk()
    root.title("Expense Tracker")
    root.geometry("1100x600")
    try:
        import ttkbootstrap as tb
        tb.Style("darkly")
    except Exception:
        ttk.Style()
    MainWindow(root, repo)
    root.mainloop()



if __name__ == "__main__":
    versions()
    main()
