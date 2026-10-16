"""Phase 1A done-criterion: the validator accepts 30 legal words and rejects 30 illegal ones.

Both lists are hand-written literals. They deliberately do NOT come from scripts/gen_words.py:
if the generator supplied the test corpus, a shared misunderstanding of the phonotactics would
pass silently. The generator's own words are exercised by test_script_roundtrip.py instead.

Each illegal word is paired with the constraint id from spec/phonology.yaml that it must trip,
so the test pins down *why* a word is rejected, not merely that it is.
"""

from __future__ import annotations

import pytest

from tanese_nlp.phonology import spec_load as S
from tanese_nlp.phonology.phonotactics import validate, validate_moras
from tanese_nlp.phonology.romanization import GEM, SYLLABIC, Mora

# --------------------------------------------------------------------------------------
# 30 legal words. Forms only -- none of these is vocabulary (locked decision 14).
# --------------------------------------------------------------------------------------
LEGAL = [
    "a",            # a single word-initial vowel: the whole word is one carrier mora
    "ii",           # carrier + length
    "kana",         # the baseline two-syllable shape
    "kan'a",        # moraic n before a vowel, with the required apostrophe
    "kan'ya",       # moraic n before y
    "kan'wa",       # moraic n before w
    "kaa",          # identical adjacent vowels are one long vowel
    "kaaka",        # long vowel followed by an ordinary onset
    "kaan",         # long vowel closed by the moraic n
    "kanna",        # moraic n + /n/, never a geminate
    "kannha",       # moraic n + retroflex nasal
    "kantha",       # moraic n before a retroflex plosive
    "kanha",        # the digraph nh as a single onset
    "katha",        # the digraph th as a single onset
    "madhu",        # the digraph dh
    "pata",         # minimal pair with the next entry
    "bata",         # ... showing the voicing contrast
    "kaththa",      # geminate retroflex: the full onset spelling repeated
    "kassa",        # geminate fricative
    "kalla",        # geminate lateral
    "oppa",         # word-initial vowel then a geminate
    "tomon",        # word-final moraic n
    "ennu",         # carrier, moraic n, then an onset
    "irumi",        # word-initial carrier mora
    "wiru",         # wi is legal; only wu is a gap
    "yume",         # ye/yu/ya/yo are legal; only yi is a gap
    "nhoori",       # retroflex nasal onset plus a long vowel
    "dhiithe",      # retroflex voiced plosive plus a long vowel
    "gunto",        # moraic n before a plain plosive needs no apostrophe
    "sanmo",        # moraic n before a nasal onset: still no apostrophe needed
]

# --------------------------------------------------------------------------------------
# 30 illegal words, each with the constraint it must break.
# --------------------------------------------------------------------------------------
ILLEGAL = [
    ("", "PT-002"),             # the empty string is not a word
    ("kaza", "PT-001"),         # z is not in the alphabet
    ("KAna", "PT-001"),         # the romanization is lowercase-only
    ("ka1", "PT-001"),          # digits are not letters
    ("kta", "PT-003"),          # initial cluster
    ("sk", "PT-003"),           # cluster with no vowel at all
    ("haka", "PT-003"),         # h is a diacritic letter and never begins a mora
    ("kah", "PT-003"),          # ... including word-finally
    ("kaddha", "PT-003"),       # d doubled before the digraph dh is not a geminate
    ("kanhka", "PT-003"),       # retroflex nasal with no vowel after it
    ("kannta", "PT-003"),       # two moraic n in a row
    ("kakk", "PT-003"),         # a geminate's first half with nothing to double
    ("kak", "PT-004"),          # word-final consonant other than n
    ("kap", "PT-004"),
    ("nka", "PT-005"),          # a word may not open with the moraic n
    ("kka", "PT-005"),          # ... nor with a gemination mora
    ("kamma", "PT-007"),        # m is not geminable
    ("kanhnha", "PT-007"),      # nor is the retroflex nasal
    ("karra", "PT-007"),        # nor the tap
    ("kayya", "PT-007"),        # nor the glides
    ("kawwa", "PT-007"),
    ("kaia", "PT-008"),         # word-internal hiatus
    ("ia", "PT-008"),           # hiatus with nothing else in the word
    ("kaaia", "PT-008"),        # hiatus after a long vowel
    ("thaen", "PT-008"),        # hiatus between two different vowels
    ("kaaa", "PT-009"),         # a vowel may be lengthened only once
    ("kanya", "PT-010"),        # moraic n before y without the apostrophe
    ("kanwa", "PT-010"),        # ... or before w
    ("ka'na", "PT-011"),        # apostrophe not after a moraic n
    ("kan'ta", "PT-011"),       # apostrophe not before a vowel, y or w
]


