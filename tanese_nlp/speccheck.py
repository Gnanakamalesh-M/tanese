"""Validate the machine-readable language rules in spec/ against JSON Schema.

spec/*.yaml is the source of truth for Tanese. This module only reads spec/ and
spec/schemas/; it never touches data/evaluation/ (no answer-key leakage).

Errors are returned as strings rather than raised, so a caller can report every
problem in one pass instead of stopping at the first one.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = REPO_ROOT / "spec"
SCHEMA_DIR = SPEC_DIR / "schemas"

# Which schema governs which spec file. Keys are glob patterns relative to spec/;
# values are schema stems in spec/schemas/. Later phases extend this table as they
# add vocabulary_rules.yaml.
SCHEMA_MAP: dict[str, str] = {
    "phonology.yaml": "phonology",
    "romanization.yaml": "romanization",
    "script.yaml": "script",
    "grammar_rules/*.yaml": "grammar_rule",
}


def load_schemas(schema_dir: Path = SCHEMA_DIR) -> dict[str, dict[str, Any]]:
    """Load spec/schemas/<stem>.schema.json, keyed by <stem>."""
    schemas: dict[str, dict[str, Any]] = {}
    for path in sorted(schema_dir.glob("*.schema.json")):
        stem = path.name.removesuffix(".schema.json")
        schemas[stem] = json.loads(path.read_text(encoding="utf-8"))
    return schemas


def _pointer(parts: Any) -> str:
    return "/" + "/".join(str(p) for p in parts) if parts else "(root)"


def validate_file(path: Path, schema: dict[str, Any], *, rel_to: Path | None = None) -> list[str]:
    """Validate one YAML file against one schema. Returns error strings, empty if clean."""
    label = str(path.relative_to(rel_to)) if rel_to else str(path)
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"{label}: not valid YAML: {exc}"]

    if document is None:
        return [f"{label}: file is empty"]

    validator = Draft202012Validator(schema)
    return [
        f"{label}:{_pointer(error.absolute_path)}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path))
    ]


def _check_rule_ids_unique(spec_dir: Path) -> list[str]:
    """Rule ids must be unique and stable across every grammar-rule file."""
    seen: dict[str, str] = {}
    errors: list[str] = []
    for path in sorted(spec_dir.glob("grammar_rules/*.yaml")):
        label = str(path.relative_to(spec_dir))
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue  # already reported by validate_file
        if not isinstance(document, list):
            continue
        for entry in document:
            if not isinstance(entry, dict):
                continue
            rule_id = entry.get("id")
            if not isinstance(rule_id, str):
                continue
            if rule_id in seen:
                errors.append(f"{label}: duplicate rule id {rule_id!r} (also in {seen[rule_id]})")
            else:
                seen[rule_id] = label
    return errors


def check_spec_tree(spec_dir: Path = SPEC_DIR, schema_dir: Path = SCHEMA_DIR) -> list[str]:
    """Validate every spec file that a schema claims. Empty list means everything passed.

    An empty spec/ is not an error -- no language content exists until Phase 1A. A file
    that no schema claims, or that fails its schema, is.
    """
    errors: list[str] = []
    schemas = load_schemas(schema_dir)

    claimed: set[Path] = set()
    for pattern, schema_stem in SCHEMA_MAP.items():
        schema = schemas.get(schema_stem)
        for path in sorted(spec_dir.glob(pattern)):
            claimed.add(path)
            if schema is None:
                errors.append(
                    f"{path.relative_to(spec_dir)}: no schema {schema_stem!r} in {schema_dir.name}/"
                )
                continue
            errors.extend(validate_file(path, schema, rel_to=spec_dir))

    for path in sorted(spec_dir.rglob("*.yaml")):
        if path not in claimed:
            errors.append(
                f"{path.relative_to(spec_dir)}: no schema claims this file "
                f"(add a pattern to SCHEMA_MAP in tanese_nlp/speccheck.py)"
            )

    errors.extend(_check_rule_ids_unique(spec_dir))
    return errors
