import tkinter as tk
from tkinter import ttk

from expense_tracker.gui.dialogs.expense_form import _highlight_dropdown_hover

ALL_CATEGORIES = "All Categories"


class FilterDialog(tk.Toplevel):
    """Modal for picking transaction table filters.

    Future filter dimensions (date, amount, ...) each add a row to the form.
    """

    def __init__(
        self,
        master,
        categories: list[str],
        current_category: str | None,
        on_apply,
    ):
        super().__init__(master)
        self.on_apply = on_apply
        self.title("Filter Transactions")
        self.resizable(False, False)

        frame = ttk.Frame(self)
        frame.pack(fill="both", padx=10, pady=10)

        ttk.Label(frame, text="Category:").grid(row=0, column=0, sticky="w")
        self.category_var = tk.StringVar(value=current_category or ALL_CATEGORIES)
        combo = ttk.Combobox(
            frame,
            textvariable=self.category_var,
            values=[ALL_CATEGORIES] + categories,
            state="readonly",
            width=18,
        )
        combo.grid(row=1, column=0, sticky="w")
        _highlight_dropdown_hover(combo)

        buttons = ttk.Frame(frame)
        buttons.grid(row=2, column=0, pady=10, sticky="e")
        ttk.Button(buttons, text="Apply", command=self._on_apply).pack(
            side="right", padx=5
        )
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right")
        self.bind("<Escape>", lambda e: self.destroy())

    def _on_apply(self):
        selected = self.category_var.get()
        self.on_apply(None if selected == ALL_CATEGORIES else selected)
        self.destroy()
