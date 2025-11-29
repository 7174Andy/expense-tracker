import re


def normalize_merchant(description: str) -> str:
    """Normalizing the description so that it can be matched against the merchant repository. This includes:
    - Converting to uppercase
    - Removing digits
    - Removing special characters like # and *
    - Removing common trailing city/state abbreviations
    - Removing common words like "PENDING", "MOBILE", "PURCHASE"

    Args:
        description (str): The raw description from the transaction.

    Returns:
        str: The normalized description.
    """
    description = description.upper()

    # Remove digits
    description = re.sub(r"\d+", "", description)

    # Remove just # and *
    description = re.sub(r"[#*]", "", description)

    # Remove PENDI or PENDING
    description = re.sub(r"\bPENDING\b", "", description).strip()
    description = re.sub(r"\bPENDI\b", "", description).strip()

    # Remove MOBILE
    description = re.sub(r"\bMOBILE\b", "", description).strip()

    # Remove PURCHASE
    description = re.sub(r"\bPURCHASE\b", "", description).strip()

    # Remove common trailing for cities
    description = re.sub(r"\b[A-Z]{2}\b$", "", description).strip()

    # Remove extra spaces
    description = re.sub(r"\s+", " ", description).strip()

    return description
