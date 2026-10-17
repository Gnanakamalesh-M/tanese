"""The real vocabulary rules, checked rule by rule and example by example.

These assert the properties docs/SPEC.md's Phase 1C done-criteria name, over the actual
contents of spec/vocabulary_rules.yaml -- so they fail if a later phase edits the file into
an inconsistent state, not only when scripts/check_vocabulary.py is run by hand.
"""

from __future__ import annotations

import pytest

from tanese_nlp.grammar import rules as G
from tanese_nlp.phonology import spec_load as S
from tanese_nlp.phonology.phonotactics import validate
from tanese_nlp.script.convert import roman_to_script, script_to_roman
from tanese_nlp.vocabulary import consistency as C
from tanese_nlp.vocabulary import rules as V

RULES = V.load_rules()
EXAMPLES = V.examples()
REQUIRED_STRATA = {"native", "tamil_inspired", "japanese_inspired", "compound", "loan"}


def _ids(items):
    return [item.label if isinstance(item, V.Example) else item.id for item in items]


# --------------------------------------------------------------------------------------
# the file as a whole
# --------------------------------------------------------------------------------------


def test_the_rule_set_is_not_empty():
    assert RULES, "no rules loaded from spec/vocabulary_rules.yaml"


def test_rule_ids_are_unique():
    ids = [rule.id for rule in RULES]
    assert len(ids) == len(set(ids))


def test_every_consistency_check_passes():
    assert C.check_all() == []


def test_the_five_strata_required_by_phase_1c_are_declared():
    assert {entry["id"] for entry in V.strata()} == REQUIRED_STRATA


def test_only_the_loan_stratum_borrows_a_form():
    borrowers = {entry["id"] for entry in V.strata() if entry["borrows_form"]}
    assert borrowers == {"loan"}, (
        "VR-STR-002: inspiration is structural, so only `loan` may borrow a form"
    )


def test_share_targets_do_not_exceed_the_whole_lexicon():
    assert sum(entry["share_target"] for entry in V.strata()) <= 1.000001


def test_the_pipeline_covers_locked_decision_14():
    assert [entry["stage"] for entry in V.pipeline()] == [
        "candidate_generation",
        "phonotactic_check",
        "morphology_check",
        "collision_check",
        "rank",
        "human_approve",
    ]


def test_the_llm_may_act_at_one_stage_only():
    allowed = [entry["stage"] for entry in V.pipeline() if entry["llm_allowed"]]
    assert allowed == ["candidate_generation"], (
        "LOCKED decision 14: the LLM may only propose candidates"
    )


def test_the_last_pipeline_stage_is_not_automated():
    last = V.pipeline()[-1]
    assert last["stage"] == "human_approve"
    assert last["automated"] is False


# --------------------------------------------------------------------------------------
# done-criteria, per rule
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("rule", RULES, ids=_ids(RULES))
def test_done_criterion_two_examples_of_each_polarity(rule: V.Rule):
    assert len(rule.raw["valid"]) >= 2, f"{rule.id} has fewer than 2 valid examples"
    assert len(rule.raw["invalid"]) >= 2, f"{rule.id} has fewer than 2 invalid examples"


@pytest.mark.parametrize("rule", RULES, ids=_ids(RULES))
def test_every_rule_states_its_reasoning(rule: V.Rule):
    assert rule.raw["reason"].strip()
    assert rule.raw["inspiration"]["how_modified"].strip()


# --------------------------------------------------------------------------------------
# every example
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("example", EXAMPLES, ids=_ids(EXAMPLES))
def test_example_legality_is_as_declared(example: V.Example):
    results = [validate(word) for word in example.words if word]
    if example.legality == "illegal":
        assert any(not result.ok for result in results), (
            f"{example.label} is declared illegal but every word in it is legal"
        )
    else:
        for result in results:
            assert result.ok, f"{example.label}: {result}"


