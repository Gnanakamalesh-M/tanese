"""Does each vocabulary check actually fire?

A checker that returns no errors proves nothing until it has been shown to catch the thing
it claims to catch. Each test here breaks one declared table or one rule and asserts the
relevant check reports it. Same approach as tests/unit/test_contradictions.py for Phase 1B.

The loaders are cached module-level functions, so each test replaces them through
monkeypatch rather than writing files into spec/.
"""

from __future__ import annotations

import copy

import pytest

from tanese_nlp.grammar import rules as G
from tanese_nlp.vocabulary import consistency as C
from tanese_nlp.vocabulary import rules as V

# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------


def _rule(rule_id: str, category: str = "root_shape", **extra) -> V.Rule:
    raw = {
        "id": rule_id,
        "category": category,
        "name": "test rule",
        "description": "d",
        "reason": "r",
        "inspiration": {"source": "none", "original_feature": "x", "how_modified": "y"},
        "pattern": "p",
        "valid": [],
        "invalid": [],
        "status": "experimental",
        "since": "v0.1",
        **extra,
    }
    return V.Rule(id=rule_id, category=category, name=raw["name"], raw=raw)


def _example(roman: str, polarity: str = "valid", **extra) -> dict:
    from tanese_nlp.script.convert import roman_to_script

    entry: dict = {"roman": roman, **extra}
    if extra.get("phonotactics") != "illegal":
        entry["tanese"] = " ".join(roman_to_script(word) for word in roman.split(" "))
    entry["english" if polarity == "valid" else "why"] = "note"
    return entry


@pytest.fixture
def fake_rules(monkeypatch):
    """Replace the VR-* rule list with a hand-built one."""

    def install(*rules: V.Rule):
        monkeypatch.setattr(V, "load_rules", lambda *a, **k: tuple(rules))
        monkeypatch.setattr(
            V, "examples", lambda *a, **k: [e for rule in rules for e in rule.examples]
        )

    return install


@pytest.fixture
def fake_document(monkeypatch):
    """Replace the whole spec document with a mutated deep copy of the real one."""

    def install(mutate):
        document = copy.deepcopy(V.document())
        mutate(document)
        monkeypatch.setattr(V, "document", lambda *a, **k: document)
        for name, key in (
            ("strata", "strata"),
            ("root_shapes", "root_shapes"),
            ("semantic_fields", "semantic_fields"),
            ("compound_patterns", "compound_patterns"),
            ("pipeline", "pipeline"),
            ("illustrative_forms", "illustrative_forms"),
            ("adaptation_examples", "adaptation_examples"),
            ("adaptation_rejections", "adaptation_rejections"),
        ):
            monkeypatch.setattr(V, name, lambda *a, _k=key, **kw: tuple(document[_k]))
        monkeypatch.setattr(V, "mora_counts", lambda *a, **k: document["mora_counts"])
        monkeypatch.setattr(V, "originality", lambda *a, **k: document["originality"])
        monkeypatch.setattr(
            V,
            "permitted_finals",
            lambda *a, **k: tuple(
                g for entry in document["permitted_finals"] for g in entry["graphemes"]
            ),
        )
        monkeypatch.setattr(
            V,
            "substitutions",
            lambda *a, **k: {e["source"]: e["tanese"] for e in document["loan_substitutions"]},
        )
        monkeypatch.setattr(
            V, "unmapped", lambda *a, **k: {e["source"]: e["code"] for e in document["unmapped"]}
        )
        monkeypatch.setattr(
            V,
            "repairs",
            lambda *a, **k: tuple(sorted(document["loan_repairs"], key=lambda e: e["step"])),
        )
        monkeypatch.setattr(
            V, "repair_ids", lambda *a, **k: frozenset(e["id"] for e in document["loan_repairs"])
        )
        monkeypatch.setattr(
            V,
            "declared_forms",
            lambda *a, **k: frozenset(
                [e["form"] for e in document["illustrative_forms"]]
                + [e["expect"] for e in document["adaptation_examples"]]
            ),
        )
        return document

    return install


# --------------------------------------------------------------------------------------
# check 1  root shapes
# --------------------------------------------------------------------------------------


def test_check_1_catches_an_unsatisfiable_mora_range(fake_document):
    fake_document(lambda d: d["mora_counts"].update({"min": 5, "max": 2}))
    assert any("no root shape is satisfiable" in e for e in C.check_root_shapes())


