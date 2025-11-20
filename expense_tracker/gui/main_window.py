import math
import tkinter as tk
from tkinter import ttk, messagebox

from expense_tracker.core.repositories import TransactionRepository
from expense_tracker.gui.dialogs.add_expense import AddExpenseDialog
from expense_tracker.gui.dialogs.edit_expense import EditExpenseDialog
from expense_tracker.gui.dialogs.upload import UploadDialog


class MainWindow(tk.Frame):
    def __init__(self, master, transaction_repo, merchant_repo):
        super().__init__(master)
        self.transaction_repo: TransactionRepository = transaction_repo
        self.merchant_repo = merchant_repo
        self.master = master
        self._active_dialog: tk.Toplevel | None = None
        self._current_page = 0
        self._page_size = 100
        self._total_transactions = 0
        self.pack(fill=tk.BOTH, expand=True)
        self._build_toolbar()
        self._build_body()
        self._build_footer()
        self.refresh()


    def _build_body(self):
        self.tree = ttk.Treeview(self, columns=("id", "date", "amount", "category", "description"), show="headings")
        self.tree.heading("date", text="Date")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("category", text="Category")
        self.tree.heading("description", text="Description")
        self.tree.column("id", width=0, stretch=tk.NO)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind events
        self.tree.bind('<Double-1>', lambda e: self._edit_transaction())

    def _build_footer(self):
        footer = tk.Frame(self)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        self.prev_button = ttk.Button(footer, text="Previous", command=self._previous_page)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.page_label = ttk.Label(footer, text="")
        self.page_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.next_button = ttk.Button(footer, text="Next", command=self._next_page)
        self.next_button.pack(side=tk.LEFT, padx=5, pady=5)

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
        
        self._total_transactions = self.transaction_repo.count_all_transactions()
        offset = self._current_page * self._page_size
        
        transactions = self.transaction_repo.get_all_transactions(
            limit=self._page_size,
            offset=offset,
        )

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
        
        total_pages = math.ceil(self._total_transactions / self._page_size)
        self.page_label.config(text=f"Page {self._current_page + 1} of {total_pages}")

        self.prev_button.config(state=tk.NORMAL if self._current_page > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if offset + self._page_size < self._total_transactions else tk.DISABLED)
    
    def _build_toolbar(self):
        bar = tk.Frame(self)
        bar.pack(fill=tk.X)
        ttk.Button(bar, text="Add Transaction", command=self._add_transaction).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(bar, text="Edit Transaction", command=self._edit_transaction).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(bar, text="Delete Transaction", command=self._delete_transaction).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(bar, text="Refresh", command=self.refresh).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(bar, text="Import Statement", command=self._upload_statement).pack(side=tk.RIGHT, padx=5, pady=5)
        self.qvar = tk.StringVar()
        ttk.Entry(bar, textvariable=self.qvar, width=30).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(bar, text="Search", command=self._search_transactions).pack(side=tk.LEFT, padx=5, pady=5)
        

    def _get_selected_ids(self) -> list[int]:
        ids = []
        for item in self.tree.selection():
            item_data = self.tree.item(item, "values")
            if item_data:
                ids.append(int(item_data[0]))
        return ids

    def _upload_statement(self):
        self._open_dialog(UploadDialog, self.transaction_repo, self.merchant_repo)

    def _add_transaction(self):
        self._open_dialog(AddExpenseDialog, self.transaction_repo)

    def _edit_transaction(self):
        transaction_ids = self._get_selected_ids()
        if not transaction_ids:
            messagebox.showwarning("No selection", "Please select a transaction to edit.")
            return
        
        if len(transaction_ids) > 1:
            messagebox.showwarning("Multiple Selection", "Please select only one transaction to edit.")
            return
        
        self._open_dialog(EditExpenseDialog, self.transaction_repo, self.merchant_repo, transaction_ids[0])
    
    def _delete_transaction(self):
        transaction_ids = self._get_selected_ids()

        if not transaction_ids:
            messagebox.showwarning("No selection", "Please select a transaction to delete.")
            return
        
        confirm = messagebox.askyesno(
            "Delete Transaction", 
            "Are you sure you want to delete the selected transaction?"
        )

        if confirm:
            deleted = self.transaction_repo.delete_multiple_transactions(transaction_ids)
            messagebox.showinfo("Success", f"Deleted {deleted} transaction(s) successfully.")
            self.refresh()

    def _search_transactions(self):
        query = self.qvar.get()
        messagebox.showinfo("Search Transactions", f"Search for: {query}")
    
    def _open_dialog(self, dialog_class, *args, **kwargs):
        if self._active_dialog is not None and self._active_dialog.winfo_exists():
            self._active_dialog.lift()
            self._active_dialog.focus_set()
            return

        # Create a new dialog
        dialog = dialog_class(self.master, *args, **kwargs)
        self._active_dialog = dialog

        # Cloas handler
        def on_close():
            if dialog.winfo_exists():
                dialog.destroy()
            self._active_dialog = None
            self.refresh()
        
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        dialog.transient(self.master)
        dialog.grab_set()

        self.master.wait_window(dialog)

        self._active_dialog = None
        self.refresh()
