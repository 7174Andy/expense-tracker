import logging
import tkinter as tk
from tkinter import ttk, messagebox

from expense_tracker.core.transaction_repository import TransactionRepository
from expense_tracker.core.merchant_repository import MerchantCategoryRepository
from expense_tracker.services.merchant import MerchantCategoryService
from expense_tracker.utils.merchant_normalizer import normalize_merchant
from expense_tracker.gui.dialogs.expense_form import build_expense_form, validate_amount

logger = logging.getLogger(__name__)


class EditExpenseDialog(tk.Toplevel):
    def __init__(
        self,
        master,
        repo: TransactionRepository,
        merchant_repo: MerchantCategoryRepository,
        transaction_id: int,
    ):
        super().__init__(master)
        self.repo = repo
        self.merchant_repo = merchant_repo
        self.transaction_id = transaction_id
        self.merchant_service = MerchantCategoryService(
            merchant_repo, repo, normalize_merchant
        )
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
        self.prev_data = self.repo.get_transaction(self.transaction_id)
        if self.prev_data is not None:
            self.amount_var.set(str(self.prev_data.amount))
            self.category_var.set(self.prev_data.category)
            self.description_var.set(self.prev_data.description)

            # Only suggest category if the current category is "Uncategorized"
            if self.prev_data.category == "Uncategorized":
                suggested_category = self.merchant_repo.get_category(
                    normalize_merchant(self.prev_data.description)
                )
                if suggested_category:
                    self.category_var.set(suggested_category.category)

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
            self.repo.update_transaction(self.transaction_id, data)

            # Check if we need to update merchant categories
            if (
                self.prev_data is not None
                and self.prev_data.category != data["category"]
            ):
                try:
                    self.merchant_service.update_category(
                        self.prev_data.description, data["category"]
                    )
                    self.merchant_service.update_uncategorized_transactions()
                    messagebox.showinfo(
                        "Success",
                        f"Transaction {self.transaction_id} updated and related transactions recategorized.",
                    )
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Failed to update related transactions: {e}"
                    )
                self.destroy()
            else:
                # No category change, just close the dialog
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
