from dataclasses import dataclass
from datetime import date

@dataclass
class Transaction:
    id: int | None
    date: date
    amount: float
    category: str
    description: str

@dataclass
class MerchantCategory:
    merchant_key: str
    category: str