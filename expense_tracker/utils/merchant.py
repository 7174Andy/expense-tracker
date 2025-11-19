import re
from expense_tracker.core.repository import MerchantCategoryRepository

def normalize_merchant(description: str) -> str:
    description = description.upper()
    
    # Remove digits
    description = re.sub(r'\d+', '', description)

    # Remove extra spaces
    description = re.sub(r'\s+', ' ', description).strip()

    # Remove common trailing for cities
    description = re.sub(r"\b[A-Z]{2}\b$", "", description).strip()
    
    return description

def categorize_merchant(description: str, amount: float, merchant_repo: MerchantCategoryRepository) -> str:
    merchant = normalize_merchant(description)

    # If the amount is positive, it's likely an income, so we can categorize it as "Income"
    if amount > 0:
        return "Income"

    # First try exact match
    category = merchant_repo.get_category(merchant)
    if category:
        return category
    
    # If no exact match, try fuzzy matching
    fuzzy_match = fuzzy_lookup_merchant(merchant, merchant_repo=merchant_repo)
    if fuzzy_match:
        category = merchant_repo.get_category(fuzzy_match)
        if category:
            return category

    return "Other"

def fuzzy_lookup_merchant(merchat: str, threshold: int =90, merchant_repo: MerchantCategoryRepository = None) -> str | None:
    from rapidfuzz import process
    if merchant_repo is None:
        return None
    
    merchants = merchant_repo.get_all_merchants()
    if not merchants:
        return None
    
    best_match, score, _ = process.extractOne(merchat, merchants, score_cutoff=threshold)
    if score >= threshold:
        return best_match
    return None