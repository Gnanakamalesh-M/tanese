"""The loanword adapter, one test per declared rule.

The expected outputs live in spec/vocabulary_rules.yaml, hand-derived from the repair steps,
so these tests assert the code agrees with the spec rather than recording whatever the code
happens to do. Each substitution, each deliberately unmapped sound, each worked example and
each required rejection gets its own test, so a failure names the rule that broke.
"""

from __future__ import annotations

import pytest

from tanese_nlp.phonology import spec_load as S
from tanese_nlp.phonology.phonotactics import validate
from tanese_nlp.vocabulary import loanwords as L
from tanese_nlp.vocabulary import rules as V

SUBSTITUTIONS = V.document()["loan_substitutions"]
UNMAPPED = V.document()["unmapped"]
EXAMPLES = V.adaptation_examples()
REJECTIONS = V.adaptation_rejections()


# --------------------------------------------------------------------------------------
# the substitution table
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("entry", SUBSTITUTIONS, ids=lambda e: e["source"])
def test_substitution_target_is_made_of_real_graphemes(entry: dict):
    graphemes = set(S.vowels()) | set(S.consonants())
    for grapheme in L.split_graphemes(entry["tanese"]):
        assert grapheme in graphemes, (
            f"{entry['source']!r} -> {entry['tanese']!r} uses {grapheme!r}, which is not in "
            f"spec/phonology.yaml"
        )


@pytest.mark.parametrize("entry", SUBSTITUTIONS, ids=lambda e: e["source"])
def test_substitution_applies_in_a_word(entry: dict):
    """Each mapped sound, used between a legal onset and a legal vowel, adapts cleanly."""
    result = L.adapt(["k", "a", entry["source"], "a"], f"ka{entry['source']}a")
    assert result.ok, f"{entry['source']!r} should be adaptable: {result}"
    assert validate(result.form).ok


def test_the_digraph_consonants_are_not_split_into_characters():
    """`th` is one consonant. Splitting it would produce a `t` plus a non-existent `h`."""
    assert L.split_graphemes("th") == ["th"]
    assert L.split_graphemes("thatha") == ["th", "a", "th", "a"]
    assert L.split_graphemes("aa") == ["a", "a"]


def test_h_is_deleted_rather_than_substituted():
    """There is no /h/ phoneme, and every candidate substitute is further off than silence."""
    assert V.substitutions()["h"] == ""
    result = L.adapt(["h", "o", "t", "e", "l"], "hotel")
    assert result.ok
    assert result.form == "otelu"


# --------------------------------------------------------------------------------------
# sounds that must be refused
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("entry", UNMAPPED, ids=lambda e: e["source"])
def test_unmapped_sound_is_rejected_by_name(entry: dict):
    result = L.adapt(["k", "a", entry["source"]], f"ka{entry['source']}")
    assert not result.ok, (
        f"{entry['source']!r} is declared unmapped but was adapted to {result.form!r}"
    )
    assert result.code == entry["code"]
    assert result.offending == entry["source"], "the rejection must name the offending sound"


@pytest.mark.parametrize("entry", UNMAPPED, ids=lambda e: e["source"])
def test_unmapped_sound_is_not_also_mapped(entry: dict):
    assert entry["source"] not in V.substitutions(), (
        "a sound is either mapped or deliberately unmapped, never both"
    )


def test_an_unlisted_sound_is_rejected_as_unknown():
    result = L.adapt(["k", "a", "zzz"], "kazzz")
    assert not result.ok
    assert result.code == V.UNKNOWN
    assert result.offending == "zzz"


def test_a_rejection_names_the_first_offending_sound_only():
    """Two bad sounds give one rejection, so the message points somewhere specific."""
    result = L.adapt(["sh", "a", "ch"], "sh-a-ch")
    assert not result.ok
    assert result.offending == "sh"


# --------------------------------------------------------------------------------------
# the worked examples -- the edge shapes
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("entry", EXAMPLES, ids=lambda e: e["source_word"])
def test_adaptation_matches_the_expected_output(entry: dict):
    result = L.adapt(entry["segments"], entry["source_word"])
    assert result.ok, f"{entry['source_word']!r} was rejected: {result}"
    assert result.form == entry["expect"]


@pytest.mark.parametrize("entry", EXAMPLES, ids=lambda e: e["source_word"])
def test_adaptation_fires_the_declared_steps(entry: dict):
    result = L.adapt(entry["segments"], entry["source_word"])
    assert list(result.steps_fired) == entry["steps_fired"]


