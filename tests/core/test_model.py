from datetime import date
from expense_tracker.core.models import Transaction, MerchantCategory


def test_transaction_creation():
    """Test that a Transaction object can be created with correct values."""
    t = Transaction(
        id=1,
        date=date(2023, 1, 1),
        amount=10.50,
        category="Food",
        description="Lunch",
    )
    assert t.id == 1
    assert t.date == date(2023, 1, 1)
    assert t.amount == 10.50
    assert t.category == "Food"
    assert t.description == "Lunch"


def test_merchant_category_creation():
    """Test that a MerchantCategory object can be created with correct values."""
    mc = MerchantCategory(
        merchant_key="amazon",
        category="Shopping",
    )
    assert mc.merchant_key == "amazon"
    assert mc.category == "Shopping"
