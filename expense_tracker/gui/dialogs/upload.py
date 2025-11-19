import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

from expense_tracker.core.model import Transaction
from expense_tracker.core.repository import TransactionRepository
from expense_tracker.utils.extract import parse_bofa_statement_pdf

class UploadDialog(tk.Toplevel):
    def __init__(self, master, repo: TransactionRepository):
        super().__init__(master)
        self.repo = repo
        self.title("Upload Bank Statement")
        self.resizable(False, False)

        self.file_var = tk.StringVar()

        self._build_form()

    def _build_form(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", padx=10, pady=10)

        # File selection
        ttk.Label(frame, text="Select PDF File:").grid(row=0, column=0, sticky="w")
        file_entry = ttk.Entry(frame, textvariable=self.file_var, width=40)
        file_entry.grid(row=1, column=0, sticky="w")
        ttk.Button(frame, text="Browse", command=self._browse_file).grid(row=1, column=1, padx=5)

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="e")
        ttk.Button(button_frame, text="Upload", command=self._on_upload).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side=tk.LEFT, padx=5)
    
    def _browse_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.file_var.set(file_path)

    def _on_upload(self):
        file_path = self.file_var.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a PDF file to upload.")
            return

        try:
            transactions = parse_bofa_statement_pdf(file_path)
            for t in transactions:
                transaction = Transaction(
                    id=None,
                    date=self._parse_date(t["date"]),
                    amount=t["amount"],
                    category="Uncategorized",
                    description=t["description"],
                )
                self.repo.add_transaction(transaction)
            messagebox.showinfo("Success", "Bank statement uploaded successfully.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload bank statement: {e}")

    def _on_cancel(self):
        self.file_var.set("")
        self.destroy()

    def _parse_date(self, raw_date) -> date:
        if isinstance(raw_date, date):
            return raw_date
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
            try:
                return datetime.strptime(raw_date, fmt).date()
            except (ValueError, TypeError):
                continue
        raise ValueError(f"Unsupported date format: {raw_date}")
