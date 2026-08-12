import tkinter as tk
from tkinter import ttk, messagebox

from expense_tracker.core.models import Transaction
from expense_tracker.services.transaction import TransactionService
from expense_tracker.utils.extract import parse_statement


class UploadDialog(tk.Toplevel):
    def __init__(self, master, transaction_service: TransactionService):
        super().__init__(master)
        self.transaction_service = transaction_service
        self.title("Upload Bank Statement")
        self.resizable(False, False)

        self.file_var = tk.StringVar()
        self.summary_var = tk.StringVar(value="Select a statement, then preview it.")
        self.parsed: list[dict] = []

        self._build_form()

    def _build_form(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", padx=10, pady=10)

        # File selection
        ttk.Label(frame, text="Select PDF File:").grid(row=0, column=0, sticky="w")
        file_entry = ttk.Entry(frame, textvariable=self.file_var, width=40)
        file_entry.grid(row=1, column=0, sticky="w")
        ttk.Button(frame, text="Browse", command=self._browse_file).grid(
            row=1, column=1, padx=5
        )
        self.preview_button = ttk.Button(
            frame, text="Preview", command=self._on_preview
        )
        self.preview_button.grid(row=1, column=2, padx=5)

        # Parsed transactions, reviewed before anything is written
        ttk.Label(frame, textvariable=self.summary_var).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(10, 2)
        )
        self.tree = ttk.Treeview(
            frame,
            columns=("date", "description", "amount"),
            show="headings",
            height=12,
        )
        for col, text, width, anchor in (
            ("date", "Date", 90, "w"),
            ("description", "Description", 340, "w"),
            ("amount", "Amount", 90, "e"),
        ):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor)
        self.tree.grid(row=3, column=0, columnspan=3, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=3, column=3, sticky="ns")

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky="e")
        self.import_button = ttk.Button(
            button_frame, text="Import", command=self._on_import, state="disabled"
        )
        self.import_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(
            side=tk.LEFT, padx=5
        )

    def _browse_file(self):
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.file_var.set(file_path)

    def _reset_preview(self):
        self.parsed = []
        self.tree.delete(*self.tree.get_children())
        self.import_button.configure(state="disabled")

    def _on_preview(self):
        """Parse and show the transactions. Nothing is written to the database."""
        file_path = self.file_var.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a PDF file to upload.")
            return

        self._reset_preview()
        try:
            profile_name, parsed = parse_statement(file_path)
        except Exception as e:
            self.summary_var.set("Could not read the statement.")
            messagebox.showerror("Error", f"Failed to read bank statement: {e}")
            return

        if not parsed:
            self.summary_var.set(f"{profile_name}: no transactions found.")
            messagebox.showinfo(
                "No Transactions",
                "No transactions were found in this statement. Nothing was imported.",
            )
            return

        for t in parsed:
            self.tree.insert(
                "",
                "end",
                values=(t["date"], t["description"], f"{t['amount']:,.2f}"),
            )
        total = sum(t["amount"] for t in parsed)
        self.summary_var.set(
            f"{profile_name}: {len(parsed)} transaction(s), total {total:,.2f}. "
            "Review before importing."
        )
        self.parsed = parsed
        self.import_button.configure(state="normal")

    def _on_import(self):
        if not self.parsed:
            return
        try:
            transactions = [
                Transaction(
                    id=None,
                    date=t["date"],
                    amount=t["amount"],
                    category="Uncategorized",
                    description=t["description"],
                )
                for t in self.parsed
            ]
            imported = self.transaction_service.import_transactions(transactions)
            messagebox.showinfo(
                "Success",
                f"Imported {imported} transaction(s) from bank statement.",
            )
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import bank statement: {e}")

    def _on_cancel(self):
        self.file_var.set("")
        self._reset_preview()
        self.destroy()
