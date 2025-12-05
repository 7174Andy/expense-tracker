from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox

from expense_tracker.core.models import Transaction
from expense_tracker.core.transaction_repository import TransactionRepository


class AddExpenseDialog(tk.Toplevel):
    def __init__(self, master, repo: TransactionRepository):
        super().__init__(master)
        self.repo = repo
        self.title("Add Expense")
        self.resizable(False, False)

        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.description_var = tk.StringVar()

        self._build_form()

    def _build_form(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", padx=10, pady=10)

        # Amount
        ttk.Label(frame, text="Amount (e.g. 12.50):").grid(row=0, column=0, sticky="w")
        amount = ttk.Entry(frame, textvariable=self.amount_var, width=20)
        amount.grid(row=1, column=0, sticky="w")

        # Category
        ttk.Label(frame, text="Category:").grid(row=2, column=0, sticky="w")
        category = ttk.Entry(frame, textvariable=self.category_var, width=20)
        category.grid(row=3, column=0, sticky="w")

        # Description
        ttk.Label(frame, text="Description:").grid(row=4, column=0, sticky="w")
        description = ttk.Entry(frame, textvariable=self.description_var, width=20)
        description.grid(row=5, column=0, sticky="w")

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, pady=10, sticky="e")
        ttk.Button(button_frame, text="Add", command=self._on_add).pack(
            side="right", padx=5
        )
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(
            side="right"
        )

        # Keyboard bindings
        self.bind("<Escape>", lambda e: self._on_cancel())

    def _on_add(self):
        raw = self.amount_var.get()
        if not raw:
            messagebox.showerror("Error", "Amount is required.")
            return

        try:
            amount = float(raw)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number.")
            return

        try:
            transaction = Transaction(
                id=None,
                date=date.today(),
                amount=amount,
                category=self.category_var.get() or "Uncategorized",
                description=self.description_var.get() or "",
            )
            saved_transaction = self.repo.add_transaction(transaction)
            self.result = saved_transaction.id
            self.destroy()
            messagebox.showinfo(
                "Success", f"Transaction added with ID: {saved_transaction.id}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add transaction: {e}")
            return

    def _on_cancel(self):
        self.result = None
        self.destroy()
