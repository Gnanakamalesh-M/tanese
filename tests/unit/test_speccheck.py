"""Tests for the spec/ YAML schema check.

Fixtures are built in tmp_path rather than committed under spec/, so that test input
is never mistaken for real Tanese language content. The real grammar_rule schema is
used, so these tests also guard the schema itself.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest
import yaml

from tanese_nlp.speccheck import (
    SCHEMA_DIR,
    SCHEMA_MAP,
    check_spec_tree,
    load_schemas,
    validate_file,
)

MINIMAL_RULE: dict[str, Any] = {
    "id": "GR-TEST-001",
    # Phase 1B closed `category` to an enum, so the fixture has to name a real one. It is
    # still not part of the language: the ids and example strings are nonsense on purpose.
    "category": "syntax",
    "name": "test rule",
    "description": "A schema-exercising rule that is not part of the language.",
    "reason": "Exists only to verify the validator.",
    "inspiration": {
        "source": "none",
        "original_feature": "n/a",
        "how_modified": "n/a",
    },
    "pattern": "A + B",
    "valid": [
        {"tanese": "x1", "roman": "x1", "english": "first"},
        {"tanese": "x2", "roman": "x2", "english": "second"},
    ],
    "invalid": [
        {"tanese": "y1", "roman": "y1", "why": "first reason"},
        {"tanese": "y2", "roman": "y2", "why": "second reason"},
    ],
    "status": "official",
    "since": "v0.1",
}


@pytest.fixture
def grammar_rule_schema() -> dict[str, Any]:
    return load_schemas(SCHEMA_DIR)["grammar_rule"]


def write_rules(path: Path, rules: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(rules, sort_keys=False), encoding="utf-8")
    return path


def rule(**overrides: Any) -> dict[str, Any]:
    entry = copy.deepcopy(MINIMAL_RULE)
    entry.update(overrides)
    return entry


def test_schema_dir_contains_grammar_rule_schema() -> None:
    assert "grammar_rule" in load_schemas(SCHEMA_DIR)


def test_minimal_rule_validates_clean(tmp_path: Path, grammar_rule_schema: dict[str, Any]) -> None:
    path = write_rules(tmp_path / "ok.yaml", [rule()])
    assert validate_file(path, grammar_rule_schema) == []


def test_missing_required_key_is_reported(
    tmp_path: Path, grammar_rule_schema: dict[str, Any]
) -> None:
    entry = rule()
    del entry["reason"]
    path = write_rules(tmp_path / "bad.yaml", [entry])

    errors = validate_file(path, grammar_rule_schema)
    assert errors
    assert any("reason" in error for error in errors)


def test_single_valid_example_is_reported(
    tmp_path: Path, grammar_rule_schema: dict[str, Any]
) -> None:
    entry = rule(valid=[{"tanese": "x1", "roman": "x1", "english": "only one"}])
    path = write_rules(tmp_path / "bad.yaml", [entry])

    errors = validate_file(path, grammar_rule_schema)
    assert any("/0/valid" in error for error in errors)


def test_single_invalid_example_is_reported(
    tmp_path: Path, grammar_rule_schema: dict[str, Any]
) -> None:
    entry = rule(invalid=[{"tanese": "y1", "roman": "y1", "why": "only one"}])
    path = write_rules(tmp_path / "bad.yaml", [entry])

    errors = validate_file(path, grammar_rule_schema)
    assert any("/0/invalid" in error for error in errors)


@pytest.mark.parametrize("rule_id", ["PART-003", "GR-PART-3", "gr-part-003", "GR-PART-0003"])
def test_malformed_rule_id_is_reported(
    tmp_path: Path, grammar_rule_schema: dict[str, Any], rule_id: str
) -> None:
    path = write_rules(tmp_path / "bad.yaml", [rule(id=rule_id)])

    errors = validate_file(path, grammar_rule_schema)
    assert any("/0/id" in error for error in errors)


def test_unknown_inspiration_source_is_reported(
    tmp_path: Path, grammar_rule_schema: dict[str, Any]
) -> None:
    entry = rule(
        inspiration={"source": "korean", "original_feature": "a", "how_modified": "b"},
    )
    path = write_rules(tmp_path / "bad.yaml", [entry])

    errors = validate_file(path, grammar_rule_schema)
    assert any("/0/inspiration/source" in error for error in errors)


def test_unknown_category_is_reported(
    tmp_path: Path, grammar_rule_schema: dict[str, Any]
) -> None:
    """The category enum is what makes the conditional morpheme requirement well-defined:
    a typo'd category would otherwise skip the requirement silently."""
    path = write_rules(tmp_path / "bad.yaml", [rule(category="particles")])

    errors = validate_file(path, grammar_rule_schema)
    assert any("/0/category" in error for error in errors)


