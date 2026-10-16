"""Phase 1A done-criterion: roman -> script -> roman on 200 generated legal words.

Both script forms are tested: the canonical dot-joined id sequence and the Private Use Area
string. The generator asserts its own coverage (see scripts/gen_words.py), so a pass here
means the whole glyph table round-trips, not just the common moras.
"""

from __future__ import annotations

import pytest

from scripts.gen_words import generate
from tanese_nlp.phonology import spec_load as S
from tanese_nlp.phonology.phonotactics import validate
from tanese_nlp.script.convert import (
    pua_to_roman,
    roman_to_pua,
    roman_to_script,
    script_to_roman,
)

WORDS = generate(200)


def test_the_corpus_is_the_size_the_done_criteria_ask_for():
    assert len(WORDS) == 200
    assert len(set(WORDS)) == 200


def test_the_corpus_is_deterministic():
    """Same seed, same words -- otherwise a CI failure could not be reproduced locally."""
    assert generate(200) == WORDS


@pytest.mark.parametrize("word", WORDS)
def test_every_generated_word_is_legal(word):
    result = validate(word)
    assert result.ok, str(result)


@pytest.mark.parametrize("word", WORDS)
def test_id_roundtrip(word):
    assert script_to_roman(roman_to_script(word)) == word


@pytest.mark.parametrize("word", WORDS)
def test_pua_roundtrip(word):
    assert pua_to_roman(roman_to_pua(word)) == word


@pytest.mark.parametrize("word", WORDS)
def test_one_glyph_per_mora(word):
    """Locked decision 13: one id per mora, so the two counts must agree."""
    moras = validate(word).moras
    assert len(roman_to_script(word).split(".")) == len(moras)
    assert len(roman_to_pua(word)) == len(moras)


def test_the_corpus_covers_the_whole_glyph_table():
    """A round-trip over 200 words proves little if it only touches the frequent moras."""
    used = {mora.glyph for word in WORDS for mora in validate(word).moras}
    assert used == set(S.legal_mora_ids())


def test_no_two_moras_share_a_glyph_id():
    seen: dict[str, str] = {}
    for word in WORDS:
        for mora in validate(word).moras:
            key = f"{mora.kind}:{mora.onset or ''}{mora.vowel or ''}"
            if mora.kind == "syllabic":
                assert seen.setdefault(mora.glyph, key) == key, mora.glyph
    assert len(seen) == len(set(seen.values()))


def test_illegal_words_have_no_script_form():
    """A word that is not Tanese must fail loudly rather than produce plausible glyphs."""
    for word in ("kaia", "kanya", "kta", ""):
        with pytest.raises(ValueError):
            roman_to_script(word)
        with pytest.raises(ValueError):
            roman_to_pua(word)


def test_unknown_glyphs_are_rejected():
    with pytest.raises(ValueError):
        script_to_roman("TS-KA.TS-NOPE")
    with pytest.raises(ValueError):
        pua_to_roman("ka")
    with pytest.raises(ValueError):
        script_to_roman("")
