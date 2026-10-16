"""Load spec/phonology.yaml, spec/romanization.yaml and spec/script.yaml.

Every derived set in this module (the vowel list, the geminable consonants, the legal mora
inventory, the glyph ids) is computed from those files, never hardcoded here. That is what
lets Phase 1B+ change a phoneme or a gap in one place and have the validator, the converter,
the word generator and the tests all follow.

This module reads spec/ only. It never touches data/evaluation/ -- no answer-key leakage.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SPEC_DIR = REPO_ROOT / "spec"

# A mora with no onset: spelled as the bare vowel, written with the carrier glyph.
NO_ONSET = None

GLYPH_PREFIX = "TS-"
LENGTH_GLYPH = f"{GLYPH_PREFIX}LONG"
NASAL_GLYPH = f"{GLYPH_PREFIX}NASAL"
GEM_GLYPH = f"{GLYPH_PREFIX}GEM"
MARK_GLYPHS = (LENGTH_GLYPH, NASAL_GLYPH, GEM_GLYPH)


def _load(name: str) -> dict[str, Any]:
    document = yaml.safe_load((SPEC_DIR / name).read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"spec/{name}: expected a mapping at the top level")
    return document


@cache
def phonology() -> dict[str, Any]:
    return _load("phonology.yaml")


@cache
def romanization() -> dict[str, Any]:
    return _load("romanization.yaml")


@cache
def script() -> dict[str, Any]:
    return _load("script.yaml")


@cache
def vowels() -> tuple[str, ...]:
    """Vowel graphemes, in spec order."""
    return tuple(entry["id"] for entry in phonology()["vowels"])


@cache
def consonants() -> dict[str, dict[str, Any]]:
    """Consonant graphemes mapped to their full spec entry, in spec order."""
    return {entry["id"]: entry for entry in phonology()["consonants"]}


@cache
def geminable() -> frozenset[str]:
    return frozenset(key for key, entry in consonants().items() if entry["geminable"])


@cache
def letters() -> frozenset[str]:
    return frozenset(romanization()["alphabet"]["letters"])


@cache
def separator() -> str:
    return romanization()["alphabet"]["separator"]


@cache
def consonant_graphemes_longest_first() -> tuple[str, ...]:
    """Consonant spellings ordered so a longest-match lexer takes digraphs first."""
    return tuple(sorted(consonants(), key=lambda g: (-len(g), g)))


@cache
def gaps() -> frozenset[tuple[str | None, str]]:
    """Syllabic moras that the phonology declares illegal, as (onset, vowel) pairs."""
    pairs: set[tuple[str | None, str]] = set()
    for entry in phonology()["gaps"]:
        pairs.add(split_mora_spelling(entry["mora"]))
    return frozenset(pairs)


def split_mora_spelling(spelling: str) -> tuple[str | None, str]:
    """Split a syllabic mora's spelling, e.g. 'yi' -> ('y', 'i'), 'a' -> (None, 'a')."""
    vowel = spelling[-1]
    if vowel not in vowels():
        raise ValueError(f"{spelling!r} does not end in a vowel grapheme")
    onset = spelling[:-1] or NO_ONSET
    if onset is not NO_ONSET and onset not in consonants():
        raise ValueError(f"{spelling!r} does not start with a consonant grapheme")
    return onset, vowel


@cache
def legal_syllabic_moras() -> tuple[tuple[str | None, str], ...]:
    """Every legal (onset, vowel) pair: all onsets including none, less the declared gaps."""
    onsets: list[str | None] = [NO_ONSET, *consonants()]
    return tuple(
        (onset, vowel)
        for onset in onsets
        for vowel in vowels()
        if (onset, vowel) not in gaps()
    )


def glyph_id(onset: str | None, vowel: str) -> str:
    """The script.yaml id of a syllabic mora, e.g. ('th', 'a') -> 'TS-THA'."""
    return f"{GLYPH_PREFIX}{'' if onset is NO_ONSET else onset.upper()}{vowel.upper()}"


@cache
def legal_mora_ids() -> frozenset[str]:
    """The complete set of mora ids the script table must contain, derived from the spec."""
    return frozenset(
        [glyph_id(onset, vowel) for onset, vowel in legal_syllabic_moras()] + list(MARK_GLYPHS)
    )


@cache
def script_glyphs() -> dict[str, dict[str, Any]]:
    """script.yaml's mora table, keyed by id."""
    return {entry["id"]: entry for entry in script()["moras"]}


@cache
def pua_by_id() -> dict[str, str]:
    """Mora id -> its Private Use Area character."""
    return {
        entry["id"]: chr(int(entry["pua"].removeprefix("U+"), 16))
        for entry in script()["moras"]
    }


@cache
def id_by_pua() -> dict[str, str]:
    return {char: glyph for glyph, char in pua_by_id().items()}


@cache
def constraint_ids() -> frozenset[str]:
    return frozenset(entry["id"] for entry in phonology()["constraints"])