def test_check_1_catches_a_missing_root_shape(fake_document):
    fake_document(lambda d: d["root_shapes"].pop(0))
    assert any("RS-MIN" in e for e in C.check_root_shapes())


def test_check_1_catches_an_illustrative_form_over_the_mora_cap(fake_document):
    fake_document(lambda d: d["illustrative_forms"].append(
        {
            "form": "welugaanen",
            "shape": "six moras",
            "status": "experimental",
            "why_needed": "test",
        }
    ))
    assert any("outside the declared range" in e for e in C.check_root_shapes())


def test_check_1_catches_an_illustrative_form_with_an_illegal_final(fake_document):
    fake_document(lambda d: d["permitted_finals"].clear() or d["permitted_finals"].append(
        {"kind": "moraic_nasal", "graphemes": ["n"]}
    ))
    assert any("not a permitted final" in e for e in C.check_root_shapes())


# --------------------------------------------------------------------------------------
# check 2  the cross-phase suffix check
# --------------------------------------------------------------------------------------


def test_check_2_catches_a_final_that_cannot_take_a_suffix(fake_document, monkeypatch):
    """A vowel-initial suffix is exactly what RS-FINAL assumes cannot exist."""
    monkeypatch.setattr(G, "suffix_forms", lambda *a, **k: frozenset({"ke", "ate"}))
    fake_document(lambda d: None)
    errors = C.check_suffix_concatenation()
    assert any("-ate" in e for e in errors), errors


def test_check_2_reports_when_no_suffix_is_declared(monkeypatch):
    monkeypatch.setattr(G, "suffix_forms", lambda *a, **k: frozenset())
    assert any("declares no suffixes" in e for e in C.check_suffix_concatenation())


# --------------------------------------------------------------------------------------
# check 3  compounds
# --------------------------------------------------------------------------------------


def test_check_3_catches_a_fusing_compound_pattern(fake_document):
    fake_document(lambda d: d["compound_patterns"][0].update({"written": "one_word"}))
    assert any("GR-NOUN-004" in e for e in C.check_compounds())


def test_check_3_catches_a_head_initial_compound_pattern(fake_document):
    fake_document(lambda d: d["compound_patterns"][0].update({"head": "initial"}))
    assert any("head-final" in e for e in C.check_compounds())


def test_check_3_catches_a_one_word_compound_example(fake_rules):
    fake_rules(
        _rule("VR-X-001", "compound", valid=[_example("sedhanami"), _example("kalu nami")])
    )
    assert any("is one word" in e for e in C.check_compounds())


# --------------------------------------------------------------------------------------
# check 4-5  collisions and originality
# --------------------------------------------------------------------------------------


def test_check_4_catches_a_form_that_equals_a_declared_particle(fake_document):
    fake_document(lambda d: d["illustrative_forms"].append(
        {"form": "thon", "shape": "x", "status": "experimental", "why_needed": "test"}
    ))
    assert any("RS-RESERVED" in e for e in C.check_reserved_collisions())


def test_check_4_catches_a_form_that_equals_a_demo_root(fake_document):
    fake_document(lambda d: d["illustrative_forms"].append(
        {"form": "nami", "shape": "x", "status": "experimental", "why_needed": "test"}
    ))
    assert any("demo root" in e for e in C.check_reserved_collisions())


def test_check_5_catches_a_form_equal_to_a_banned_source_form(fake_document):
    fake_document(lambda d: d["illustrative_forms"].append(
        {"form": "made", "shape": "x", "status": "experimental", "why_needed": "test"}
    ))
    assert any("hard gate" in e for e in C.check_originality())


def test_check_5_catches_a_form_one_edit_from_a_banned_source_form(fake_document):
    fake_document(lambda d: d["illustrative_forms"].append(
        {"form": "mado", "shape": "x", "status": "experimental", "why_needed": "test"}
    ))
    assert any("below the declared floor" in e for e in C.check_originality())


def test_check_5_passes_a_form_at_the_floor(fake_document):
    fake_document(lambda d: d["illustrative_forms"].append(
        {"form": "welugan", "shape": "x", "status": "experimental", "why_needed": "test"}
    ))
    assert C.check_originality() == []


# --------------------------------------------------------------------------------------
# check 6  the loan tables
# --------------------------------------------------------------------------------------