def test_counts_match_the_done_criteria():
    """docs/SPEC.md Phase 1A asks for 30 of each; keep the lists honest about their size."""
    assert len(LEGAL) == 30
    assert len(ILLEGAL) == 30
    assert len(set(LEGAL)) == 30
    assert len({word for word, _ in ILLEGAL}) == 30
    assert not set(LEGAL) & {word for word, _ in ILLEGAL}


@pytest.mark.parametrize("word", LEGAL)
def test_legal_words_are_accepted(word):
    result = validate(word)
    assert result.ok, str(result)
    assert result.moras


@pytest.mark.parametrize(("word", "code"), ILLEGAL, ids=[w or "<empty>" for w, _ in ILLEGAL])
def test_illegal_words_are_rejected_for_the_right_reason(word, code):
    result = validate(word)
    assert not result.ok, f"{word!r} was accepted but should break {code}"
    assert code in result.codes, f"{word!r} broke {result.codes}, expected {code}"


@pytest.mark.parametrize(("word", "code"), ILLEGAL, ids=[w or "<empty>" for w, _ in ILLEGAL])
def test_every_reported_code_is_a_real_constraint(word, code):
    """A violation code that is not in spec/phonology.yaml would be unexplainable."""
    for violation in validate(word).violations:
        assert violation.code in S.constraint_ids()


def test_mora_counts_follow_the_locked_mora_based_phonology():
    """Locked decision 10: length and the moraic n are moras of their own."""
    assert validate("kana").mora_count == 2
    assert validate("kaa").mora_count == 2       # ka + length
    assert validate("kan'a").mora_count == 3     # ka + n + a
    assert validate("kaththa").mora_count == 3   # ka + gem + tha
    assert validate("kaaka").mora_count == 3     # ka + length + ka


def test_ill_formed_geminates_are_rejected():
    """PT-006, which no romanized string can express -- see validate_moras' docstring.

    A geminate's spelling is the onset repeated, so the lexer can only ever build a gemination
    mora that is followed by a matching onset. These sequences are reachable from the script
    side, where a glyph sequence is given directly, so the constraint is checked at mora level.
    """
    ka = Mora(SYLLABIC, "k", "a")
    ta = Mora(SYLLABIC, "t", "a")

    word_final = validate_moras([ka, Mora(GEM, onset="t")])
    assert not word_final.ok
    assert "PT-006" in word_final.codes

    mismatched = validate_moras([ka, Mora(GEM, onset="k"), ta])
    assert not mismatched.ok
    assert "PT-006" in mismatched.codes

    # The well-formed counterpart, so the test cannot pass by rejecting everything.
    assert validate_moras([ka, Mora(GEM, onset="t"), ta]).ok


def test_every_constraint_in_the_spec_is_exercised_by_this_file():
    """A constraint nobody tests is a constraint nobody has checked."""
    covered = {code for _, code in ILLEGAL} | {
        "PT-006",  # test_ill_formed_geminates_are_rejected
        "PT-012",  # test_gaps_are_rejected_wherever_they_appear
    }
    untested = S.constraint_ids() - covered
    assert not untested, f"constraints with no test: {sorted(untested)}"


def test_gaps_are_rejected_wherever_they_appear():
    """PT-012: the yi/wu gaps, generated from the spec rather than spelled out here."""
    for onset, vowel in sorted(S.gaps(), key=lambda pair: (pair[0] or "", pair[1])):
        word = f"ka{onset or ''}{vowel}"
        result = validate(word)
        assert not result.ok, f"{word!r} contains the gap {onset}{vowel} but was accepted"
        assert "PT-012" in result.codes, f"{word!r} broke {result.codes}"
