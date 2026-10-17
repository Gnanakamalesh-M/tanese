"""Does each check actually fire?

A checker that returns no errors proves nothing until it has been shown to catch the thing
it claims to catch. Each test here builds a deliberately broken rule set, or a fake
data/vocabulary/ file, and asserts the relevant check reports it.

The rule loaders are cached module-level functions, so each test replaces them through
monkeypatch rather than writing files into spec/.
"""

from __future__ import annotations

import pytest
import yaml

from tanese_nlp import speccheck
from tanese_nlp.grammar import contradictions as C
from tanese_nlp.grammar import rules as R
from tanese_nlp.script.convert import roman_to_script

# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------


def _script(sentence: str) -> str:
    return " ".join(roman_to_script(token) for token in sentence.split(" "))


def _rule(rule_id: str, category: str = "syntax", **extra) -> R.Rule:
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
    return R.Rule(
        id=rule_id, category=category, name=raw["name"], source_file="test.yaml", raw=raw
    )


def _example(roman: str, polarity: str = "valid") -> dict:
    entry = {"tanese": _script(roman), "roman": roman}
    entry["english" if polarity == "valid" else "why"] = "note"
    return entry


def _morpheme(form: str, slot: str, function: str, kind: str = "suffix", **extra) -> dict:
    return {"form": form, "slot": slot, "function": function, "kind": kind, **extra}


@pytest.fixture
def fake_rules(monkeypatch):
    """Replace the rule tree with a hand-built one, keeping the real support files."""

    real_separator = R.separator()

    def install(*rules: R.Rule):
        monkeypatch.setattr(R, "load_rules", lambda *a, **k: tuple(rules))
        # The fake tree declares no GR-ORD-001, so keep the real word boundary: these tests
        # are about the rules, not about redefining what a word is.
        monkeypatch.setattr(R, "separator", lambda *a, **k: real_separator)
        morphemes = [m for rule in rules for m in rule.morphemes]
        monkeypatch.setattr(R, "morphemes", lambda *a, **k: iter(morphemes))
        monkeypatch.setattr(
            R, "particle_forms", lambda *a, **k: frozenset(
                m.form for m in morphemes if m.kind == "particle"
            )
        )
        monkeypatch.setattr(
            R, "word_forms", lambda *a, **k: frozenset(
                m.form for m in morphemes if m.kind == "word"
            )
        )
        monkeypatch.setattr(
            R, "suffix_forms", lambda *a, **k: frozenset(
                m.form for m in morphemes if m.kind == "suffix"
            )
        )

    return install


# --------------------------------------------------------------------------------------
# checks 1-4
# --------------------------------------------------------------------------------------


def test_check_1_catches_one_form_with_two_functions(fake_rules):
    fake_rules(
        _rule("GR-A-001", "particle", morphemes=[_morpheme("do", "case", "object", "particle")]),
        _rule("GR-A-002", "particle", morphemes=[_morpheme("do", "case", "dative", "particle")]),
    )
    errors = C.check_form_uniqueness()
    assert len(errors) == 1
    assert "'do'" in errors[0] and "GR-A-001" in errors[0] and "GR-A-002" in errors[0]


def test_check_1_allows_the_same_form_restated_with_the_same_function(fake_rules):
    fake_rules(
        _rule("GR-A-001", "particle", morphemes=[_morpheme("do", "case", "object", "particle")]),
        _rule("GR-A-002", "particle", morphemes=[_morpheme("do", "case", "object", "particle")]),
    )
    assert C.check_form_uniqueness() == []


def test_check_2_catches_two_forms_for_one_function(fake_rules):
    fake_rules(
        _rule("GR-A-001", "particle", morphemes=[_morpheme("do", "case", "object", "particle")]),
        _rule("GR-A-002", "particle", morphemes=[_morpheme("ba", "case", "object", "particle")]),
    )
    errors = C.check_function_uniqueness()
    assert len(errors) == 1
    assert "(case, object)" in errors[0]


def test_check_3_catches_a_slot_order_that_contradicts_the_locked_decision(fake_rules):
    fake_rules(_rule("GR-A-001", "morphology", slot_order=["root", "tense", "aspect"]))
    errors = C.check_slot_order()
    assert errors and "LOCKED decision 6" in errors[0]


def test_check_3_catches_two_rules_ordering_the_slots_differently(fake_rules):
    fake_rules(
        _rule("GR-A-001", "morphology", slot_order=C.LOCKED_SLOT_ORDER),
        _rule("GR-A-002", "morphology", slot_order=["root", "mood", "tense"]),
    )
    assert any("different slot orders" in e for e in C.check_slot_order())


def test_check_3_catches_a_suffix_in_a_slot_the_order_does_not_have(fake_rules):
    fake_rules(
        _rule(
            "GR-A-001",
            "morphology",
            morphemes=[_morpheme("ke", "evidential", "hearsay", word_class="verb")],
        )
    )
    assert any("not a verb slot" in e for e in C.check_slot_order())


