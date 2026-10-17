"""Load spec/vocabulary_rules.yaml and index what it declares.

Mirrors tanese_nlp.grammar.rules: frozen dataclasses, `@cache` on every loader, and no
language knowledge of its own. Every table in this module is read from the spec file, so
changing a substitution or a root shape is a one-line edit to YAML and never a code change.

This module reads spec/ only. It never touches data/evaluation/ -- no answer-key leakage.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SPEC_FILE = REPO_ROOT / "spec" / "vocabulary_rules.yaml"

# Rejection codes. Declared here because the adapter raises them and the spec file names
# them in `unmapped` and `adaptation_rejections`; check 6 asserts the two agree.
UNMAPPED = "VL-UNMAPPED"
UNKNOWN = "VL-UNKNOWN"
RESIDUE = "VL-RESIDUE"


@dataclass(frozen=True)
class Example:
    """One valid or invalid example from a VR-* rule."""

    roman: str
    tanese: str | None
    note: str
    polarity: str  # "valid" | "invalid"
    legality: str  # "legal" | "illegal", as the example declares itself
    rule_id: str
    index: int

    @property
    def label(self) -> str:
        return f"{self.rule_id} {self.polarity}[{self.index}]"

    @property
    def words(self) -> list[str]:
        """The example split into words. Compounds are multi-word (VR-COMP-001)."""
        return self.roman.split(" ")


@dataclass(frozen=True)
class Rule:
    """One vocabulary rule, as read from YAML."""

    id: str
    category: str
    name: str
    raw: dict[str, Any]

    @property
    def examples(self) -> list[Example]:
        found: list[Example] = []
        for polarity, note_key in (("valid", "english"), ("invalid", "why")):
            for index, entry in enumerate(self.raw.get(polarity, [])):
                found.append(
                    Example(
                        roman=entry["roman"],
                        tanese=entry.get("tanese"),
                        note=entry[note_key],
                        polarity=polarity,
                        legality=entry.get("phonotactics", "legal"),
                        rule_id=self.id,
                        index=index,
                    )
                )
        return found


@cache
def document(path: Path = SPEC_FILE) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"{path.name}: expected a mapping at the top level")
    return loaded


@cache
def load_rules(path: Path = SPEC_FILE) -> tuple[Rule, ...]:
    """Every VR-* rule, in document order."""
    return tuple(
        Rule(id=entry["id"], category=entry["category"], name=entry["name"], raw=entry)
        for entry in document(path)["rules"]
    )


def examples(path: Path = SPEC_FILE) -> list[Example]:
    return [example for rule in load_rules(path) for example in rule.examples]


@cache
def strata(path: Path = SPEC_FILE) -> tuple[dict[str, Any], ...]:
    return tuple(document(path)["strata"])


@cache
def root_shapes(path: Path = SPEC_FILE) -> tuple[dict[str, Any], ...]:
    return tuple(document(path)["root_shapes"])


@cache
def mora_counts(path: Path = SPEC_FILE) -> dict[str, Any]:
    return document(path)["mora_counts"]


@cache
def permitted_finals(path: Path = SPEC_FILE) -> tuple[str, ...]:
    """Every grapheme a root may end in, flattened across the declared kinds."""
    return tuple(
        grapheme
        for entry in document(path)["permitted_finals"]
        for grapheme in entry["graphemes"]
    )


@cache
def originality(path: Path = SPEC_FILE) -> dict[str, Any]:
    return document(path)["originality"]


@cache
def semantic_fields(path: Path = SPEC_FILE) -> tuple[dict[str, Any], ...]:
    return tuple(document(path)["semantic_fields"])


@cache
def compound_patterns(path: Path = SPEC_FILE) -> tuple[dict[str, Any], ...]:
    return tuple(document(path)["compound_patterns"])


@cache
def substitutions(path: Path = SPEC_FILE) -> dict[str, str]:
    """Source sound -> Tanese graphemes. An empty value means deletion (source /h/)."""
    return {entry["source"]: entry["tanese"] for entry in document(path)["loan_substitutions"]}


@cache
def unmapped(path: Path = SPEC_FILE) -> dict[str, str]:
    """Source sound -> its rejection code, for sounds deliberately left unmapped."""
    return {entry["source"]: entry["code"] for entry in document(path)["unmapped"]}


@cache
def repairs(path: Path = SPEC_FILE) -> tuple[dict[str, Any], ...]:
    """The repair steps, sorted by their declared step number rather than file order."""
    return tuple(sorted(document(path)["loan_repairs"], key=lambda entry: entry["step"]))


@cache
def repair_ids(path: Path = SPEC_FILE) -> frozenset[str]:
    return frozenset(entry["id"] for entry in repairs(path))


@cache
def adaptation_examples(path: Path = SPEC_FILE) -> tuple[dict[str, Any], ...]:
    return tuple(document(path)["adaptation_examples"])


@cache
def adaptation_rejections(path: Path = SPEC_FILE) -> tuple[dict[str, Any], ...]:
    return tuple(document(path)["adaptation_rejections"])


@cache
def pipeline(path: Path = SPEC_FILE) -> tuple[dict[str, Any], ...]:
    """The Phase 2 pipeline stages, in declared order."""
    return tuple(document(path)["pipeline"])


@cache
def illustrative_forms(path: Path = SPEC_FILE) -> tuple[dict[str, Any], ...]:
    return tuple(document(path)["illustrative_forms"])


@cache
def declared_forms(path: Path = SPEC_FILE) -> frozenset[str]:
    """Every form this file invents: the illustrative roots and the adapted loan outputs.

    These are what check 13 keeps out of data/vocabulary/. Forms borrowed from the demo
    wordlist are not included: the grammar's own check 12 already guards those.
    """
    return frozenset(
        [entry["form"] for entry in illustrative_forms(path)]
        + [entry["expect"] for entry in adaptation_examples(path)]
    )


def levenshtein(left: str, right: str) -> int:
    """Absolute edit distance, the metric the originality gate declares."""
    previous = list(range(len(right) + 1))
    for i, left_char in enumerate(left, start=1):
        current = [i]
        for j, right_char in enumerate(right, start=1):
            current.append(
                min(
                    previous[j] + 1,
                    current[j - 1] + 1,
                    previous[j - 1] + (left_char != right_char),
                )
            )
        previous = current
    return previous[-1]
