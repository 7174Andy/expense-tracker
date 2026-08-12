import re
from collections import Counter
from dataclasses import dataclass

import pdfplumber

from expense_tracker.utils.date import parse_date_from_str

AMOUNT_RX = re.compile(
    r"^(?:-?\$?\s?\d[\d,]*\.?\d{0,2}|\(-?\$?\s?\d[\d,]*\.?\d{0,2}\))$"
)

# strftime directives -> regex, for building a profile's leading-date matcher
_DATE_DIRECTIVES = {"%m": r"\d{2}", "%d": r"\d{2}", "%y": r"\d{2}", "%Y": r"\d{4}"}


@dataclass(frozen=True)
class StatementProfile:
    """Parsing rules for one bank AND statement type, e.g. BofA checking.

    A bank issuing several statement types gets several sibling profiles;
    there is deliberately no per-bank grouping level.
    """

    name: str
    detect: tuple[str, ...]  # substrings sought in page-1 text, then metadata
    date_formats: tuple[str, ...]  # must include a year
    skip: tuple[str, ...]  # description prefixes to drop


BOFA_CHECKING = StatementProfile(
    name="BofA Checking",
    detect=("Bank of America",),
    date_formats=("%m/%d/%y",),
    skip=("total ",),
)

# Fallback for unrecognized statements. Never registered in PROFILES: its empty
# `detect` would match everything and shadow every real profile.
GENERIC = StatementProfile(
    name="Generic",
    detect=(),
    date_formats=("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d"),
    skip=("total ",),
)

PROFILES = (BOFA_CHECKING,)


def _date_rx(date_formats: tuple[str, ...]) -> re.Pattern:
    patterns = []
    for fmt in date_formats:
        rx = re.escape(fmt)
        for directive, digits in _DATE_DIRECTIVES.items():
            rx = rx.replace(directive, digits)
        patterns.append(rx)
    return re.compile(f"^(?:{'|'.join(patterns)})$")


def page_lines(page) -> list[list[str]]:
    """Rebuild rows by grouping words by y-position instead of trusting pdfplumber's table.

    The only function that touches the PDF library, so swapping engines is a
    one-function change.
    """
    words = page.extract_words(use_text_flow=True) or []
    lines = {}

    # group nearby words into lines
    for w in words:
        ykey = round(w["top"] / 2) * 2  # 2-point vertical tolerance
        lines.setdefault(ykey, []).append(w)

    rows = []
    for _, wline in sorted(lines.items()):
        # sort words by x-position and extract text
        wline.sort(key=lambda w: w["x0"])

        # extract tokens and filter out empty ones
        tokens = [w["text"].strip() for w in wline if w["text"].strip()]
        if tokens:
            rows.append(tokens)
    return rows


def detect_profile(pdf) -> StatementProfile:
    """Page text outranks metadata.

    Metadata is emitted by the issuing software, so two statement types from one
    bank share it and only page text can tell them apart. Matching metadata first
    would let the less specific signal win and the discriminator never run.
    """
    first_page = pdf.pages[0].extract_text() or "" if pdf.pages else ""
    for profile in PROFILES:
        if any(s in first_page for s in profile.detect):
            return profile

    metadata = " ".join(str(v) for v in (pdf.metadata or {}).values())
    for profile in PROFILES:
        if any(s in metadata for s in profile.detect):
            return profile

    return GENERIC


def remove_boilerplate(pages: list[list[list[str]]]) -> list[list[str]]:
    """Drop lines present on every page - headers and footers, not transactions.

    Counts pages containing a line rather than total occurrences, so a line
    repeated twice on one page of a two-page statement is not mistaken for a
    footer.
    """
    if len(pages) < 2:
        return [line for page in pages for line in page]

    counts = Counter(
        text for page in pages for text in {" ".join(line) for line in page}
    )
    boilerplate = {text for text, n in counts.items() if n == len(pages)}
    return [
        line for page in pages for line in page if " ".join(line) not in boilerplate
    ]


def rows_from_lines(lines: list[list[str]], profile: StatementProfile) -> list[dict]:
    """Interpret token lines as transactions. Takes plain lists, no PDF types."""
    date_rx = _date_rx(profile.date_formats)
    rows = []
    for tokens in lines:
        # filter out irrelevant rows
        if len(tokens) < 3:
            continue

        # must begin with a date and end with an amount
        if not date_rx.match(tokens[0]):
            continue
        amt_idx = next(
            (i for i in range(len(tokens) - 1, -1, -1) if AMOUNT_RX.match(tokens[i])),
            None,
        )
        if amt_idx is None:
            continue
        desc = " ".join(tokens[1:amt_idx])
        if profile.skip and desc.lower().startswith(profile.skip):
            continue
        rows.append(
            {
                "date": parse_date_from_str(tokens[0]),
                "description": desc,
                "amount": _parse_amount(tokens[amt_idx]),
            }
        )
    return rows


def _parse_amount(s: str) -> float:
    s = s.replace("$", "").replace(",", "").strip()
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    val = float(s) if s else 0.0
    return -val if neg else val


def parse_statement(path: str) -> tuple[str, list[dict]]:
    """Parse a statement PDF into (profile name, transactions).

    The profile name is returned so the import preview can show which profile
    was used - seeing "Generic" is the user's cue that the parse may be wrong.
    """
    with pdfplumber.open(path) as pdf:
        profile = detect_profile(pdf)
        pages = [page_lines(page) for page in pdf.pages]
    return profile.name, rows_from_lines(remove_boilerplate(pages), profile)
