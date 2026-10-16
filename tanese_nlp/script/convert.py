"""Romanized Tanese <-> Tanese script.

Locked decision 12 makes the romanization canonical and the script a mapping layer on top,
so every conversion goes through the mora sequence from tanese_nlp.phonology: there is no
direct letter-to-glyph table to drift out of sync.

Two script forms, both round-trippable:

    ids  'kaatha' <-> 'TS-KA.TS-LONG.TS-THA'   canonical, readable, diffable in YAML
    pua  'kaatha' <-> ''     one character per mora, for Phase 6 rendering

Illegal input raises ValueError rather than silently producing a wrong glyph string: a word
that is not Tanese has no script form, and callers that want the reason should validate
first.
"""

from __future__ import annotations

from tanese_nlp.phonology import spec_load as S
from tanese_nlp.phonology.phonotactics import validate
from tanese_nlp.phonology.romanization import (
    GEM,
    LENGTH,
    NASAL,
    SYLLABIC,
    Mora,
    moras_to_roman,
)

ID_SEPARATOR = "."

_KIND_BY_GLYPH = {
    S.LENGTH_GLYPH: LENGTH,
    S.NASAL_GLYPH: NASAL,
    S.GEM_GLYPH: GEM,
}


def _moras_of(word: str) -> list[Mora]:
    result = validate(word)
    if not result.ok:
        raise ValueError(f"not a legal Tanese word: {result}")
    return result.moras


def roman_to_script(word: str) -> str:
    """'kaatha' -> 'TS-KA.TS-LONG.TS-THA'."""
    return ID_SEPARATOR.join(mora.glyph for mora in _moras_of(word))


def roman_to_pua(word: str) -> str:
    """'kaatha' -> the three-character Private Use Area string."""
    pua = S.pua_by_id()
    return "".join(pua[mora.glyph] for mora in _moras_of(word))


def _moras_from_glyphs(glyphs: list[str]) -> list[Mora]:
    table = S.script_glyphs()
    moras: list[Mora] = []
    for index, glyph in enumerate(glyphs):
        entry = table.get(glyph)
        if entry is None:
            raise ValueError(f"{glyph!r} is not a mora id in spec/script.yaml")
        kind = _KIND_BY_GLYPH.get(glyph, SYLLABIC)
        if kind is SYLLABIC:
            onset, vowel = S.split_mora_spelling(entry["mora"])
            moras.append(Mora(SYLLABIC, onset, vowel, position=index))
        elif kind == GEM:
            # The gemination mora carries no segment; its onset is the next mora's.
            following = table.get(glyphs[index + 1]) if index + 1 < len(glyphs) else None
            if following is None or following.get("kind") != SYLLABIC:
                raise ValueError(f"{S.GEM_GLYPH} at {index} is not followed by a syllabic mora")
            onset, _ = S.split_mora_spelling(following["mora"])
            moras.append(Mora(GEM, onset=onset, position=index))
        else:
            moras.append(Mora(kind, position=index))
    return moras


def _finish(moras: list[Mora]) -> str:
    word = moras_to_roman(moras)
    result = validate(word)
    if not result.ok:
        raise ValueError(f"script spells an illegal word {word!r}: {result}")
    return word


def script_to_roman(text: str) -> str:
    """'TS-KA.TS-LONG.TS-THA' -> 'kaatha'."""
    if not text:
        raise ValueError("empty script form")
    return _finish(_moras_from_glyphs(text.split(ID_SEPARATOR)))


def pua_to_roman(text: str) -> str:
    """The Private Use Area form -> 'kaatha'."""
    if not text:
        raise ValueError("empty script form")
    by_pua = S.id_by_pua()
    glyphs = []
    for char in text:
        glyph = by_pua.get(char)
        if glyph is None:
            raise ValueError(f"U+{ord(char):04X} is not a Tanese mora codepoint")
        glyphs.append(glyph)
    return _finish(_moras_from_glyphs(glyphs))
