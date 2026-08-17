import tkinter as tk
from tkinter import ttk, messagebox


def _highlight_dropdown_hover(combo: ttk.Combobox) -> None:
    """Make the hovered row in the dropdown list stand out.

    Tk already moves the listbox selection to the row under the cursor
    (ComboboxListbox <Motion> -> ttk::combobox::LBHover), but ttkbootstrap paints
    that selection #555555 on a #2f2f2f popdown, which is barely visible. Repaint
    it with the theme accent. The popdown is plain Tk, so it has to be configured
    per widget, after ttkbootstrap has styled it at construction.
    """
    try:
        from ttkbootstrap import Style

        accent = Style.get_instance().colors.primary
    except Exception:
        return  # no ttkbootstrap, no dark popdown to fix

    popdown = combo.tk.eval(f"ttk::combobox::PopdownWindow {combo}")
    combo.tk.call(f"{popdown}.f.l", "configure", "-selectbackground", accent)


def build_expense_form(
    parent: tk.Widget,
    amount_var: tk.StringVar,
    category_var: tk.StringVar,
    description_var: tk.StringVar,
    submit_text: str,
    on_submit,
    on_cancel,
    categories: list[str] | None = None,
) -> ttk.Frame:
    """Build the shared Amount/Category/Description form used by Add and Edit dialogs."""
    frame = ttk.Frame(parent)
    frame.pack(fill="both", padx=10, pady=10)

    # Amount
    ttk.Label(frame, text="Amount (e.g. 12.50):").grid(row=0, column=0, sticky="w")
    ttk.Entry(frame, textvariable=amount_var, width=20).grid(
        row=1, column=0, sticky="w"
    )

    # Category — editable so a new category can still be typed in
    ttk.Label(frame, text="Category:").grid(row=2, column=0, sticky="w")
    combo = ttk.Combobox(
        frame, textvariable=category_var, values=categories or [], width=18
    )
    combo.grid(row=3, column=0, sticky="w")
    _highlight_dropdown_hover(combo)

    # Description
    ttk.Label(frame, text="Description:").grid(row=4, column=0, sticky="w")
    ttk.Entry(frame, textvariable=description_var, width=20).grid(
        row=5, column=0, sticky="w"
    )

    # Buttons
    button_frame = ttk.Frame(frame)
    button_frame.grid(row=6, column=0, pady=10, sticky="e")
    ttk.Button(button_frame, text=submit_text, command=on_submit).pack(
        side="right", padx=5
    )
    ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side="right")

    return frame


def validate_amount(amount_var: tk.StringVar) -> float | None:
    """Validate and parse the amount field. Shows error messagebox on failure."""
    raw = amount_var.get()
    if not raw:
        messagebox.showerror("Error", "Amount is required.")
        return None
    try:
        return float(raw)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a valid number.")
        return None
