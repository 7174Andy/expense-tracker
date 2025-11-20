import logging
import tkinter as tk
from tkinter import ttk, messagebox
from expense_tracker.core.repositories import TransactionRepository, MerchantCategoryRepository
from expense_tracker.services.marchant import MerchantCategoryService
from expense_tracker.utils.merchant_normalizer import normalize_merchant

logger = logging.getLogger(__name__)

class EditExpenseDialog(tk.Toplevel):
    def __init__(self, master, repo: TransactionRepository, merchant_repo: MerchantCategoryRepository, transaction_id: int):
        super().__init__(master)
        self.repo = repo
        self.merchant_repo = merchant_repo
        self.transaction_id = transaction_id
        self.merchant_service = MerchantCategoryService(merchant_repo, repo, normalize_merchant)
        self.title("Edit Expense")
        self.resizable(False, False)

        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.description_var = tk.StringVar()
        
        self.progress_frame = ttk.Frame(self)
        self.progress_frame.pack(fill="x", padx=10, pady=5)
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack(side="left", padx=5)
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')

        self.prev_data = None

        self._build_form()
        self._load_transaction_data()

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
        ttk.Button(button_frame, text="Save", command=self._on_save).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side="right")

        # Keyboard bindings
        self.bind("<Escape>", lambda e: self._on_cancel())

    def show_progress(self, message):
        """Show progress bar and message"""
        self.progress_label.config(text=message)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=5)
        self.progress_bar.start(10)

    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_label.config(text="")

    def _load_transaction_data(self):
        self.prev_data = self.repo.get_transaction(self.transaction_id)
        if self.prev_data is not None:
            self.amount_var.set(str(self.prev_data.amount))
            self.category_var.set(self.prev_data.category)
            self.description_var.set(self.prev_data.description)

            # Only suggest category if the current category is "Uncategorized"
            if self.prev_data.category == "Uncategorized":
                suggested_category = self.merchant_repo.get_category(normalize_merchant(self.prev_data.description))
                if suggested_category:
                    self.category_var.set(suggested_category.category)

    def _on_save(self):
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
            data = {
                "amount": amount,
                "category": self.category_var.get() or "Uncategorized",
                "description": self.description_var.get() or ""
            }
            self.repo.update_transaction(self.transaction_id, data)
            if self.prev_data is not None and self.prev_data.category != data["category"]:
                self.merchant_service.update_category(self.prev_data.description, data["category"])

                self.merchant_service.update_uncategorized_transactions()
            self.result = self.transaction_id
            self.destroy()
            messagebox.showinfo("Success", f"Transaction {self.transaction_id} updated.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update transaction: {e}")
            return
    
    def _on_cancel(self):
        self.result = None
        self.destroy()