@pytest.mark.parametrize(
    "example",
    [e for e in EXAMPLES if e.legality == "legal"],
    ids=_ids([e for e in EXAMPLES if e.legality == "legal"]),
)
def test_legal_example_script_form_matches_its_romanization(example: V.Example):
    expected = " ".join(roman_to_script(word) for word in example.words)
    assert example.tanese == expected


@pytest.mark.parametrize(
    "example",
    [e for e in EXAMPLES if e.legality == "legal"],
    ids=_ids([e for e in EXAMPLES if e.legality == "legal"]),
)
def test_legal_example_round_trips_through_the_script(example: V.Example):
    back = " ".join(script_to_roman(part) for part in example.tanese.split(" "))
    assert back == example.roman


@pytest.mark.parametrize(
    "example",
    [e for e in EXAMPLES if e.legality == "illegal"],
    ids=_ids([e for e in EXAMPLES if e.legality == "illegal"]),
)
def test_illegal_example_has_no_script_form(example: V.Example):
    assert example.tanese is None, (
        "an illegal word has no script form; the converter refuses to produce one"
    )


# --------------------------------------------------------------------------------------
# forms this file introduces
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("form", sorted(V.declared_forms()))
def test_declared_form_is_a_legal_word(form: str):
    assert validate(form).ok


@pytest.mark.parametrize("form", sorted(V.declared_forms()))
def test_declared_form_clears_the_originality_gates(form: str):
    floor = V.originality()["new_root_gate"]["min_edit_distance"]
    banned = [e["form"] for e in G.load_originality() if not e.get("unspellable")]
    distance = min(V.levenshtein(form, other) for other in banned)
    assert distance >= floor, f"{form!r} is edit distance {distance} from a listed source form"


@pytest.mark.parametrize("form", sorted(V.declared_forms()))
def test_declared_form_does_not_collide_with_a_declared_morpheme(form: str):
    assert form not in {m.form for m in G.morphemes()}
    assert form not in G.roots()


@pytest.mark.parametrize("entry", V.illustrative_forms(), ids=lambda e: e["form"])
def test_illustrative_form_matches_the_declared_root_shape(entry: dict):
    counts = V.mora_counts()
    result = validate(entry["form"])
    assert counts["min"] <= result.mora_count <= counts["max"]
    assert entry["form"][-1] in V.permitted_finals()
    assert entry["status"] == "experimental"


# --------------------------------------------------------------------------------------
# cross-spec coupling
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("final", V.permitted_finals())
def test_every_permitted_final_takes_every_declared_suffix(final: str):
    """RS-FINAL's reason, as a test: this is why those finals and no others."""
    stem = "katan" if final == "n" else f"kat{final}"
    assert validate(stem).ok, f"test stem {stem!r} is not itself legal"
    for suffix in sorted(G.suffix_forms()):
        result = validate(stem + suffix)
        assert result.ok, f"{stem}+{suffix} is illegal: {result}"


def test_every_declared_suffix_is_consonant_initial():
    """The fact RS-FINAL rests on. If this fails, RS-FINAL has to be rewritten."""
    for suffix in sorted(G.suffix_forms()):
        assert suffix[0] not in S.vowels(), (
            f"suffix -{suffix} is vowel-initial, which RS-FINAL assumes cannot happen"
        )


@pytest.mark.parametrize("final", V.permitted_finals())
def test_permitted_finals_exist_in_the_phonology(final: str):
    assert final in set(S.vowels()) | set(S.consonants())


@pytest.mark.parametrize("field", V.semantic_fields(), ids=lambda f: f["id"])
def test_semantic_field_names_a_declared_stratum(field: dict):
    assert field["stratum"] in {entry["id"] for entry in V.strata()}


@pytest.mark.parametrize("pattern", V.compound_patterns(), ids=lambda p: p["id"])
def test_compounds_are_never_fused(pattern: dict):
    """GR-NOUN-004 is official and lists the fused spelling as invalid."""
    assert pattern["written"] == "separate_words"
    assert pattern["head"] in ("final", "none")