@pytest.mark.parametrize("entry", EXAMPLES, ids=lambda e: e["source_word"])
def test_adaptation_output_is_a_legal_word(entry: dict):
    assert validate(entry["expect"]).ok


@pytest.mark.parametrize("entry", REJECTIONS, ids=lambda e: e["source_word"])
def test_declared_rejection_is_refused_with_the_right_code(entry: dict):
    result = L.adapt(entry["segments"], entry["source_word"])
    assert not result.ok, f"{entry['source_word']!r} should be refused, got {result.form!r}"
    assert result.code == entry["code"]
    assert result.offending == entry["offending"]


# The five edge shapes the repair steps exist for, asserted by name so a regression says
# which repair broke rather than only which word changed.


def test_film_breaks_a_final_cluster_and_keeps_the_nasal_as_a_coda():
    result = L.adapt(["f", "i", "l", "m"], "film")
    assert result.form == "pilun"
    assert "LR-2-NASAL" in result.steps_fired
    assert "LR-5-EPENTHESIS" in result.steps_fired


def test_strike_takes_epenthesis_twice_and_avoids_the_yi_gap():
    result = L.adapt(["s", "t", "r", "a", "i", "k"], "strike")
    assert result.form == "suturawiku"
    assert "awi" in result.form, "the default glide `y` would make the gap mora `yi`"
    assert "ayi" not in result.form


def test_bank_absorbs_the_nasal_instead_of_inserting_a_vowel():
    result = L.adapt(["b", "a", "n", "k"], "bank")
    assert result.form == "banku"
    assert result.form != "banuku", "a nasal before a stop becomes the moraic n"


def test_a_retroflex_coda_takes_a_not_u():
    result = L.adapt(["k", "o", "t_retro"], "koT")
    assert result.form == "kotha"
    assert result.form != "kothu", "a retroflex into a high back vowel is an unstable join"


def test_a_geminable_pair_becomes_a_geminate_and_a_non_geminable_one_does_not():
    geminable = L.adapt(["p", "a", "t_retro", "t_retro", "u"], "paTTu")
    assert geminable.form == "paththu"
    assert "LR-3-GEMINATE" in geminable.steps_fired

    # `n` is not geminable (constraint PT-007), so the pair falls through to LR-2.
    nasal = L.adapt(["a", "n", "n", "a"], "anna")
    assert nasal.form == "anna"
    assert "LR-3-GEMINATE" not in nasal.steps_fired
    assert "LR-2-NASAL" in nasal.steps_fired

    # `r` is not geminable either, and is not a nasal, so LR-5 breaks it up.
    rhotic = L.adapt(["k", "a", "r", "r", "a"], "karra")
    assert rhotic.form == "karura"
    assert "LR-5-EPENTHESIS" in rhotic.steps_fired


# --------------------------------------------------------------------------------------
# determinism and totality
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("entry", EXAMPLES, ids=lambda e: e["source_word"])
def test_adaptation_is_deterministic(entry: dict):
    first = L.adapt(entry["segments"], entry["source_word"])
    second = L.adapt(entry["segments"], entry["source_word"])
    assert first.form == second.form
    assert first.steps_fired == second.steps_fired


def test_a_word_initial_nasal_is_not_turned_into_a_coda():
    """Constraint PT-005: an initial moraic nasal has nothing to attach to."""
    result = L.adapt(["n", "t", "a"], "nta")
    assert result.ok
    assert result.form == "nuta"


def test_a_long_vowel_survives_and_is_not_over_lengthened():
    assert L.adapt(["k", "a:", "r"], "kaar").form == "kaaru"
    # Three identical vowels would break constraint PT-009, so the run is truncated.
    assert L.adapt(["k", "a", "a", "a"], "kaaa").form == "kaa"


def test_an_onset_n_before_a_vowel_stays_an_onset():
    """`kana` is /ka.na/; only a moraic n takes the apostrophe."""
    assert L.adapt(["k", "a", "n", "a"], "kana").form == "kana"


@pytest.mark.parametrize("entry", list(EXAMPLES) + list(REJECTIONS), ids=lambda e: e["source_word"])
def test_the_adapter_never_returns_an_unvalidated_form(entry: dict):
    """LR-7: a result is either validated legal, or a named rejection. Never a third thing."""
    result = L.adapt(entry["segments"], entry["source_word"])
    if result.ok:
        assert validate(result.form).ok
    else:
        assert result.code in (V.UNMAPPED, V.UNKNOWN, V.RESIDUE)
        assert result.offending