def test_check_6_catches_a_sound_both_mapped_and_unmapped(fake_document):
    fake_document(lambda d: d["unmapped"].append(
        {"source": "f", "code": "VL-UNMAPPED", "reason": "test"}
    ))
    assert any("both" in e for e in C.check_loan_tables())


def test_check_6_catches_a_substitution_to_a_non_grapheme(fake_document):
    fake_document(lambda d: d["loan_substitutions"].append(
        {"source": "test", "tanese": "q", "source_examples": ["x"], "reason": "test"}
    ))
    assert any("not a grapheme" in e or "not a Tanese grapheme" in e for e in C.check_loan_tables())


def test_check_6_catches_non_consecutive_repair_steps(fake_document):
    fake_document(lambda d: d["loan_repairs"][0].update({"step": 9}))
    assert any("consecutive" in e for e in C.check_loan_tables())


def test_check_6_catches_an_undeclared_step_in_an_example(fake_document):
    fake_document(lambda d: d["adaptation_examples"][0]["steps_fired"].append("LR-9-NONSENSE"))
    assert any("not a declared repair" in e for e in C.check_loan_tables())


def test_check_6_catches_the_llm_allowed_at_the_wrong_stage(fake_document):
    fake_document(lambda d: d["pipeline"][3].update({"llm_allowed": True}))
    assert any("LOCKED decision 14" in e for e in C.check_loan_tables())


# --------------------------------------------------------------------------------------
# check 7  the adapter against the spec
# --------------------------------------------------------------------------------------


def test_check_7_catches_a_wrong_expected_output(fake_document):
    fake_document(lambda d: d["adaptation_examples"][0].update({"expect": "nhodi"}))
    assert any("but the spec declares" in e for e in C.check_adapter_matches_spec())


def test_check_7_catches_a_wrong_declared_step_list(fake_document):
    fake_document(lambda d: d["adaptation_examples"][0].update(
        {"steps_fired": ["LR-1-SUBSTITUTE"]}
    ))
    assert any("fired" in e for e in C.check_adapter_matches_spec())


def test_check_7_catches_a_rejection_that_should_have_adapted(fake_document):
    fake_document(lambda d: d["adaptation_rejections"].append(
        {
            "source_word": "bank",
            "segments": ["b", "a", "n", "k"],
            "code": "VL-UNMAPPED",
            "offending": "b",
            "reason": "test",
        }
    ))
    assert any("should be rejected" in e for e in C.check_adapter_matches_spec())


def test_a_doubly_listed_sound_is_refused_rather_than_quietly_mapped(fake_document):
    """The adapter consults `unmapped` before `loan_substitutions`.

    So a sound listed in both tables is still refused, which is the property check 7's
    sweep over the unmapped list depends on. The double listing itself is check 6's job.
    """
    from tanese_nlp.vocabulary import loanwords as L

    fake_document(lambda d: d["loan_substitutions"].append(
        {"source": "sh", "tanese": "s", "source_examples": ["shop"], "reason": "test"}
    ))
    result = L.adapt(["sh", "o", "p"], "shop")
    assert not result.ok, "a sound declared unmapped must not be adapted"
    assert result.code == V.UNMAPPED
    assert C.check_adapter_matches_spec() == []
    assert any("both" in e for e in C.check_loan_tables()), "check 6 reports the double listing"


# --------------------------------------------------------------------------------------
# check 8-9  the examples
# --------------------------------------------------------------------------------------


def test_check_8_catches_a_valid_example_using_an_undeclared_word(fake_rules):
    fake_rules(_rule("VR-X-001", valid=[_example("thukini"), _example("nami")]))
    assert any("thukini" in e for e in C.check_example_closure())


def test_check_8_does_not_apply_closure_to_invalid_examples(fake_rules):
    fake_rules(_rule("VR-X-001", invalid=[_example("thukini", "invalid")]))
    assert C.check_example_closure() == []


def test_check_8_allows_a_declared_form_plus_a_suffix(fake_rules):
    fake_rules(_rule("VR-X-001", valid=[_example("welugannen")]))
    assert C.check_example_closure() == []


def test_check_9_catches_an_example_declared_legal_that_is_not(fake_rules):
    fake_rules(_rule("VR-X-001", valid=[{"roman": "kaia", "tanese": "x", "english": "n"}]))
    assert any("declared legal but is not" in e for e in C.check_example_legality())


def test_check_9_catches_an_example_declared_illegal_that_is_legal(fake_rules):
    fake_rules(
        _rule("VR-X-001", invalid=[_example("nami", "invalid", phonotactics="illegal")])
    )
    assert any("every word in it is legal" in e for e in C.check_example_legality())


