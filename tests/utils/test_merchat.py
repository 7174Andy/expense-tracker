import pytest
from unittest.mock import MagicMock
from expense_tracker.utils.merchant import (
    normalize_merchant,
    categorize_merchant,
    fuzzy_lookup_merchant,
)

# Tests for normalize_merchant
@pytest.mark.parametrize(
    "input_str, expected_str",
    [
        ("  whole foods  ", "WHOLE FOODS"),
        ("7-eleven 123", "-ELEVEN"),
        ("  starbucks   coffee  ", "STARBUCKS COFFEE"),
        ("some store CA", "SOME STORE"),
        ("GREATCLIPS NH", "GREATCLIPS"),
        ("  trader joe's #456  NY  ", "TRADER JOE'S"),
        ("AMAZON.COM", "AMAZON.COM"),
        ("some store tx", "SOME STORE"),
        ("TARGET T- AUSTIN TX", "TARGET T- AUSTIN"),
        ("IN-N-OUT BURGER", "IN-N-OUT BURGER"),
        ("PURCHASE 0924 UBER * PENDING San FranciscoCA", "UBER SAN FRANCISCOCA"),
        ("MOBILE PURCHASE 0928 VONS #2012 SAN DIEGO", "VONS SAN DIEGO"),
        ("MOBILE PURCHASE 1001 SQ *THE BELLA La Jolla", "SQ THE BELLA LA JOLLA"),
    ],
)
def test_normalize_merchant(input_str, expected_str):
    """Test the normalize_merchant function with various inputs."""
    assert normalize_merchant(input_str) == expected_str


# Mocks and fixtures for dependent services
@pytest.fixture
def mock_repo() -> MagicMock:
    """Fixture for a mocked MerchantCategoryRepository."""
    repo = MagicMock()
    merchants = {
        "STARBUCKS": "Coffee",
        "MCDONALDS": "Fast Food",
        "TRADER JOE'S": "Groceries",
        "NETFLIX": "Subscriptions",
    }

    def get_category(merchant: str) -> str | None:
        return merchants.get(merchant)

    repo.get_category.side_effect = get_category
    repo.get_all_merchants.return_value = list(merchants.keys())
    return repo


# Tests for categorize_merchant
def test_categorize_merchant_income(mock_repo: MagicMock):
    """Test that positive amounts are categorized as Income."""
    assert categorize_merchant("PAYCHECK", 1000.0, mock_repo) == "Income"
    mock_repo.get_category.assert_not_called()
    mock_repo.get_all_merchants.assert_not_called()


def test_categorize_merchant_exact_match(mock_repo: MagicMock):
    """Test categorization with an exact merchant match."""
    assert categorize_merchant("Starbucks", -5.0, mock_repo) == "Coffee"
    mock_repo.get_category.assert_called_once_with("STARBUCKS")


def test_categorize_merchant_normalized_exact_match(mock_repo: MagicMock):
    """Test categorization with a match after normalization."""
    assert categorize_merchant("  trader joe's #123 NY ", -50.0, mock_repo) == "Groceries"
    mock_repo.get_category.assert_called_once_with("TRADER JOE'S")

def test_categorize_merchant_fuzzy_match(mock_repo: MagicMock):
    """Test categorization with a fuzzy merchant match."""
    # Make get_category only return a value for the "correct" fuzzy match
    mock_repo.get_category.side_effect = lambda m: "Coffee" if m == "STARBUCKS" else None
    
    assert categorize_merchant("Starbuck", -5.0, mock_repo) == "Coffee"
    
    # It should have tried an exact match on the normalized input first
    mock_repo.get_category.assert_any_call("STARBUCK")
    # Then, after fuzzy lookup, it should have tried to get the category for the best match
    mock_repo.get_category.assert_any_call("STARBUCKS")
    mock_repo.get_all_merchants.assert_called_once()


def test_categorize_merchant_no_match(mock_repo: MagicMock):
    """Test categorization when no match is found."""
    mock_repo.get_category.return_value = None
    assert categorize_merchant("Unknown Place", -20.0, mock_repo) == "Other"
    mock_repo.get_category.assert_called_once_with("UNKNOWN PLACE")
    mock_repo.get_all_merchants.assert_called_once()


def test_categorize_merchant_fuzzy_lookup_returns_none(mock_repo: MagicMock):
    """Test that it returns 'Other' if fuzzy lookup finds nothing."""
    mock_repo.get_category.return_value = None
    mock_repo.get_all_merchants.return_value = ["A", "B", "C"] # No close matches
    assert categorize_merchant("XYZ Corp", -10.0, mock_repo) == "Other"


def test_categorize_merchant_zero_amount(mock_repo: MagicMock):
    """Test that zero amount transactions are categorized normally."""
    assert categorize_merchant("Netflix", 0.0, mock_repo) == "Subscriptions"
    mock_repo.get_category.assert_called_once_with("NETFLIX")

# Tests for fuzzy_lookup_merchant
def test_fuzzy_lookup_merchant_no_repo():
    """Test fuzzy lookup with no repository provided."""
    assert fuzzy_lookup_merchant("STARBUCK") is None


def test_fuzzy_lookup_merchant_empty_merchant_list(mock_repo: MagicMock):
    """Test fuzzy lookup with an empty list of merchants."""
    mock_repo.get_all_merchants.return_value = []
    assert fuzzy_lookup_merchant("STARBUCK", merchant_repo=mock_repo) is None
    mock_repo.get_all_merchants.assert_called_once()


def test_fuzzy_lookup_merchant_good_match(mock_repo: MagicMock):
    """Test fuzzy lookup with a good match."""
    assert fuzzy_lookup_merchant("STARBUCK", merchant_repo=mock_repo) == "STARBUCKS"
    mock_repo.get_all_merchants.assert_called_once()


def test_fuzzy_lookup_merchant_below_threshold(mock_repo: MagicMock):
    """Test fuzzy lookup when the best match is below the score threshold."""
    assert fuzzy_lookup_merchant("SBUX", threshold=95, merchant_repo=mock_repo) is None
    mock_repo.get_all_merchants.assert_called_once()

def test_fuzzy_lookup_merchant_no_close_match(mock_repo: MagicMock):
    """Test fuzzy lookup with no reasonably close matches."""
    assert fuzzy_lookup_merchant("COMPLETELY UNKNOWN", merchant_repo=mock_repo) is None
    mock_repo.get_all_merchants.assert_called_once()

def test_fuzzy_lookup_merchant_exact_match(mock_repo: MagicMock):
    """Test that an exact match is returned correctly by fuzzy lookup."""
    assert fuzzy_lookup_merchant("STARBUCKS", merchant_repo=mock_repo) == "STARBUCKS"
