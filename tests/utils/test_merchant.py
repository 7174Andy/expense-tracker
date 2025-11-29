import pytest
from unittest.mock import MagicMock
from expense_tracker.core.models import MerchantCategory
from expense_tracker.utils.merchant_normalizer import (
    normalize_merchant,
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
        "STARBUCKS": MerchantCategory("STARBUCKS", "Coffee"),
        "MCDONALDS": MerchantCategory("MCDONALDS", "Fast Food"),
        "TRADER JOE'S": MerchantCategory("TRADER JOE'S", "Groceries"),
        "NETFLIX": MerchantCategory("NETFLIX", "Subscriptions"),
    }

    def get_category(merchant: str) -> MerchantCategory | None:
        return merchants.get(merchant)

    repo.get_category.side_effect = get_category
    repo.get_all_merchants.return_value = list(merchants.values())
    return repo
