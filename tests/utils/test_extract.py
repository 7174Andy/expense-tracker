from dataclasses import FrozenInstanceError
from datetime import date
from unittest.mock import Mock, patch

import pytest

from expense_tracker.utils.extract import (
    BOFA_CHECKING,
    GENERIC,
    PROFILES,
    StatementProfile,
    _parse_amount,
    detect_profile,
    page_lines,
    parse_statement,
    remove_boilerplate,
    rows_from_lines,
)


def _mock_page(words, text=""):
    page = Mock()
    page.extract_words.return_value = words
    page.extract_text.return_value = text
    return page


def _mock_pdf(pages, metadata=None):
    pdf = Mock()
    pdf.pages = pages
    pdf.metadata = metadata or {}
    return pdf


# --- amounts: assertions carried over verbatim as the regression baseline ---


def test_parse_amount():
    assert _parse_amount("100.00") == 100.0
    assert _parse_amount("$50.50") == 50.5
    assert _parse_amount("1,000.00") == 1000.0
    assert _parse_amount("($25.00)") == -25.0
    assert _parse_amount("-10.00") == -10.0
    assert _parse_amount("") == 0.0
    assert _parse_amount("  $ 123.45  ") == 123.45
    assert _parse_amount(" -5.00 ") == -5.00
    assert _parse_amount("$1,234.56") == 1234.56


# --- layout pass ---


def test_page_lines_groups_by_y_position():
    page = _mock_page(
        [
            # out of order horizontally, to prove sorting by x0
            {"text": "Transaction", "top": 10, "x0": 30},
            {"text": "01/15/24", "top": 10, "x0": 10},
            {"text": "Some", "top": 10, "x0": 20},
            # rounds into the same y-bucket, so it joins the line above
            {"text": "$123.45", "top": 10.5, "x0": 40},
            # a different bucket, so it starts a new line
            {"text": "01/16/24", "top": 20, "x0": 10},
            {"text": "", "top": 20, "x0": 20},  # blank tokens are dropped
        ]
    )

    assert page_lines(page) == [
        ["01/15/24", "Some", "Transaction", "$123.45"],
        ["01/16/24"],
    ]


def test_page_lines_buckets_rather_than_tolerates():
    """`round(top / 2) * 2` buckets, so near-identical tops can still split.

    Carried over from the original parser unchanged; documented here so a future
    change to the grouping rule is a deliberate one.
    """
    page = _mock_page(
        [
            {"text": "A", "top": 10, "x0": 10},
            {"text": "B", "top": 11, "x0": 20},  # 1pt apart, different bucket
        ]
    )

    assert page_lines(page) == [["A"], ["B"]]


def test_page_lines_handles_empty_page():
    assert page_lines(_mock_page([])) == []
    assert page_lines(_mock_page(None)) == []


# --- profiles ---


def test_profile_is_immutable():
    with pytest.raises(FrozenInstanceError):
        setattr(BOFA_CHECKING, "name", "Something Else")


def test_generic_is_not_registered():
    # An empty `detect` would match everything and shadow every real profile.
    assert GENERIC not in PROFILES
    assert GENERIC.detect == ()


def test_every_profile_date_format_has_a_year():
    # Year inference is out of scope, so no profile may omit the year.
    for profile in (*PROFILES, GENERIC):
        for fmt in profile.date_formats:
            assert "%y" in fmt or "%Y" in fmt


# --- detection ---


def test_detect_profile_by_page_text():
    pdf = _mock_pdf([_mock_page([], text="Bank of America Statement")])
    assert detect_profile(pdf) is BOFA_CHECKING


def test_detect_profile_by_metadata():
    pdf = _mock_pdf(
        [_mock_page([], text="nothing useful here")],
        metadata={"Producer": "Bank of America Statement Generator"},
    )
    assert detect_profile(pdf) is BOFA_CHECKING


def test_detect_profile_falls_back_to_generic():
    pdf = _mock_pdf([_mock_page([], text="Some Other Bank")], metadata={"Producer": "X"})
    assert detect_profile(pdf) is GENERIC


def test_detect_profile_prefers_page_text_over_metadata(monkeypatch):
    """Two profiles sharing metadata are only separable by page text."""
    sibling = StatementProfile(
        name="BofA Credit",
        detect=("Credit Card Statement",),
        date_formats=("%m/%d/%y",),
        skip=(),
    )
    monkeypatch.setattr(
        "expense_tracker.utils.extract.PROFILES", (BOFA_CHECKING, sibling)
    )
    pdf = _mock_pdf(
        [_mock_page([], text="Credit Card Statement")],
        metadata={"Producer": "Bank of America"},  # would match BOFA_CHECKING
    )
    assert detect_profile(pdf) is sibling


# --- preprocessing ---


