from expense_tracker.utils.extract import _parse_date, _parse_amount

def test_parse_date():
    assert _parse_date("11/08/23") == "2023-11-08"
    assert _parse_date("01/01/2024") == "2024-01-01"
    assert _parse_date("invalid-date") == "invalid-date" # Should return original string if parsing fails

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
