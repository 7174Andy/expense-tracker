from datetime import date
import tkinter as tk
from tkinter import messagebox

from expense_tracker.core.models import Transaction
from expense_tracker.services.transaction import TransactionService
from expense_tracker.gui.dialogs.expense_form import build_expense_form, validate_amount


class AddExpenseDialog(tk.Toplevel):
    def __init__(self, master, transaction_service: TransactionService):
        super().__init__(master)
        self.transaction_service = transaction_service
        self.title("Add Expense")
        self.resizable(False, False)

        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.description_var = tk.StringVar()

        build_expense_form(
            self,
            self.amount_var,
            self.category_var,
            self.description_var,
            submit_text="Add",
            on_submit=self._on_add,
            on_cancel=self._on_cancel,
        )
        self.bind("<Escape>", lambda e: self._on_cancel())

    def _on_add(self):
        amount = validate_amount(self.amount_var)
        if amount is None:
            return

        try:
            transaction = Transaction(
                id=None,
                date=date.today(),
                amount=amount,
                category=self.category_var.get() or "Uncategorized",
                description=self.description_var.get() or "",
            )
            saved_transaction = self.transaction_service.add_transaction(transaction)
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
