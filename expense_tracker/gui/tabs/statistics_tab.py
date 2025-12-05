import calendar
import tkinter as tk
from tkinter import ttk

from expense_tracker.core.transaction_repository import TransactionRepository


class StatisticsTab(tk.Frame):
    def __init__(self, master, transaction_repo: TransactionRepository):
        super().__init__(master)
        self.transaction_repo: TransactionRepository = transaction_repo

        # State: the latest month and year where the record is available
        latest_year, latest_month = self.transaction_repo.get_latest_month_with_data()
        self._current_year = latest_year
        self._current_month = latest_month

        # Cache all months with data for navigation button state management
        self._months_with_data = self.transaction_repo.get_all_months_with_data()

        self.pack(fill=tk.BOTH, expand=True)

        # Build UI
        self._build_header()
        self._build_metrics_cards()

    def _build_header(self):
        """Build header with month navigation controls."""
        header = tk.Frame(self)
        header.pack(fill=tk.X, padx=20, pady=15)

        # Previous month button
        self.prev_button = ttk.Button(
            header, text="<", command=self._previous_month, width=3
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)

        # Month/Year label
        self.month_label = ttk.Label(header, text="", font=("Arial", 20, "bold"))
        self.month_label.pack(side=tk.LEFT, expand=True)

        # Next month button
        self.next_button = ttk.Button(
            header, text=">", command=self._next_month, width=3
        )
        self.next_button.pack(side=tk.RIGHT, padx=5)

        self._update_header_label()

    def _build_metrics_cards(self):
        """Build card-based layout for displaying metrics."""
        # Container for metrics cards
        cards_container = tk.Frame(self)
        cards_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Configure grid to center cards
        cards_container.grid_columnconfigure(0, weight=1)
        cards_container.grid_columnconfigure(1, weight=1)
        cards_container.grid_rowconfigure(0, weight=1)

        # Net Income Card
        net_income_card = tk.Frame(
            cards_container, relief=tk.RIDGE, borderwidth=2, bg="#2b2b2b"
        )
        net_income_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        net_income_title = tk.Label(
            net_income_card,
            text="Monthly Net Income",
            font=("Arial", 14, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        )
        net_income_title.pack(pady=(20, 10))

        self.net_income_label = tk.Label(
            net_income_card,
            text="$0.00",
            font=("Arial", 32, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        )
        self.net_income_label.pack(pady=(10, 20))

        # Top Spending Category Card
        top_category_card = tk.Frame(
            cards_container, relief=tk.RIDGE, borderwidth=2, bg="#2b2b2b"
        )
        top_category_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        top_category_title = tk.Label(
            top_category_card,
            text="Top Spending Category",
            font=("Arial", 14, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        )
        top_category_title.pack(pady=(20, 10))

        self.top_category_name_label = tk.Label(
            top_category_card,
            text="N/A",
            font=("Arial", 24, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        )
        self.top_category_name_label.pack(pady=(5, 5))

        self.top_category_amount_label = tk.Label(
            top_category_card,
            text="$0.00",
            font=("Arial", 18),
            bg="#2b2b2b",
            fg="#aaaaaa",
        )
        self.top_category_amount_label.pack(pady=(5, 20))

    def _update_header_label(self):
        """Update the month/year label and button states."""
        month_name = calendar.month_name[self._current_month]
        self.month_label.config(text=f"{month_name} {self._current_year}")
        self._update_button_states()

    def _has_previous_month(self) -> bool:
        """Check if there's data in the previous month."""
        if self._current_month == 1:
            prev_year, prev_month = self._current_year - 1, 12
        else:
            prev_year, prev_month = self._current_year, self._current_month - 1
        return (prev_year, prev_month) in self._months_with_data

    def _has_next_month(self) -> bool:
        """Check if there's data in the next month."""
        if self._current_month == 12:
            next_year, next_month = self._current_year + 1, 1
        else:
            next_year, next_month = self._current_year, self._current_month + 1
        return (next_year, next_month) in self._months_with_data

    def _update_button_states(self):
        """Enable/disable navigation buttons based on data availability."""
        # Enable previous button only if previous month has data
        if self._has_previous_month():
            self.prev_button.config(state=tk.NORMAL)
        else:
            self.prev_button.config(state=tk.DISABLED)

        # Enable next button only if next month has data
        if self._has_next_month():
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)

    def _previous_month(self):
        """Navigate to previous month."""
        if self._current_month == 1:
            self._current_month = 12
            self._current_year -= 1
        else:
            self._current_month -= 1
        self._update_header_label()
        self._update_metrics()

    def _next_month(self):
        """Navigate to next month."""
        if self._current_month == 12:
            self._current_month = 1
            self._current_year += 1
        else:
            self._current_month += 1
        self._update_header_label()
        self._update_metrics()

    def _update_metrics(self):
        """Update metric displays with current month data."""
        # Get monthly net income
        net_income = self.transaction_repo.get_monthly_net_income(
            self._current_year, self._current_month
        )

        # Format and color code net income
        formatted_income = f"${abs(net_income):,.2f}"
        if net_income < 0:
            formatted_income = f"-{formatted_income}"
            color = "#ff4444"  # Red for negative
        elif net_income > 0:
            color = "#44ff44"  # Green for positive
        else:
            color = "#ffffff"  # White for zero

        self.net_income_label.config(text=formatted_income, fg=color)

        # Get top spending category
        top_category = self.transaction_repo.get_top_spending_category(
            self._current_year, self._current_month
        )

        if top_category is None:
            self.top_category_name_label.config(text="N/A")
            self.top_category_amount_label.config(text="$0.00")
        else:
            category_name, amount = top_category
            self.top_category_name_label.config(text=category_name)
            self.top_category_amount_label.config(text=f"${amount:,.2f}")

    def refresh(self):
        """Refresh statistics when tab becomes active."""
        self._update_metrics()
