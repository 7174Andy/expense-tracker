import math
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox

from expense_tracker.core.repositories import TransactionRepository
from expense_tracker.gui.dialogs.add_expense import AddExpenseDialog
from expense_tracker.gui.dialogs.edit_expense import EditExpenseDialog
from expense_tracker.gui.dialogs.upload import UploadDialog


class TransactionsTab(tk.Frame):
    def __init__(self, master, transaction_repo, merchant_repo, main_window):
        super().__init__(master)
        self.transaction_repo: TransactionRepository = transaction_repo
        self.merchant_repo = merchant_repo
        self.main_window = main_window
        self._current_page = 0
        self._page_size = 100
        self._total_transactions = 0
        self._search_keyword: str | None = None
        self._filter_date: date | None = None

        self.pack(fill=tk.BOTH, expand=True)
        self._build_toolbar()
        self._build_body()
        self._build_footer()
        self.refresh()

    def _build_body(self):
        self.tree = ttk.Treeview(
            self,
            columns=("id", "date", "amount", "category", "description"),
            show="headings",
        )
        self.tree.heading("date", text="Date")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("category", text="Category")
        self.tree.heading("description", text="Description")

        # Set column widths
        self.tree.column("date", width=100, anchor=tk.W, stretch=tk.NO)
        self.tree.column("amount", width=100, anchor=tk.W, stretch=tk.NO)
        self.tree.column("category", width=150, anchor=tk.W, stretch=tk.NO)
        self.tree.column("description", width=300, anchor=tk.W)

        self.tree.column("id", width=0, stretch=tk.NO)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind events
        self.tree.bind("<Double-1>", lambda e: self._edit_transaction())

    def _build_footer(self):
        footer = tk.Frame(self)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        self.prev_button = ttk.Button(
            footer, text="Previous", command=self._previous_page
        )
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.page_label = ttk.Label(footer, text="")
        self.page_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.next_button = ttk.Button(footer, text="Next", command=self._next_page)
        self.next_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.search_indicator = ttk.Label(footer, text="", foreground="white")
        self.search_indicator.pack(side=tk.RIGHT, padx=5, pady=5)

    def _previous_page(self):
        if self._current_page > 0:
            self._current_page -= 1
            self.refresh()

    def _next_page(self):
        self._current_page += 1
        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        offset = self._current_page * self._page_size

        # Use date filter if active, otherwise use search/all transactions
        if self._filter_date:
            transactions = self.transaction_repo.get_transactions_for_date(
                self._filter_date
            )
            self._total_transactions = len(transactions)
            self.search_indicator.config(
                text=f"Filtered by date: {self._filter_date.isoformat()}"
            )
        elif self._search_keyword:
            self._total_transactions = self.transaction_repo.count_search_results(
                self._search_keyword
            )
            transactions = self.transaction_repo.search_by_keyword(
                self._search_keyword,
                limit=self._page_size,
                offset=offset,
            )
            self.search_indicator.config(text=f"Search: {self._search_keyword}")
        else:
            self._total_transactions = self.transaction_repo.count_all_transactions()
            transactions = self.transaction_repo.get_all_transactions(
                limit=self._page_size,
                offset=offset,
            )
            self.search_indicator.config(text="")

        for transaction in transactions:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    transaction.id,
                    transaction.date.isoformat(),
                    transaction.amount,
                    transaction.category,
                    transaction.description,
                ),
            )

        total_pages = (
            math.ceil(self._total_transactions / self._page_size)
            if self._total_transactions > 0
            else 1
        )
        self.page_label.config(text=f"Page {self._current_page + 1} of {total_pages}")

        self.prev_button.config(
            state=tk.NORMAL if self._current_page > 0 else tk.DISABLED
        )
        self.next_button.config(
            state=tk.NORMAL
            if offset + self._page_size < self._total_transactions
            else tk.DISABLED
        )

    def _build_toolbar(self):
        bar = tk.Frame(self)
        bar.pack(fill=tk.X)
        ttk.Button(bar, text="Add Transaction", command=self._add_transaction).pack(
            side=tk.LEFT, padx=5, pady=5
        )
        ttk.Button(bar, text="Edit Transaction", command=self._edit_transaction).pack(
            side=tk.LEFT, padx=5, pady=5
        )
        ttk.Button(
            bar, text="Delete Transaction", command=self._delete_transaction
        ).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(bar, text="Refresh", command=self.refresh).pack(
            side=tk.LEFT, padx=5, pady=5
        )
        ttk.Button(bar, text="Import Statement", command=self._upload_statement).pack(
            side=tk.RIGHT, padx=5, pady=5
        )
        self.qvar = tk.StringVar()
        search_entry = ttk.Entry(bar, textvariable=self.qvar, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, pady=5)
        search_entry.bind("<Return>", lambda _: self._search_transactions())
        ttk.Button(bar, text="Search", command=self._search_transactions).pack(
            side=tk.LEFT, padx=5, pady=5
        )
        ttk.Button(bar, text="Clear Search", command=self._clear_search).pack(
            side=tk.LEFT, padx=5, pady=5
        )

    def _get_selected_ids(self) -> list[int]:
        ids = []
        for item in self.tree.selection():
            item_data = self.tree.item(item, "values")
            if item_data:
                ids.append(int(item_data[0]))
        return ids

    def _upload_statement(self):
        self.main_window._open_dialog(
            UploadDialog, self.transaction_repo, self.merchant_repo
        )

    def _add_transaction(self):
        self.main_window._open_dialog(AddExpenseDialog, self.transaction_repo)

    def _edit_transaction(self):
        transaction_ids = self._get_selected_ids()
        if not transaction_ids:
            messagebox.showwarning(
                "No selection", "Please select a transaction to edit."
            )
            return

        if len(transaction_ids) > 1:
            messagebox.showwarning(
                "Multiple Selection", "Please select only one transaction to edit."
            )
            return

        self.main_window._open_dialog(
            EditExpenseDialog,
            self.transaction_repo,
            self.merchant_repo,
            transaction_ids[0],
        )

    def _delete_transaction(self):
        transaction_ids = self._get_selected_ids()

        if not transaction_ids:
            messagebox.showwarning(
                "No selection", "Please select a transaction to delete."
            )
            return

        confirm = messagebox.askyesno(
            "Delete Transaction",
            "Are you sure you want to delete the selected transaction?",
        )

        if confirm:
            deleted = self.transaction_repo.delete_multiple_transactions(
                transaction_ids
            )
            messagebox.showinfo(
                "Success", f"Deleted {deleted} transaction(s) successfully."
            )
            self.refresh()

    def _search_transactions(self):
        keyword = self.qvar.get().strip()
        # Empty search clears the search
        if not keyword:
            self._clear_search()
            return

        self._search_keyword = keyword
        self._current_page = 0  # Reset to first page
        self.refresh()

    def _clear_search(self):
        self._search_keyword = None
        self._filter_date = None  # Also clear date filter
        self.qvar.set("")  # Clear the search entry field
        self._current_page = 0  # Reset to first page
        self.refresh()

    def filter_by_date(self, target_date: date):
        """Filter transactions by a specific date."""
        self._filter_date = target_date
        self._search_keyword = None  # Clear search when filtering by date
        self.qvar.set("")  # Clear the search entry field
        self._current_page = 0  # Reset to first page
        self.refresh()