def test_remove_boilerplate_drops_lines_on_every_page():
    footer = ["01/31/24", "Member", "FDIC", "$0.00"]  # looks like a transaction
    pages = [
        [["01/15/24", "Coffee", "-4.50"], footer],
        [["01/16/24", "Books", "-20.00"], footer],
    ]

    assert remove_boilerplate(pages) == [
        ["01/15/24", "Coffee", "-4.50"],
        ["01/16/24", "Books", "-20.00"],
    ]


def test_remove_boilerplate_keeps_lines_on_some_pages():
    shared = ["01/15/24", "Coffee", "-4.50"]
    pages = [[shared, ["a", "b", "c"]], [["d", "e", "f"]], [shared]]

    assert shared in remove_boilerplate(pages)


def test_remove_boilerplate_skips_single_page_statements():
    pages = [[["01/15/24", "Coffee", "-4.50"], ["Page", "1", "of", "1"]]]

    assert remove_boilerplate(pages) == pages[0]


def test_remove_boilerplate_ignores_repeats_within_one_page():
    """A line twice on one page of a two-page statement is not a footer."""
    twice = ["01/15/24", "Coffee", "-4.50"]
    pages = [[twice, twice], [["01/16/24", "Books", "-20.00"]]]

    assert twice in remove_boilerplate(pages)


# --- row interpretation: plain token lists, no PDF objects ---


def test_rows_from_lines():
    lines = [
        ["01/15/24", "Some", "Transaction", "$123.45"],
        ["01/16/24", "Another", "One", "($50.00)"],
        ["01/17/24", "Total", "Spending", "$173.45"],  # skip prefix
        ["Invalid", "Line", "$10.00"],  # no leading date
        ["01/18/24", "No", "Amount"],  # no amount
        ["01/19/24", "Short"],  # fewer than 3 tokens
    ]

    assert rows_from_lines(lines, BOFA_CHECKING) == [
        {"date": date(2024, 1, 15), "description": "Some Transaction", "amount": 123.45},
        {"date": date(2024, 1, 16), "description": "Another One", "amount": -50.00},
    ]


def test_rows_from_lines_uses_rightmost_amount():
    lines = [["01/15/24", "Store", "#1234", "Purchase", "-42.00"]]

    (row,) = rows_from_lines(lines, BOFA_CHECKING)
    assert row["description"] == "Store #1234 Purchase"
    assert row["amount"] == -42.00


def test_rows_from_lines_respects_profile_date_formats():
    lines = [["2024-01-15", "ISO", "Dated", "-4.50"]]

    # BofA statements are MM/DD/YY, so an ISO date is not a transaction there
    assert rows_from_lines(lines, BOFA_CHECKING) == []
    # the generic profile accepts it
    (row,) = rows_from_lines(lines, GENERIC)
    assert row["date"] == date(2024, 1, 15)


# --- end to end ---


@patch("expense_tracker.utils.extract.pdfplumber.open")
def test_parse_statement(mock_open):
    footer = [
        {"text": "Member", "top": 90, "x0": 10},
        {"text": "FDIC", "top": 90, "x0": 20},
        {"text": "Page", "top": 90, "x0": 30},
    ]
    page1 = _mock_page(
        [
            {"text": "01/15/24", "top": 10, "x0": 10},
            {"text": "Transaction", "top": 10, "x0": 20},
            {"text": "1", "top": 10, "x0": 30},
            {"text": "$10.00", "top": 10, "x0": 40},
            *footer,
        ],
        text="Bank of America Statement",
    )
    page2 = _mock_page(
        [
            {"text": "01/16/24", "top": 20, "x0": 10},
            {"text": "Transaction", "top": 20, "x0": 20},
            {"text": "2", "top": 20, "x0": 30},
            {"text": "($20.00)", "top": 20, "x0": 40},
            *footer,
        ]
    )
    mock_open.return_value.__enter__.return_value = _mock_pdf([page1, page2])

    profile_name, transactions = parse_statement("dummy_path.pdf")

    assert profile_name == "BofA Checking"
    assert len(transactions) == 2
    assert transactions[0]["description"] == "Transaction 1"
    assert transactions[0]["amount"] == 10.00
    assert transactions[1]["description"] == "Transaction 2"
    assert transactions[1]["amount"] == -20.00
    mock_open.assert_called_with("dummy_path.pdf")


@patch("expense_tracker.utils.extract.pdfplumber.open")
def test_parse_statement_unknown_bank_uses_generic(mock_open):
    page = _mock_page(
        [
            {"text": "2024-01-15", "top": 10, "x0": 10},
            {"text": "Some", "top": 10, "x0": 20},
            {"text": "Purchase", "top": 10, "x0": 30},
            {"text": "-15.00", "top": 10, "x0": 40},
        ],
        text="Credit Union of Nowhere",
    )
    mock_open.return_value.__enter__.return_value = _mock_pdf([page])

    profile_name, transactions = parse_statement("dummy_path.pdf")

    assert profile_name == "Generic"
    assert transactions == [
        {"date": date(2024, 1, 15), "description": "Some Purchase", "amount": -15.00}
    ]
