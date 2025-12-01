import calendar
import tkinter as tk
from datetime import date
from tkinter import ttk

from expense_tracker.core.repositories import TransactionRepository


class HeatmapTab(tk.Frame):
    def __init__(self, master, transaction_repo: TransactionRepository, main_window):
        super().__init__(master)
        self.transaction_repo: TransactionRepository = transaction_repo
        self.main_window = main_window

        # State
        self._months_with_expenses: list[tuple[int, int]] = []
        self._current_index = 0
        self._spending_data: dict[int, float] = {}

        # Tooltip
        self._tooltip: tk.Toplevel | None = None

        self.pack(fill=tk.BOTH, expand=True)

        # Build UI
        self._build_header()
        self._calendar_container = tk.Frame(self)
        self._calendar_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _build_header(self):
        """Build header with month navigation controls."""
        header = tk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)

        # Previous month button
        self.prev_button = ttk.Button(
            header, text="<", command=self._previous_month, width=3
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)

        # Month/Year label
        self.month_label = ttk.Label(header, text="", font=("Arial", 14, "bold"))
        self.month_label.pack(side=tk.LEFT, expand=True)

        # Next month button
        self.next_button = ttk.Button(
            header, text=">", command=self._next_month, width=3
        )
        self.next_button.pack(side=tk.RIGHT, padx=5)

    def _update_header_label(self):
        """Update the month/year label and button states."""
        if not self._months_with_expenses:
            self.month_label.config(text="No expenses found")
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            return

        year, month = self._months_with_expenses[self._current_index]
        month_name = calendar.month_name[month]

        # Show current position
        self.month_label.config(
            text=f"{month_name} {year}"
        )

        # Update button states
        self.prev_button.config(
            state=tk.NORMAL if self._current_index < len(self._months_with_expenses) - 1 else tk.DISABLED
        )
        self.next_button.config(
            state=tk.NORMAL if self._current_index > 0 else tk.DISABLED
        )

    def _previous_month(self):
        """Navigate to previous month with expenses."""
        if self._current_index < len(self._months_with_expenses) - 1:
            self._current_index += 1
            self._update_header_label()
            self._build_calendar_grid()

    def _next_month(self):
        """Navigate to next month with expenses."""
        if self._current_index > 0:
            self._current_index -= 1
            self._update_header_label()
            self._build_calendar_grid()

    def refresh(self):
        """Fetch data and rebuild calendar grid."""
        # Get all months with expenses
        self._months_with_expenses = self.transaction_repo.get_months_with_expenses()

        # Reset to most recent month
        self._current_index = 0

        # Update header
        self._update_header_label()

        # Build calendar
        self._build_calendar_grid()

    def _build_calendar_grid(self):
        """Build the calendar grid with spending data."""
        # Clear existing calendar
        for widget in self._calendar_container.winfo_children():
            widget.destroy()

        if not self._months_with_expenses:
            # Show message if no transactions
            message = tk.Label(
                self._calendar_container,
                text="No expenses found",
                font=("Arial", 16),
                fg="gray",
            )
            message.pack(pady=50)
            return

        # Get current month
        year, month = self._months_with_expenses[self._current_index]

        # Fetch spending data for current month
        self._spending_data = self.transaction_repo.get_daily_spending_for_month(
            year, month
        )

        # Create grid frame
        grid_frame = tk.Frame(self._calendar_container)
        grid_frame.pack(expand=True)

        # Day of week headers
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day_name in enumerate(day_names):
            label = tk.Label(
                grid_frame,
                text=day_name,
                font=("Arial", 10, "bold"),
                width=12,
                height=1,
            )
            label.grid(row=0, column=col, padx=2, pady=2)

        # Get calendar information
        first_weekday, num_days = calendar.monthrange(year, month)

        # Calculate color thresholds
        spending_values = [v for v in self._spending_data.values() if v > 0]
        if spending_values:
            spending_values.sort()
            p25_idx = len(spending_values) // 4
            p75_idx = (3 * len(spending_values)) // 4
            p25 = spending_values[p25_idx] if p25_idx < len(spending_values) else 0
            p75 = spending_values[p75_idx] if p75_idx < len(spending_values) else 0
        else:
            p25 = p75 = 0

        # Build calendar grid
        current_day = 1
        for week in range(6):  # Max 6 weeks
            if current_day > num_days:
                break

            for weekday in range(7):
                row = week + 1  # +1 for header row

                # Check if we should place a day here
                if week == 0 and weekday < first_weekday:
                    # Empty cell before first day of month
                    empty_canvas = tk.Canvas(
                        grid_frame,
                        width=90,
                        height=70,
                        highlightthickness=1,
                        highlightbackground="#CCCCCC",
                    )
                    empty_canvas.grid(row=row, column=weekday, padx=2, pady=2)
                    # Draw gray background for empty cells
                    empty_canvas.create_rectangle(
                        0, 0, 90, 70,
                        fill="#EEEEEE",
                        outline="",
                    )
                elif current_day <= num_days:
                    # Create day cell using Canvas for reliable color rendering
                    spending = self._spending_data.get(current_day, 0.0)
                    color = self._get_color_for_spending(spending, p25, p75)

                    # Determine text color for readability
                    text_color = "white" if color == "#CC0000" else "black"

                    # Create canvas with explicit background rectangle
                    cell_canvas = tk.Canvas(
                        grid_frame,
                        width=90,
                        height=70,
                        highlightthickness=1,
                        highlightbackground="#999999",
                    )
                    cell_canvas.grid(row=row, column=weekday, padx=2, pady=2)

                    # Draw colored rectangle as background (this bypasses theme)
                    cell_canvas.create_rectangle(
                        0, 0, 90, 70,
                        fill=color,
                        outline="",
                    )

                    # Draw text on top of the colored background
                    cell_canvas.create_text(
                        45, 20,
                        text=str(current_day),
                        fill=text_color,
                        font=("Arial", 12, "bold"),
                    )
                    cell_canvas.create_text(
                        45, 50,
                        text=f"${spending:.2f}",
                        fill=text_color,
                        font=("Arial", 9),
                    )

                    # Bind events
                    day_num = current_day  # Capture in closure
                    cell_canvas.bind(
                        "<Button-1>",
                        lambda _e, y=year, m=month, d=day_num: self._on_day_click(y, m, d),
                    )
                    cell_canvas.bind(
                        "<Enter>",
                        lambda e, m=month, d=day_num, s=spending: self._show_tooltip(
                            e, m, d, s
                        ),
                    )
                    cell_canvas.bind("<Leave>", self._hide_tooltip)
                    # Change cursor on hover
                    cell_canvas.configure(cursor="hand2")

                    current_day += 1

    def _get_color_for_spending(self, spending: float, p25: float, p75: float) -> str:
        """
        Calculate color based on spending amount using a heatmap gradient.
        White (no spending) -> Light red -> Medium red -> Dark red (high spending)
        """
        if spending == 0:
            return "#FFFFFF"  # White (no spending)
        elif spending < p25:
            return "#FFCCCC"  # Light red (low spending)
        elif spending < p75:
            return "#FF6666"  # Medium red (moderate spending)
        else:
            return "#CC0000"  # Dark red (high spending)

    def _show_tooltip(self, event, month: int, day: int, amount: float):
        """Show tooltip with spending details."""
        self._hide_tooltip(event)  # Hide any existing tooltip

        month_name = calendar.month_name[month]

        self._tooltip = tk.Toplevel(self)
        self._tooltip.wm_overrideredirect(True)
        self._tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

        label = tk.Label(
            self._tooltip,
            text=f"{month_name} {day}: ${amount:.2f}",
            background="#FFFFE0",
            relief=tk.SOLID,
            borderwidth=1,
            padx=5,
            pady=3,
        )
        label.pack()

    def _hide_tooltip(self, event):
        """Hide the tooltip."""
        if self._tooltip:
            self._tooltip.destroy()
            self._tooltip = None

    def _on_day_click(self, year: int, month: int, day: int):
        """Handle click on a day cell."""
        # Construct the full date
        clicked_date = date(year, month, day)

        # Call main window to switch to Transactions tab with filter
        self.main_window.show_transactions_for_date(clicked_date)