def test_check_3_catches_a_tense_field_on_a_non_mood_suffix(fake_rules):
    fake_rules(
        _rule(
            "GR-A-001",
            "morphology",
            morphemes=[
                _morpheme("ke", "tense", "non_past", word_class="verb", tense="forbidden")
            ],
        )
    )
    assert any("only mood suffixes" in e for e in C.check_slot_order())


def test_check_4_catches_a_feature_required_and_forbidden(fake_rules):
    fake_rules(
        _rule("GR-A-001", asserts={"requires": ["clause.verb_final"]}),
        _rule("GR-A-002", asserts={"forbids": ["clause.verb_final"]}),
    )
    errors = C.check_assertions()
    assert len(errors) == 1
    assert "clause.verb_final" in errors[0]


# --------------------------------------------------------------------------------------
# checks 5-9
# --------------------------------------------------------------------------------------


def test_check_5_catches_a_sentence_valid_in_one_rule_and_invalid_in_another(fake_rules):
    fake_rules(
        _rule("GR-A-001", valid=[_example("ano dhen ikkeke")]),
        _rule("GR-A-002", invalid=[_example("ano dhen ikkeke", "invalid")]),
    )
    errors = C.check_example_cross_consistency()
    assert len(errors) == 1
    assert "GR-A-001" in errors[0] and "GR-A-002" in errors[0]


def test_check_5_ignores_case_and_spacing_differences(fake_rules):
    fake_rules(
        _rule("GR-A-001", valid=[_example("ano dhen ikkeke")]),
        _rule("GR-A-002", invalid=[{"tanese": "x", "roman": "ANO  dhen ikkeke", "why": "w"}]),
    )
    assert C.check_example_cross_consistency() != []


def test_check_6_catches_a_rule_contradicting_itself(fake_rules):
    fake_rules(
        _rule(
            "GR-A-001",
            valid=[_example("ano dhen ikkeke")],
            invalid=[_example("ano dhen ikkeke", "invalid")],
        )
    )
    errors = C.check_example_self_consistency()
    assert any("both valid and invalid" in e for e in errors)


def test_check_6_catches_a_repeated_example(fake_rules):
    fake_rules(
        _rule("GR-A-001", valid=[_example("ano dhen ikkeke"), _example("ano dhen ikkeke")])
    )
    assert any("repeats a valid example" in e for e in C.check_example_self_consistency())


def test_check_7_catches_an_illegal_word_in_an_example(fake_rules):
    fake_rules(
        _rule("GR-A-001", invalid=[{"tanese": "x", "roman": "ano dhen kaia", "why": "w"}])
    )
    errors = C.check_phonotactics()
    assert len(errors) == 1
    assert "PT-008" in errors[0] and "'kaia'" in errors[0]


def test_check_7_catches_a_double_separator(fake_rules):
    fake_rules(_rule("GR-A-001", valid=[{"tanese": "x", "roman": "ano  dhen", "english": "e"}]))
    assert any("empty word" in e for e in C.check_phonotactics())


def test_check_8_catches_a_hand_typed_script_field(fake_rules):
    fake_rules(
        _rule(
            "GR-A-001",
            valid=[{"tanese": "TS-KA", "roman": "ano dhen ikkeke", "english": "e"}],
        )
    )
    errors = C.check_script_fidelity()
    assert len(errors) == 1
    assert "the converter gives" in errors[0]


def test_check_9_catches_a_valid_example_using_an_undeclared_word(fake_rules):
    fake_rules(_rule("GR-A-001", valid=[_example("ano dhen bakuke")]))
    errors = C.check_lexicon_closure_and_originality()
    assert any("'bakuke'" in e and "demo root" in e for e in errors)


def test_check_9_does_not_apply_lexicon_closure_to_invalid_examples(fake_rules):
    """An invalid example is often invalid *because* a form is wrong."""
    fake_rules(_rule("GR-A-001", invalid=[_example("ano dhen bakuke", "invalid")]))
    assert not any("demo root" in e for e in C.check_lexicon_closure_and_originality())


def test_check_9_catches_a_borrowed_particle(fake_rules):
    fake_rules(
        _rule("GR-A-001", "particle", morphemes=[_morpheme("ga", "case", "subject", "particle")])
    )
    errors = C.check_lexicon_closure_and_originality()
    assert any("japanese" in e and "LOCKED decision 3" in e for e in errors)


def test_check_9_catches_a_wrong_unspellable_flag(monkeypatch):
    monkeypatch.setattr(
        R,
        "load_originality",
        lambda *a, **k: ({"form": "do", "source": "japanese", "gloss": "g", "unspellable": True},),
    )
    errors = C.check_lexicon_closure_and_originality()
    assert any("unspellable=True" in e for e in errors)


def test_a_particle_filed_under_syntax_is_reported(fake_rules):
    """The categorisation guard fires -- and the form is still checked anyway."""
    fake_rules(
        _rule("GR-A-001", "syntax", morphemes=[_morpheme("lun", "clause", "topic", "particle")]),
        _rule("GR-A-002", "syntax", morphemes=[_morpheme("lun", "clause", "focus", "particle")]),
    )
    misfiled = C.misfiled_morpheme_declarations()
    assert len(misfiled) == 2
    assert all("recategorise it" in error for error in misfiled)
    # the category does not exempt the forms from check 1
    assert C.check_form_uniqueness() != []


