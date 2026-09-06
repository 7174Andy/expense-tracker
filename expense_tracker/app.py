from tkinter import Tk, ttk
from expense_tracker.gui.main_window import MainWindow

from expense_tracker.version import versions
from expense_tracker.utils.path import get_database_path
from expense_tracker.utils.migration import migrate_legacy_databases
from expense_tracker.core.merchant_repository import MerchantCategoryRepository
from expense_tracker.core.transaction_repository import TransactionRepository
from expense_tracker.services.merchant import MerchantCategoryService
from expense_tracker.services.transaction import TransactionService
from expense_tracker.services.statistics import StatisticsService
from expense_tracker.utils.merchant_normalizer import normalize_merchant

def _fix_combobox_arrow(style) -> None:
    """Patch two ttkbootstrap 1.18 Combobox arrow quirks.

    The arrow is an image element. Its sticky="s" parks it on the bottom edge
    of the field instead of the centerline, and its focus/hover/pressed image
    is drawn in colors.primary (#375a7f on darkly), which is invisible against
    the readonly field background (#555555). Swap in an arrow element that
    keeps the input foreground color in every enabled state, centered on the
    field edge.
    """
    style.configure("TCombobox")  # force ttkbootstrap's lazy style build
    builder = style._get_builder()
    colors = style.colors
    disabled = colors.border if builder.is_light_theme else colors.selectbg
    # (color, direction) grid of image names; rows: normal/disabled/active
    arrows = builder.create_simple_arrow_assets(colors.inputfg, disabled, colors.inputfg)
    style.element_create(
        "Combobox.downarrow.visible",
        "image",
        arrows[0][1],
        ("disabled", arrows[1][1]),
    )
    style.layout("TCombobox", _use_visible_downarrow(style.layout("TCombobox")))


def _use_visible_downarrow(elements):
    """Rewrite a Combobox layout to use the always-visible arrow element."""
    fixed = []
    for name, opts in elements:
        if name == "Combobox.downarrow":
            name = "Combobox.downarrow.visible"
            opts["sticky"] = "e"
        if "children" in opts:
            opts["children"] = _use_visible_downarrow(opts["children"])
        fixed.append((name, opts))
    return fixed


def main():
    """Start the Expense Tracker application."""

    versions()

    # Migrate legacy databases if they exist
    migrate_legacy_databases()

    # Use platform-specific data directory for databases
    print("Using data directory for databases.")
    print(f" - Transactions DB: {get_database_path('transactions.db')}")
    print(f" - Merchant Categories DB: {get_database_path('merchant_categories.db')}")
    transaction_repo = TransactionRepository(str(get_database_path("transactions.db")))
    merchant_repo = MerchantCategoryRepository(
        str(get_database_path("merchant_categories.db"))
    )
    merchant_service = MerchantCategoryService(
        merchant_repo, transaction_repo, normalize_merchant
    )
    transaction_service = TransactionService(transaction_repo, merchant_service)
    statistics_service = StatisticsService(transaction_repo)

    root = Tk()
    root.title("Expense Tracker")
    root.geometry("1200x700")
    try:
        import ttkbootstrap as tb

        _fix_combobox_arrow(tb.Style("darkly"))
    except Exception:
        ttk.Style()
    MainWindow(root, transaction_repo, transaction_service, statistics_service)
    root.focus_force()
    root.mainloop()
