"""The romanization must be a one-to-one mapping: one parse per spelling, one spelling per word.

The cases here are the ones that decided the design (see the Phase 1A decisions in
docs/SPEC.md's phase notes and the `ambiguity_cases` block of spec/romanization.yaml): the
retroflex digraphs against the moraic n, `nn` against a geminate n, and identical adjacent
vowels against hiatus. They are written out as literals so the expected parse is visible, and
also cross-checked against the spec file so prose and code cannot drift apart.
"""

from __future__ import annotations

import pytest

from tanese_nlp.phonology import spec_load as S
from tanese_nlp.phonology.phonotactics import validate
from tanese_nlp.phonology.romanization import moras_to_roman, parse_roman

# roman -> the mora ids it must parse to.
PARSES = [
    ("katha", ["TS-KA", "TS-THA"]),
    ("kantha", ["TS-KA", "TS-NASAL", "TS-THA"]),
    ("kanha", ["TS-KA", "TS-NHA"]),
    ("kannha", ["TS-KA", "TS-NASAL", "TS-NHA"]),
    ("kanna", ["TS-KA", "TS-NASAL", "TS-NA"]),
    ("kanma", ["TS-KA", "TS-NASAL", "TS-MA"]),
    ("kanra", ["TS-KA", "TS-NASAL", "TS-RA"]),
    ("kan'a", ["TS-KA", "TS-NASAL", "TS-A"]),
    ("kan'ya", ["TS-KA", "TS-NASAL", "TS-YA"]),
    ("kana", ["TS-KA", "TS-NA"]),
    ("kaa", ["TS-KA", "TS-LONG"]),
    ("kaaka", ["TS-KA", "TS-LONG", "TS-KA"]),
    ("kaatha", ["TS-KA", "TS-LONG", "TS-THA"]),
    ("kaththa", ["TS-KA", "TS-GEM", "TS-THA"]),
    ("kadhdha", ["TS-KA", "TS-GEM", "TS-DHA"]),
    ("kakka", ["TS-KA", "TS-GEM", "TS-KA"]),
    ("kassa", ["TS-KA", "TS-GEM", "TS-SA"]),
]


@pytest.mark.parametrize(("word", "glyphs"), PARSES)
def test_parse_is_what_the_spec_says(word, glyphs):
    moras, violations = parse_roman(word)
    assert not violations, [str(v) for v in violations]
    assert [mora.glyph for mora in moras] == glyphs


@pytest.mark.parametrize(("word", "glyphs"), PARSES)
def test_spelling_is_the_inverse_of_parsing(word, glyphs):
    moras, _ = parse_roman(word)
    assert moras_to_roman(moras) == word


def test_the_nn_contrast_is_real():
    """`kanna` and `kannha` differ only in which nasal the onset is, never in gemination."""
    assert [m.glyph for m in validate("kanna").moras] == ["TS-KA", "TS-NASAL", "TS-NA"]
    assert [m.glyph for m in validate("kannha").moras] == ["TS-KA", "TS-NASAL", "TS-NHA"]
    # A geminate nasal is not merely unspelled, it is illegal: see PT-007.
    assert "PT-007" in validate("kanhnha").codes


def test_identical_adjacent_vowels_are_only_ever_long():
    """`kaa` has no second reading, so /ka.a/ is not expressible -- and does not need to be."""
    assert [m.glyph for m in validate("kaa").moras] == ["TS-KA", "TS-LONG"]
    assert validate("kaa").mora_count == 2
    # Three in a row is over-long rather than long-plus-hiatus.
    assert "PT-009" in validate("kaaa").codes


def test_apostrophe_is_required_and_only_where_the_spec_says():
    assert validate("kan'a").ok
    assert validate("kan'ya").ok
    assert validate("kan'wa").ok
    assert "PT-010" in validate("kanya").codes
    assert "PT-010" in validate("kanwa").codes
    # No apostrophe before an ordinary onset, where there is nothing to disambiguate.
    assert validate("kanta").ok
    assert "PT-011" in validate("kan'ta").codes


def test_ambiguity_cases_in_the_spec_file_match_the_lexer():
    """spec/romanization.yaml documents these parses in prose; they must be the real ones."""
    for case in S.romanization()["ambiguity_cases"]:
        moras, violations = parse_roman(case["roman"])
        assert not violations, f"{case['roman']}: {[str(v) for v in violations]}"
        assert [mora.glyph for mora in moras] == case["moras"], case["roman"]


def test_longest_match_takes_digraphs_first():
    """Without digraph-first matching, `nha` would read as moraic n plus a stray h."""
    for digraph in S.romanization()["retroflex_digraphs"]["pairs"]:
        moras, violations = parse_roman(f"{digraph}a")
        assert not violations
        assert len(moras) == 1
        assert moras[0].onset == digraph


def test_h_never_begins_a_mora():
    """The whole `h`-as-retroflex-marker scheme depends on /h/ not being a phoneme."""
    assert "h" not in S.consonants()
    assert "PT-003" in validate("haka").codes
