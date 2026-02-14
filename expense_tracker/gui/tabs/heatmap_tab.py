import calendar
import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk

from expense_tracker.services.statistics import StatisticsService

# GitHub-style green color palette (5 levels)
COLORS = [
    "#ebedf0",  # no spending
    "#9be9a8",  # low
    "#40c463",  # medium
    "#30a14e",  # high
    "#216e39",  # very high
]

CELL_SIZE = 14
CELL_GAP = 3
CELL_STRIDE = CELL_SIZE + CELL_GAP

DAY_LABELS = ["Mon", "", "Wed", "", "Fri", "", "Sun"]
MONTH_ABBREVS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

# Layout constants
LEFT_MARGIN = 40  # space for day-of-week labels
TOP_MARGIN = 20   # space for month labels


class HeatmapTab(tk.Frame):
    def __init__(self, master, statistics_service: StatisticsService, main_window):
        super().__init__(master)
        self.statistics_service = statistics_service
        self.main_window = main_window

        # State
        self._available_years: list[int] = []
        self._current_year: int = date.today().year
        self._spending_data: dict[str, float] = {}
        self._cell_map: dict[tuple[int, int], date] = {}  # (col, row) -> date

        # Tooltip
        self._tooltip: tk.Toplevel | None = None
        self._tooltip_cell: tuple[int, int] | None = None

        self.pack(fill=tk.BOTH, expand=True)

        # Build UI
        self._build_header()
        self._canvas_container = tk.Frame(self)
        self._canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._canvas: tk.Canvas | None = None

    def _build_header(self):
        """Build header with year navigation controls."""
        header = tk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)

        self.prev_button = ttk.Button(
            header, text="<", command=self._previous_year, width=3
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.year_label = ttk.Label(header, text="", font=("Arial", 20, "bold"))
        self.year_label.pack(side=tk.LEFT, expand=True)

        self.next_button = ttk.Button(
            header, text=">", command=self._next_year, width=3
        )
        self.next_button.pack(side=tk.RIGHT, padx=5)

    def _update_header(self):
        """Update the year label and button states."""
        if not self._available_years:
            self.year_label.config(text="No expenses found")
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            return

        self.year_label.config(text=str(self._current_year))

        year_idx = (
            self._available_years.index(self._current_year)
            if self._current_year in self._available_years
            else -1
        )
        self.prev_button.config(
            state=tk.NORMAL
            if year_idx < len(self._available_years) - 1
            else tk.DISABLED
        )
        self.next_button.config(
            state=tk.NORMAL if year_idx > 0 else tk.DISABLED
        )

    def _previous_year(self):
        """Navigate to previous year with expenses."""
        if self._current_year not in self._available_years:
            return
        idx = self._available_years.index(self._current_year)
        if idx < len(self._available_years) - 1:
            self._current_year = self._available_years[idx + 1]
            self._update_header()
            self._build_heatmap()

    def _next_year(self):
        """Navigate to next year with expenses."""
        if self._current_year not in self._available_years:
            return
        idx = self._available_years.index(self._current_year)
        if idx > 0:
            self._current_year = self._available_years[idx - 1]
            self._update_header()
            self._build_heatmap()

    def refresh(self):
        """Fetch data and rebuild heatmap."""
        self._available_years = self.statistics_service.get_available_years()

        if self._available_years:
            self._current_year = self._available_years[0]
        else:
            self._current_year = date.today().year

        self._update_header()
        self._build_heatmap()

    def _build_heatmap(self):
        """Build the GitHub-style heatmap grid."""
        # Clear existing canvas
        for widget in self._canvas_container.winfo_children():
            widget.destroy()

        if not self._available_years:
            message = tk.Label(
                self._canvas_container,
                text="No expenses found",
                font=("Arial", 16),
                fg="gray",
            )
            message.pack(pady=50)
            return

        # Fetch spending data
        self._spending_data = self.statistics_service.get_yearly_heatmap_data(
            self._current_year
        )

        # Calculate grid layout
        jan1 = date(self._current_year, 1, 1)
        dec31 = date(self._current_year, 12, 31)
        jan1_weekday = jan1.weekday()  # 0=Mon, 6=Sun
        self._total_days = (dec31 - jan1).days + 1
        total_days = self._total_days
        num_cols = (jan1_weekday + total_days - 1) // 7 + 1

        # Build cell map
        self._cell_map = {}
        for day_offset in range(total_days):
            d = jan1 + timedelta(days=day_offset)
            col = (jan1_weekday + day_offset) // 7
            row = d.weekday()
            self._cell_map[(col, row)] = d

        # Calculate color thresholds from spending data
        spending_values = sorted(v for v in self._spending_data.values() if v > 0)
        if spending_values:
            n = len(spending_values)
            self._thresholds = [
                spending_values[n // 4],
                spending_values[n // 2] if n > 1 else spending_values[0],
                spending_values[(3 * n) // 4] if n > 2 else spending_values[-1],
            ]
        else:
            self._thresholds = [0, 0, 0]

        # Canvas dimensions
        canvas_w = LEFT_MARGIN + num_cols * CELL_STRIDE + 10
        canvas_h = TOP_MARGIN + 7 * CELL_STRIDE + 50  # extra for legend

        self._canvas = tk.Canvas(
            self._canvas_container,
            width=canvas_w,
            height=canvas_h,
            highlightthickness=0,
        )
        self._canvas.pack(anchor=tk.CENTER)

        # Draw month labels
        self._draw_month_labels(jan1, jan1_weekday)

        # Draw day-of-week labels
        for row_idx, label in enumerate(DAY_LABELS):
            if label:
                y = TOP_MARGIN + row_idx * CELL_STRIDE + CELL_SIZE // 2
                self._canvas.create_text(
                    LEFT_MARGIN - 8, y,
                    text=label,
                    anchor=tk.E,
                    font=("Arial", 9),
                    fill="white",
                )

        # Draw cells
        for (col, row), d in self._cell_map.items():
            x = LEFT_MARGIN + col * CELL_STRIDE
            y = TOP_MARGIN + row * CELL_STRIDE
            spending = self._spending_data.get(d.isoformat(), 0.0)
            color = self._get_color(spending)

            self._canvas.create_rectangle(
                x, y, x + CELL_SIZE, y + CELL_SIZE,
                fill=color,
                outline="",
                tags=f"cell_{col}_{row}",
            )

        # Draw legend
        self._draw_legend(canvas_w, canvas_h)

        # Build summary cards below heatmap
        self._build_summary_cards()

        # Bind events
        self._canvas.bind("<Motion>", self._on_mouse_move)
        self._canvas.bind("<Leave>", self._on_mouse_leave)
        self._canvas.bind("<Button-1>", self._on_click)
        self._canvas.configure(cursor="hand2")

    def _build_summary_cards(self):
        """Build yearly summary cards below the heatmap."""
        summary_frame = tk.Frame(self._canvas_container)
        summary_frame.pack(fill=tk.X, pady=(10, 0))
        for col in range(3):
            summary_frame.columnconfigure(col, weight=1)

        # Compute metrics
        total_spent = sum(self._spending_data.values())
        daily_avg = total_spent / self._total_days if self._spending_data else 0.0

        if self._spending_data:
            busiest_key = max(self._spending_data, key=self._spending_data.get)
            busiest_date = date.fromisoformat(busiest_key)
            busiest_amount = self._spending_data[busiest_key]
            busiest_label = busiest_date.strftime("%b %-d")
        else:
            busiest_label = None
            busiest_amount = 0.0

        # Card 1: Total Spent
        card1 = tk.Frame(
            summary_frame, relief=tk.RIDGE, borderwidth=2, bg="#2b2b2b"
        )
        card1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        tk.Label(
            card1, text="Total Spent", font=("Arial", 14, "bold"),
            bg="#2b2b2b", fg="#ffffff",
        ).pack(pady=(20, 10))
        tk.Label(
            card1, text=f"${total_spent:,.2f}", font=("Arial", 28, "bold"),
            bg="#2b2b2b", fg="#ffffff",
        ).pack(pady=(10, 20))

        # Card 2: Daily Average
        card2 = tk.Frame(
            summary_frame, relief=tk.RIDGE, borderwidth=2, bg="#2b2b2b"
        )
        card2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        tk.Label(
            card2, text="Daily Average", font=("Arial", 14, "bold"),
            bg="#2b2b2b", fg="#ffffff",
        ).pack(pady=(20, 10))
        tk.Label(
            card2, text=f"${daily_avg:,.2f}", font=("Arial", 28, "bold"),
            bg="#2b2b2b", fg="#ffffff",
        ).pack(pady=(10, 20))

        # Card 3: Busiest Day
        card3 = tk.Frame(
            summary_frame, relief=tk.RIDGE, borderwidth=2, bg="#2b2b2b"
        )
        card3.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        tk.Label(
            card3, text="Busiest Day", font=("Arial", 14, "bold"),
            bg="#2b2b2b", fg="#ffffff",
        ).pack(pady=(20, 10))
        if busiest_label:
            tk.Label(
                card3, text=busiest_label, font=("Arial", 28, "bold"),
                bg="#2b2b2b", fg="#ffffff",
            ).pack(pady=(10, 0))
            tk.Label(
                card3, text=f"${busiest_amount:,.2f}", font=("Arial", 18),
                bg="#2b2b2b", fg="#aaaaaa",
            ).pack(pady=(5, 20))
        else:
            tk.Label(
                card3, text="N/A", font=("Arial", 28, "bold"),
                bg="#2b2b2b", fg="#ffffff",
            ).pack(pady=(10, 20))

    def _draw_month_labels(self, jan1: date, jan1_weekday: int):
        """Draw month abbreviation labels along the top."""
        for month_num in range(1, 13):
            first_of_month = date(self._current_year, month_num, 1)
            day_offset = (first_of_month - jan1).days
            col = (jan1_weekday + day_offset) // 7
            x = LEFT_MARGIN + col * CELL_STRIDE
            self._canvas.create_text(
                x, TOP_MARGIN - 8,
                text=MONTH_ABBREVS[month_num - 1],
                anchor=tk.W,
                font=("Arial", 9),
                fill="white",
            )

    def _draw_legend(self, canvas_w: int, canvas_h: int):
        """Draw the Less/More legend at the bottom-right."""
        legend_y = canvas_h - 25
        legend_right = canvas_w - 10
        box_size = 12
        box_gap = 3
        total_boxes_w = len(COLORS) * (box_size + box_gap)

        # "More" label
        self._canvas.create_text(
            legend_right, legend_y + box_size // 2,
            text="More",
            anchor=tk.E,
            font=("Arial", 9),
            fill="white",
        )

        # Color boxes (right to left)
        box_start_x = legend_right - 35 - total_boxes_w
        for i, color in enumerate(COLORS):
            x = box_start_x + i * (box_size + box_gap)
            self._canvas.create_rectangle(
                x, legend_y, x + box_size, legend_y + box_size,
                fill=color,
                outline="",
            )

        # "Less" label
        self._canvas.create_text(
            box_start_x - 5, legend_y + box_size // 2,
            text="Less",
            anchor=tk.E,
            font=("Arial", 9),
            fill="white",
        )

    def _get_color(self, spending: float) -> str:
        """Get the GitHub-style green color for a spending amount."""
        if spending <= 0:
            return COLORS[0]
        if spending <= self._thresholds[0]:
            return COLORS[1]
        if spending <= self._thresholds[1]:
            return COLORS[2]
        if spending <= self._thresholds[2]:
            return COLORS[3]
        return COLORS[4]

    def _coords_to_cell(self, x: int, y: int) -> tuple[int, int] | None:
        """Convert canvas coordinates to (col, row) grid position."""
        col = (x - LEFT_MARGIN) // CELL_STRIDE
        row = (y - TOP_MARGIN) // CELL_STRIDE

        # Check if click is within a cell (not in gap)
        cell_x = (x - LEFT_MARGIN) % CELL_STRIDE
        cell_y = (y - TOP_MARGIN) % CELL_STRIDE
        if cell_x >= CELL_SIZE or cell_y >= CELL_SIZE:
            return None

        if (col, row) in self._cell_map:
            return (col, row)
        return None

    def _on_mouse_move(self, event):
        """Handle mouse movement for tooltips."""
        cell = self._coords_to_cell(event.x, event.y)

        if cell == self._tooltip_cell:
            return  # Still in same cell, no update needed

        self._tooltip_cell = cell
        self._hide_tooltip()

        if cell is None:
            return

        d = self._cell_map[cell]
        spending = self._spending_data.get(d.isoformat(), 0.0)

        day_name = calendar.day_name[d.weekday()]
        month_name = calendar.month_abbr[d.month]
        tooltip_text = f"${spending:.2f} on {day_name}, {month_name} {d.day}, {d.year}"

        self._tooltip = tk.Toplevel(self)
        self._tooltip.wm_overrideredirect(True)
        self._tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

        label = tk.Label(
            self._tooltip,
            text=tooltip_text,
            background="#FFFFE0",
            relief=tk.SOLID,
            borderwidth=1,
            padx=5,
            pady=3,
        )
        label.pack()

    def _on_mouse_leave(self, event):
        """Handle mouse leaving the canvas."""
        self._tooltip_cell = None
        self._hide_tooltip()

    def _hide_tooltip(self):
        """Hide the tooltip."""
        if self._tooltip:
            self._tooltip.destroy()
            self._tooltip = None

    def _on_click(self, event):
        """Handle click on a day cell."""
        cell = self._coords_to_cell(event.x, event.y)
        if cell is None:
            return

        clicked_date = self._cell_map[cell]
        self.main_window.show_transactions_for_date(clicked_date)