def test_a_one_letter_suffix_would_make_a_particle_decomposable(fake_rules):
    """Why `test_no_single_letter_morpheme_exists` matters: with an `n` suffix, `lun`
    becomes readable as a stem plus a suffix, and the stripper cannot tell which is meant."""
    fake_rules(
        _rule(
            "GR-A-001",
            "morphology",
            morphemes=[_morpheme("n", "number", "plural", word_class="noun")],
        )
    )
    monkey_roots = frozenset({"lu"})
    import pytest as _pytest  # local import keeps the fixture list above unchanged

    with _pytest.MonkeyPatch.context() as patch:
        patch.setattr(R, "roots", lambda *a, **k: monkey_roots)
        assert C._analyses("lun") != [], "a one-letter suffix makes `lun` decomposable"


# --------------------------------------------------------------------------------------
# checks 10-12: containment of the demo wordlist
# --------------------------------------------------------------------------------------


def test_check_10_catches_an_illegal_demo_word(monkeypatch):
    monkeypatch.setattr(
        R,
        "load_example_lexicon",
        lambda *a, **k: (
            {"form": "kaia", "class": "noun", "gloss": "g", "status": "experimental"},
        ),
    )
    errors = C.check_demo_words_legal()
    assert len(errors) == 1 and "PT-008" in errors[0]


def test_check_10_catches_a_duplicated_demo_word(monkeypatch):
    word = {"form": "nami", "class": "noun", "gloss": "g", "status": "experimental"}
    monkeypatch.setattr(R, "load_example_lexicon", lambda *a, **k: (word, word))
    assert any("listed twice" in e for e in C.check_demo_words_legal())


def test_check_11_catches_a_demo_word_claiming_official_status(monkeypatch):
    monkeypatch.setattr(
        R,
        "load_example_lexicon",
        lambda *a, **k: ({"form": "nami", "class": "noun", "gloss": "g", "status": "official"},),
    )
    errors = C.check_demo_words_experimental()
    assert len(errors) == 1 and "LOCKED decisions 14-15" in errors[0]


def test_check_12_fires_when_a_demo_word_is_copied_into_the_lexicon(tmp_path):
    """The Phase 2 tripwire, demonstrated rather than merely asserted to exist."""
    leaked = sorted(R.roots())[0]
    vocabulary = tmp_path / "vocabulary"
    vocabulary.mkdir()
    (vocabulary / "official.yaml").write_text(
        yaml.safe_dump({"words": [{"form": leaked, "gloss": "copied"}]}), encoding="utf-8"
    )
    errors = C.check_demo_words_not_in_vocabulary(vocabulary)
    assert len(errors) == 1
    assert leaked in errors[0] and "must not be copied" in errors[0]


def test_check_12_passes_on_a_lexicon_with_its_own_words(tmp_path):
    vocabulary = tmp_path / "vocabulary"
    vocabulary.mkdir()
    (vocabulary / "official.yaml").write_text(
        yaml.safe_dump({"words": [{"form": "thokkan", "gloss": "its own word"}]}),
        encoding="utf-8",
    )
    assert C.check_demo_words_not_in_vocabulary(vocabulary) == []


def test_check_12_is_vacuously_true_today():
    """data/vocabulary/ is empty until Phase 2, and that must not be mistaken for a pass."""
    assert C.check_demo_words_not_in_vocabulary() == []
    assert not list(C.VOCABULARY_DIR.rglob("*.yaml"))


# --------------------------------------------------------------------------------------
# the schema glob
# --------------------------------------------------------------------------------------


def test_the_rule_schema_is_not_applied_to_the_support_files():
    """The underscore files have their own schemas, not the rule-list one."""
    assert speccheck.RULE_GLOB == "grammar_rules/[0-9]*.yaml"
    claimed = {
        pattern: stem
        for pattern, stem in speccheck.SCHEMA_MAP.items()
        if "grammar_rules" in pattern
    }
    assert claimed["grammar_rules/_example_lexicon.yaml"] == "example_lexicon"
    assert claimed["grammar_rules/_originality.yaml"] == "originality"
    for path in (R.RULES_DIR).glob("[0-9]*.yaml"):
        assert not path.name.startswith("_")


def test_a_rule_file_without_a_numeric_prefix_is_reported_not_skipped(tmp_path):
    """The narrowed glob must not become a way to smuggle an unvalidated file into spec/."""
    spec_dir = tmp_path / "spec"
    (spec_dir / "grammar_rules").mkdir(parents=True)
    (spec_dir / "grammar_rules" / "extra_rules.yaml").write_text("- id: GR-X-001\n", "utf-8")
    errors = speccheck.check_spec_tree(spec_dir=spec_dir, schema_dir=speccheck.SCHEMA_DIR)
    assert any("no schema claims this file" in error for error in errors)