@pytest.mark.parametrize("category", ["particle", "pronoun", "politeness"])
def test_form_introducing_categories_must_declare_morphemes(
    tmp_path: Path, grammar_rule_schema: dict[str, Any], category: str
) -> None:
    path = write_rules(tmp_path / "bad.yaml", [rule(category=category)])

    errors = validate_file(path, grammar_rule_schema)
    assert any("morphemes" in error for error in errors)


def test_a_morphology_rule_may_declare_a_slot_order_instead_of_morphemes(
    tmp_path: Path, grammar_rule_schema: dict[str, Any]
) -> None:
    """GR-VERB-003 states the arrangement of forms declared by other rules."""
    order = ["root", "aspect", "tense", "mood", "politeness"]
    clean = write_rules(tmp_path / "ok.yaml", [rule(category="morphology", slot_order=order)])
    assert validate_file(clean, grammar_rule_schema) == []

    # A morphology rule with neither field is rejected. jsonschema reports an anyOf failure
    # without naming the missing key, so the readable message comes from
    # contradictions.missing_morpheme_declarations(); here we only assert the rejection.
    bare = write_rules(tmp_path / "bad.yaml", [rule(category="morphology")])
    errors = validate_file(bare, grammar_rule_schema)
    assert any("/0" in error for error in errors)


def test_unexpected_key_is_reported(tmp_path: Path, grammar_rule_schema: dict[str, Any]) -> None:
    path = write_rules(tmp_path / "bad.yaml", [rule(notes="typo'd field name")])

    errors = validate_file(path, grammar_rule_schema)
    assert any("notes" in error for error in errors)


def test_malformed_yaml_reports_an_error_instead_of_raising(
    tmp_path: Path, grammar_rule_schema: dict[str, Any]
) -> None:
    path = tmp_path / "broken.yaml"
    path.write_text("- id: GR-TEST-001\n  valid: [unclosed\n", encoding="utf-8")

    errors = validate_file(path, grammar_rule_schema)
    assert len(errors) == 1
    assert "not valid YAML" in errors[0]


def test_empty_file_is_reported(tmp_path: Path, grammar_rule_schema: dict[str, Any]) -> None:
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")

    assert validate_file(path, grammar_rule_schema, rel_to=tmp_path) == [
        "empty.yaml: file is empty"
    ]


def test_duplicate_rule_id_across_files_is_reported(tmp_path: Path) -> None:
    write_rules(tmp_path / "grammar_rules" / "00_a.yaml", [rule(id="GR-DUP-001")])
    write_rules(tmp_path / "grammar_rules" / "10_b.yaml", [rule(id="GR-DUP-001")])

    errors = check_spec_tree(tmp_path, SCHEMA_DIR)
    assert any("duplicate rule id 'GR-DUP-001'" in error for error in errors)


def test_distinct_rule_ids_across_files_are_accepted(tmp_path: Path) -> None:
    write_rules(tmp_path / "grammar_rules" / "00_a.yaml", [rule(id="GR-AAA-001")])
    write_rules(tmp_path / "grammar_rules" / "10_b.yaml", [rule(id="GR-BBB-001")])

    assert check_spec_tree(tmp_path, SCHEMA_DIR) == []


def test_empty_spec_tree_is_not_an_error(tmp_path: Path) -> None:
    assert check_spec_tree(tmp_path, SCHEMA_DIR) == []


def test_unclaimed_yaml_file_is_reported(tmp_path: Path) -> None:
    # Phase 1A claimed phonology.yaml, which this test used to use as its example. Assert the
    # stand-in really is unclaimed, so the test fails loudly rather than silently passing for
    # the wrong reason when a later phase claims this name too.
    unclaimed = "not_a_real_spec_file.yaml"
    assert unclaimed not in SCHEMA_MAP

    (tmp_path / unclaimed).write_text("vowels: [a]\n", encoding="utf-8")

    errors = check_spec_tree(tmp_path, SCHEMA_DIR)
    assert any("no schema claims this file" in error for error in errors)


def test_real_spec_tree_passes() -> None:
    """The committed spec/ must always be clean -- this is what CI enforces."""
    assert check_spec_tree() == []
