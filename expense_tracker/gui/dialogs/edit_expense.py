import logging
import tkinter as tk
from tkinter import ttk, messagebox

from expense_tracker.services.transaction import TransactionService
from expense_tracker.gui.dialogs.expense_form import build_expense_form, validate_amount

logger = logging.getLogger(__name__)


class EditExpenseDialog(tk.Toplevel):
    def __init__(
        self,
        master,
        transaction_service: TransactionService,
        transaction_id: int,
    ):
        super().__init__(master)
        self.transaction_service = transaction_service
        self.transaction_id = transaction_id
        self.title("Edit Expense")
        self.resizable(False, False)

        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.description_var = tk.StringVar()

        self.progress_frame = ttk.Frame(self)
        self.progress_frame.pack(fill="x", padx=10, pady=5)
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack(side="left", padx=5)
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode="indeterminate")

        self.prev_data = None

        build_expense_form(
            self,
            self.amount_var,
            self.category_var,
            self.description_var,
            submit_text="Save",
            on_submit=self._on_save,
            on_cancel=self._on_cancel,
        )
        self.bind("<Escape>", lambda e: self._on_cancel())

        self._load_transaction_data()

    def _load_transaction_data(self):
        self.prev_data = self.transaction_service.get_transaction(self.transaction_id)
        if self.prev_data is not None:
            self.amount_var.set(str(self.prev_data.amount))
            self.category_var.set(self.prev_data.category)
            self.description_var.set(self.prev_data.description)

            # Suggest a better category if currently uncategorized
            if self.prev_data.category == "Uncategorized":
                suggested = self.transaction_service.suggest_category(
                    self.prev_data.description, self.prev_data.amount
                )
                if suggested != "Uncategorized":
                    self.category_var.set(suggested)

    def _on_save(self):
        amount = validate_amount(self.amount_var)
        if amount is None:
            return

        try:
            data = {
                "amount": amount,
                "category": self.category_var.get() or "Uncategorized",
                "description": self.description_var.get() or "",
            }

            categories_updated = self.transaction_service.update_transaction(
                self.transaction_id, data
            )

            if categories_updated:
                messagebox.showinfo(
                    "Success",
                    f"Transaction {self.transaction_id} updated and related transactions recategorized.",
                )
            else:
                self.result = self.transaction_id
                messagebox.showinfo(
                    "Success", f"Transaction {self.transaction_id} updated."
                )
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update transaction: {e}")
            return

    def _on_cancel(self):
        self.result = None
        self.destroy()
