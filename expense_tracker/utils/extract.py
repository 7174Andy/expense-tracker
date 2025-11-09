import pdfplumber
import re
from datetime import datetime

DATE_RX   = re.compile(r"^\d{2}/\d{2}/\d{2}$")
AMOUNT_RX = re.compile(r"^(?:-?\$?\s?\d[\d,]*\.?\d{0,2}|\(-?\$?\s?\d[\d,]*\.?\d{0,2}\))$")

def parse_bofa_page(page):
    """Rebuild rows by grouping words by y-position instead of trusting pdfplumber's table."""
    # group words by y-position
    words = page.extract_words(use_text_flow=True) or []
    lines = {}

    # group nearby words into lines
    for w in words:
        ykey = round(w["top"] / 2) * 2   # 2-point vertical tolerance
        lines.setdefault(ykey, []).append(w)

    rows = []
    for _, wline in sorted(lines.items()):
        # sort words by x-position and extract text
        wline.sort(key=lambda w: w["x0"])

        # extract tokens and filter out empty ones
        tokens = [w["text"].strip() for w in wline if w["text"].strip()]

        # filter out irrelevant rows
        if len(tokens) < 3: 
            continue

        # must begin with a date and end with an amount
        if not DATE_RX.match(tokens[0]): 
            continue
        amt_idx = next((i for i in range(len(tokens)-1, -1, -1)
                        if AMOUNT_RX.match(tokens[i])), None)
        if amt_idx is None:
            continue
        desc = " ".join(tokens[1:amt_idx])
        if desc.lower().startswith("total "):
            continue
        rows.append({
            "date": _parse_date(tokens[0]),
            "description": desc,
            "amount": _parse_amount(tokens[amt_idx]),
        })
    return rows

def _parse_date(s):
    for fmt in ("%m/%d/%y", "%m/%d/%Y"):
        try: 
            return datetime.strptime(s, fmt).date().isoformat()
        except Exception:
            pass
    return s

def _parse_amount(s: str) -> float:
    s = s.replace("$", "").replace(",", "").strip()
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    val = float(s) if s else 0.0
    return -val if neg else val

def parse_bofa_statement_pdf(path: str) -> list[dict]:
    rows = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            rows.extend(parse_bofa_page(page))
    return rows