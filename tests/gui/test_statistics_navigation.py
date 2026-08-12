from expense_tracker.gui.tabs.statistics_tab import adjacent_month

# A statement gap is normal: nothing was imported between January and July.
SPARSE = [(2025, 12), (2026, 1), (2026, 7)]


def test_next_month_jumps_over_a_gap():
    assert adjacent_month(SPARSE, (2026, 1), 1) == (2026, 7)


def test_previous_month_jumps_back_over_a_gap():
    assert adjacent_month(SPARSE, (2026, 7), -1) == (2026, 1)


def test_no_next_month_at_the_latest():
    assert adjacent_month(SPARSE, (2026, 7), 1) is None


def test_no_previous_month_at_the_earliest():
    assert adjacent_month(SPARSE, (2025, 12), -1) is None


def test_steps_across_a_year_boundary():
    assert adjacent_month(SPARSE, (2025, 12), 1) == (2026, 1)


def test_orders_unsorted_input():
    # get_all_months_with_data() returns a set, so order is not guaranteed
    assert adjacent_month([(2026, 7), (2025, 12), (2026, 1)], (2026, 1), 1) == (2026, 7)


def test_month_with_no_data_has_no_neighbours():
    assert adjacent_month(SPARSE, (2026, 3), 1) is None
    assert adjacent_month(SPARSE, (2026, 3), -1) is None


def test_empty_history():
    assert adjacent_month([], (2026, 1), 1) is None