def test_check_9_catches_a_hand_typed_script_field(fake_rules):
    fake_rules(
        _rule("VR-X-001", valid=[{"roman": "nami", "tanese": "TS-NA.TS-MO", "english": "n"}])
    )
    assert any("does not match its romanization" in e for e in C.check_example_legality())


def test_check_9_catches_a_missing_script_field(fake_rules):
    fake_rules(_rule("VR-X-001", valid=[{"roman": "nami", "english": "n"}]))
    assert any("has no script form" in e for e in C.check_example_legality())


def test_check_9_catches_a_script_form_on_an_illegal_example(fake_rules):
    fake_rules(
        _rule(
            "VR-X-001",
            invalid=[
                {
                    "roman": "kaia",
                    "tanese": "TS-KA.TS-A",
                    "why": "n",
                    "phonotactics": "illegal",
                }
            ],
        )
    )
    assert any("carries a script form" in e for e in C.check_example_legality())


# --------------------------------------------------------------------------------------
# check 10-12  the declared tables
# --------------------------------------------------------------------------------------


def test_check_10_catches_share_targets_over_one(fake_document):
    fake_document(lambda d: d["strata"][0].update({"share_target": 0.95}))
    assert any("more than the whole lexicon" in e for e in C.check_share_targets())


def test_check_11_catches_a_permitted_final_that_is_not_a_grapheme(fake_document):
    fake_document(lambda d: d["permitted_finals"][0]["graphemes"].append("q"))
    assert any("not a grapheme" in e for e in C.check_cross_spec_references())


def test_check_11_catches_a_semantic_field_naming_an_unknown_stratum(fake_document):
    fake_document(lambda d: d["semantic_fields"][0].update({"stratum": "klingon_inspired"}))
    assert any("not declared" in e for e in C.check_cross_spec_references())


def test_check_11_catches_a_non_loan_stratum_claiming_to_borrow_a_form(fake_document):
    fake_document(lambda d: d["strata"][0].update({"borrows_form": True}))
    assert any("VR-STR-002" in e for e in C.check_cross_spec_references())


def test_check_11_catches_the_loan_stratum_claiming_not_to_borrow_a_form(fake_document):
    fake_document(
        lambda d: next(e for e in d["strata"] if e["id"] == "loan").update(
            {"borrows_form": False}
        )
    )
    assert any("must declare borrows_form: true" in e for e in C.check_cross_spec_references())


def test_check_12_catches_a_duplicate_rule_id(fake_rules):
    fake_rules(_rule("VR-X-001"), _rule("VR-X-001"))
    assert any("duplicate rule id" in e for e in C.check_rule_shape())


def test_check_12_catches_too_few_examples(fake_rules):
    fake_rules(_rule("VR-X-001", valid=[_example("nami")]))
    assert any("valid example(s)" in e for e in C.check_rule_shape())


# --------------------------------------------------------------------------------------
# check 13  nothing invented here is vocabulary
# --------------------------------------------------------------------------------------


def test_check_13_catches_an_illustrative_form_in_the_lexicon(tmp_path):
    (tmp_path / "official.yaml").write_text(
        "version: v0.1\nwords:\n  - form: nhodi\n    gloss: smuggled in\n",
        encoding="utf-8",
    )
    errors = C.check_not_vocabulary(tmp_path)
    assert any("nhodi" in e for e in errors), errors


def test_check_13_catches_an_adapted_loan_in_the_lexicon(tmp_path):
    (tmp_path / "official.yaml").write_text(
        "version: v0.1\nwords:\n  - form: banku\n    gloss: bank\n", encoding="utf-8"
    )
    errors = C.check_not_vocabulary(tmp_path)
    assert any("banku" in e for e in errors), errors


def test_check_13_catches_a_non_experimental_illustrative_form(fake_document):
    fake_document(lambda d: d["illustrative_forms"][0].update({"status": "official"}))
    assert any("only `experimental` is permitted" in e for e in C.check_not_vocabulary())


def test_check_13_passes_on_an_empty_lexicon(tmp_path):
    assert C.check_not_vocabulary(tmp_path) == []


def test_check_13_passes_when_the_lexicon_does_not_exist_yet():
    assert C.check_not_vocabulary(V.REPO_ROOT / "data" / "vocabulary") == []
