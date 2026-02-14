from datetime import date

from expense_tracker.utils.extract import (
    _parse_amount,
    parse_bofa_page,
    parse_bofa_statement_pdf,
)
from unittest.mock import patch, Mock

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


def test_parse_bofa_page():
    mock_page = Mock()
    words = [
        # Line 1: A valid transaction
        {"text": "01/15/24", "top": 10, "x0": 10},
        {"text": "Some", "top": 10, "x0": 20},
        {"text": "Transaction", "top": 10, "x0": 30},
        {"text": "$123.45", "top": 10, "x0": 40},
        # Line 2: Another valid transaction with parenthesis for negative amount
        {"text": "01/16/24", "top": 20, "x0": 10},
        {"text": "Another", "top": 20, "x0": 20},
        {"text": "One", "top": 20, "x0": 30},
        {"text": "($50.00)", "top": 20, "x0": 40},
        # Line 3: A line to be ignored (total)
        {"text": "01/17/24", "top": 30, "x0": 10},
        {"text": "Total", "top": 30, "x0": 20},
        {"text": "Spending", "top": 30, "x0": 30},
        {"text": "$173.45", "top": 30, "x0": 40},
        # Line 4: A line without a valid date
        {"text": "Invalid", "top": 40, "x0": 10},
        {"text": "Line", "top": 40, "x0": 20},
        {"text": "$10.00", "top": 40, "x0": 30},
        # Line 5: A line without a valid amount
        {"text": "01/18/24", "top": 50, "x0": 10},
        {"text": "No", "top": 50, "x0": 20},
        {"text": "Amount", "top": 50, "x0": 30},
    ]
    mock_page.extract_words.return_value = words

    result = parse_bofa_page(mock_page)

    assert len(result) == 2
    assert result[0] == {
        "date": date(2024, 1, 15),
        "description": "Some Transaction",
        "amount": 123.45,
    }
    assert result[1] == {
        "date": date(2024, 1, 16),
        "description": "Another One",
        "amount": -50.00,
    }


@patch("expense_tracker.utils.extract.pdfplumber.open")
def test_parse_bofa_statement_pdf(mock_pdfplumber_open):
    # Create mock pages
    mock_page1 = Mock()
    mock_page1.extract_words.return_value = [
        {"text": "01/15/24", "top": 10, "x0": 10},
        {"text": "Transaction", "top": 10, "x0": 20},
        {"text": "1", "top": 10, "x0": 30},
        {"text": "$10.00", "top": 10, "x0": 40},
    ]

    mock_page2 = Mock()
    mock_page2.extract_words.return_value = [
        {"text": "01/16/24", "top": 20, "x0": 10},
        {"text": "Transaction", "top": 20, "x0": 20},
        {"text": "2", "top": 20, "x0": 30},
        {"text": "($20.00)", "top": 20, "x0": 40},
    ]

    # Mock the pdf object and its pages
    mock_pdf = Mock()
    mock_pdf.pages = [mock_page1, mock_page2]

    # The __enter__ method of the context manager should return the mock_pdf
    mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf

    transactions = parse_bofa_statement_pdf("dummy_path.pdf")

    assert len(transactions) == 2
    assert transactions[0]["description"] == "Transaction 1"
    assert transactions[0]["amount"] == 10.00
    assert transactions[1]["description"] == "Transaction 2"
    assert transactions[1]["amount"] == -20.00
    mock_pdfplumber_open.assert_called_with("dummy_path.pdf")
