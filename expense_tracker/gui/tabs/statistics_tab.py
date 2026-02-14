import calendar
import tkinter as tk
from tkinter import ttk

from expense_tracker.services.statistics import StatisticsService


class StatisticsTab(tk.Frame):
    def __init__(self, master, statistics_service: StatisticsService):
        super().__init__(master)
        self.statistics_service = statistics_service

        # State: the latest month and year where the record is available
        latest_year, latest_month = self.statistics_service.get_latest_available_month()
        self._current_year = latest_year
        self._current_month = latest_month

        # Cache all months with data for navigation button state management
        self._months_with_data = self.statistics_service.get_available_months()

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
        """Build card-based layout for displaying metrics (2x3 grid)."""
        # Container for metrics cards
        cards_container = tk.Frame(self)
        cards_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Configure 2x3 grid
        for col in range(3):
            cards_container.grid_columnconfigure(col, weight=1)
        for row in range(2):
            cards_container.grid_rowconfigure(row, weight=1)

        # Row 0, Col 0: Net Income Card
        net_income_card = tk.Frame(
            cards_container, relief=tk.RIDGE, borderwidth=2, bg="#2b2b2b"
        )
        net_income_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        tk.Label(
            net_income_card,
            text="Monthly Net Income",
            font=("Arial", 14, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        ).pack(pady=(20, 10))

        self.net_income_label = tk.Label(
            net_income_card,
            text="$0.00",
            font=("Arial", 28, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        )
        self.net_income_label.pack(pady=(10, 20))

        # Row 0, Col 1: Top Spending Category Card
        top_category_card = tk.Frame(
            cards_container, relief=tk.RIDGE, borderwidth=2, bg="#2b2b2b"
        )
        top_category_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        tk.Label(
            top_category_card,
            text="Top Spending Category",
            font=("Arial", 14, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        ).pack(pady=(20, 10))

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

        # Row 0, Col 2: Total Expenses Card
        total_expenses_card = tk.Frame(
            cards_container, relief=tk.RIDGE, borderwidth=2, bg="#2b2b2b"
        )
        total_expenses_card.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        tk.Label(
            total_expenses_card,
            text="Total Expenses",
            font=("Arial", 14, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        ).pack(pady=(20, 10))

        self.total_expenses_label = tk.Label(
            total_expenses_card,
            text="$0.00",
            font=("Arial", 28, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        )
        self.total_expenses_label.pack(pady=(10, 20))

        # Row 1, Col 0: Transaction Count Card
        txn_count_card = tk.Frame(
            cards_container, relief=tk.RIDGE, borderwidth=2, bg="#2b2b2b"
        )
        txn_count_card.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        tk.Label(
            txn_count_card,
            text="Transactions",
            font=("Arial", 14, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        ).pack(pady=(20, 10))

        self.txn_count_label = tk.Label(
            txn_count_card,
            text="0",
            font=("Arial", 28, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        )
        self.txn_count_label.pack(pady=(10, 20))

        # Row 1, Col 1: Average Transaction Card
        avg_txn_card = tk.Frame(
            cards_container, relief=tk.RIDGE, borderwidth=2, bg="#2b2b2b"
        )
        avg_txn_card.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        tk.Label(
            avg_txn_card,
            text="Avg Transaction",
            font=("Arial", 14, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        ).pack(pady=(20, 10))

        self.avg_txn_label = tk.Label(
            avg_txn_card,
            text="$0.00",
            font=("Arial", 28, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        )
        self.avg_txn_label.pack(pady=(10, 20))

        # Row 1, Col 2: Month-over-Month Card
        mom_card = tk.Frame(
            cards_container, relief=tk.RIDGE, borderwidth=2, bg="#2b2b2b"
        )
        mom_card.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        tk.Label(
            mom_card,
            text="vs. Last Month",
            font=("Arial", 14, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        ).pack(pady=(20, 10))

        self.mom_label = tk.Label(
            mom_card,
            text="N/A",
            font=("Arial", 28, "bold"),
            bg="#2b2b2b",
            fg="#ffffff",
        )
        self.mom_label.pack(pady=(10, 20))

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
        # Get monthly metrics from statistics service
        metrics = self.statistics_service.get_monthly_metrics(
            self._current_year, self._current_month
        )

        # Format and color code net income
        formatted_income = f"${abs(metrics.net_income):,.2f}"
        if metrics.net_income < 0:
            formatted_income = f"-{formatted_income}"
            color = "#ff4444"  # Red for negative
        elif metrics.net_income > 0:
            color = "#44ff44"  # Green for positive
        else:
            color = "#ffffff"  # White for zero

        self.net_income_label.config(text=formatted_income, fg=color)

        # Display top spending category
        if metrics.top_category is None:
            self.top_category_name_label.config(text="N/A")
            self.top_category_amount_label.config(text="$0.00")
        else:
            self.top_category_name_label.config(text=metrics.top_category)
            self.top_category_amount_label.config(
                text=f"${metrics.top_category_spending:,.2f}"
            )

        # Total Expenses
        self.total_expenses_label.config(text=f"${metrics.total_expenses:,.2f}")

        # Transaction Count
        self.txn_count_label.config(text=str(metrics.transaction_count))

        # Average Transaction
        self.avg_txn_label.config(text=f"${metrics.avg_transaction:,.2f}")

        # Month-over-Month
        if metrics.month_over_month_pct is None:
            self.mom_label.config(text="N/A", fg="#ffffff")
        else:
            pct = metrics.month_over_month_pct
            if pct > 0:
                self.mom_label.config(text=f"+{pct:.1f}%", fg="#ff4444")  # Red: spending increased
            elif pct < 0:
                self.mom_label.config(text=f"{pct:.1f}%", fg="#44ff44")  # Green: spending decreased
            else:
                self.mom_label.config(text="0.0%", fg="#ffffff")

    def refresh(self):
        """Refresh statistics when tab becomes active."""
        self._update_metrics()
