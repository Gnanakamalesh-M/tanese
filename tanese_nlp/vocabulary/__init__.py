"""Tanese vocabulary rules: root shapes, strata, compounds and loanword adaptation.

Public API:
    adapt(segments, source_word) -> Adapted | Rejected   source sounds -> a Tanese form
    check_all() -> list[str]                             are the vocabulary rules consistent
    load_rules() -> tuple[Rule, ...]                     the VR-* rules
"""

from tanese_nlp.vocabulary.consistency import CHECKS, check_all, stats
from tanese_nlp.vocabulary.loanwords import Adapted, Rejected, Result, adapt
from tanese_nlp.vocabulary.rules import Example, Rule, load_rules

__all__ = [
    "CHECKS",
    "Adapted",
    "Example",
    "Rejected",
    "Result",
    "Rule",
    "adapt",
    "check_all",
    "load_rules",
    "stats",
]
