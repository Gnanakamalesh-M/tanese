"""Tanese phonology: the romanization lexer and the phonotactic validator.

Public API:
    validate(word) -> Result          is this a legal Tanese word, and if not, why
    is_legal(word) -> bool            boolean shorthand
    parse_roman(word) -> moras, viol  romanized string -> mora sequence
    moras_to_roman(moras) -> str      the inverse
"""

from tanese_nlp.phonology.phonotactics import Result, is_legal, validate
from tanese_nlp.phonology.romanization import (
    GEM,
    LENGTH,
    NASAL,
    SYLLABIC,
    Mora,
    Violation,
    moras_to_roman,
    parse_roman,
)

__all__ = [
    "GEM",
    "LENGTH",
    "NASAL",
    "SYLLABIC",
    "Mora",
    "Result",
    "Violation",
    "is_legal",
    "moras_to_roman",
    "parse_roman",
    "validate",
]
