import tkinter as tk
from datetime import date
from tkinter import ttk

from expense_tracker.gui.tabs import TransactionsTab, HeatmapTab, StatisticsTab


class MainWindow(tk.Frame):
    def __init__(self, master, transaction_repo, merchant_repo, statistics_service):
        super().__init__(master)
        self.transaction_repo = transaction_repo
        self.merchant_repo = merchant_repo
        self.statistics_service = statistics_service
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

        # Create Statistics tab
        self.statistics_tab = StatisticsTab(self.notebook, statistics_service)

        # Create Heatmap tab
        self.heatmap_tab = HeatmapTab(self.notebook, statistics_service, self)

        # Add tabs to notebook
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.notebook.add(self.statistics_tab, text="Statistics")
        self.notebook.add(self.heatmap_tab, text="Heatmap")

        # Bind tab change event for lazy loading
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

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

    def _on_tab_changed(self, event):
        """Refresh tab content when user switches tabs."""
        current_tab = self.notebook.select()
        tab_index = self.notebook.index(current_tab)
        if tab_index == 1:  # Statistics tab
            self.statistics_tab.refresh()
        elif tab_index == 2:  # Heatmap tab
            self.heatmap_tab.refresh()

    def show_transactions_for_date(self, target_date: date):
        """Switch to Transactions tab with date filter applied."""
        self.notebook.select(0)  # Switch to Transactions tab (index 0)
        self.transactions_tab.filter_by_date(target_date)
