import tkinter as tk
from tkinter import ttk

from expense_tracker.gui.tabs import TransactionsTab


class MainWindow(tk.Frame):
    def __init__(self, master, transaction_repo, merchant_repo):
        super().__init__(master)
        self.transaction_repo = transaction_repo
        self.merchant_repo = merchant_repo
        self.master = master
        self._active_dialog: tk.Toplevel | None = None

        self.pack(fill=tk.BOTH, expand=True)

        # Create notebook (tab container)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create Transactions tab
        self.transactions_tab = TransactionsTab(
            self.notebook, transaction_repo, merchant_repo, self
        )

        # Add tab to notebook
        self.notebook.add(self.transactions_tab, text="Transactions")

    def _open_dialog(self, dialog_class, *args, **kwargs):
        if self._active_dialog is not None and self._active_dialog.winfo_exists():
            self._active_dialog.lift()
            self._active_dialog.focus_set()
            return

        # Create a new dialog
        dialog = dialog_class(self.master, *args, **kwargs)
        self._active_dialog = dialog

        # Close handler
        def on_close():
            if dialog.winfo_exists():
                dialog.destroy()
            self._active_dialog = None
            self.transactions_tab.refresh()

        dialog.protocol("WM_DELETE_WINDOW", on_close)
        dialog.transient(self.master)
        dialog.grab_set()

        self.master.wait_window(dialog)

        self._active_dialog = None
        self.transactions_tab.refresh()
