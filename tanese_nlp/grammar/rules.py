"""Load the grammar rule tree in spec/grammar_rules/ and index what it declares.

This module only reads spec/; it never touches data/evaluation/ (no answer-key leakage).
It owns one piece of real logic, `tokenize()`, which is the single implementation of the
word boundary declared by GR-ORD-001. Everything that needs to know where one word ends --
the phonotactic checks, the script conversion, the contradiction checker -- goes through it,
so the three can never disagree about what a word is.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RULES_DIR = REPO_ROOT / "spec" / "grammar_rules"

# Rule files carry a numeric prefix; the two support files start with an underscore. The
# same split is encoded in tanese_nlp.speccheck.SCHEMA_MAP, which validates them against
# different schemas.
RULE_GLOB = "[0-9]*.yaml"
LEXICON_FILE = "_example_lexicon.yaml"
ORIGINALITY_FILE = "_originality.yaml"

# The rule that defines what a word is. Named here because tokenize() needs it before any
# rule has been interpreted, and a hard-coded " " is exactly what this module exists to
# avoid.
WORD_BOUNDARY_RULE = "GR-ORD-001"

# Categories whose rules must declare `morphemes`. Enforced by the JSON Schema; repeated
# here so the checker can report a missing declaration in its own terms.
MORPHEME_CATEGORIES = frozenset({"morphology", "particle", "pronoun", "politeness"})


@dataclass(frozen=True)
class Morpheme:
    """One form a rule declares, with the rule it came from."""

    form: str
    slot: str
    function: str
    kind: str
    word_class: str | None
    tense: str | None
    rule_id: str

    @property
    def is_mood(self) -> bool:
        return self.slot == "mood"


@dataclass(frozen=True)
class Example:
    """One valid or invalid example, with where it came from."""

    roman: str
    tanese: str
    note: str
    polarity: str  # "valid" | "invalid"
    rule_id: str
    index: int

    @property
    def label(self) -> str:
        return f"{self.rule_id} {self.polarity}[{self.index}]"


@dataclass(frozen=True)
class Rule:
    """One grammar rule, as read from YAML."""

    id: str
    category: str
    name: str
    source_file: str
    raw: dict[str, Any]

    @property
    def morphemes(self) -> list[Morpheme]:
        return [
            Morpheme(
                form=entry["form"],
                slot=entry["slot"],
                function=entry["function"],
                kind=entry["kind"],
                word_class=entry.get("word_class"),
                tense=entry.get("tense"),
                rule_id=self.id,
            )
            for entry in self.raw.get("morphemes", [])
        ]

    @property
    def examples(self) -> list[Example]:
        found: list[Example] = []
        for polarity, note_key in (("valid", "english"), ("invalid", "why")):
            for index, entry in enumerate(self.raw.get(polarity, [])):
                found.append(
                    Example(
                        roman=entry["roman"],
                        tanese=entry["tanese"],
                        note=entry[note_key],
                        polarity=polarity,
                        rule_id=self.id,
                        index=index,
                    )
                )
        return found

    @property
    def slot_order(self) -> list[str] | None:
        return self.raw.get("slot_order")

    @property
    def requires(self) -> list[str]:
        return list(self.raw.get("asserts", {}).get("requires", []))

    @property
    def forbids(self) -> list[str]:
        return list(self.raw.get("asserts", {}).get("forbids", []))


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@cache
def load_rules(rules_dir: Path = RULES_DIR) -> tuple[Rule, ...]:
    """Every rule in spec/grammar_rules/, in file then document order."""
    rules: list[Rule] = []
    for path in sorted(rules_dir.glob(RULE_GLOB)):
        document = _load_yaml(path)
        if not isinstance(document, list):
            continue  # a schema error, already reported by tanese_nlp.speccheck
        for entry in document:
            rules.append(
                Rule(
                    id=entry["id"],
                    category=entry["category"],
                    name=entry["name"],
                    source_file=path.name,
                    raw=entry,
                )
            )
    return tuple(rules)


@cache
def load_example_lexicon(rules_dir: Path = RULES_DIR) -> tuple[dict[str, Any], ...]:
    """The demo wordlist. Not vocabulary -- see the file's own header."""
    document = _load_yaml(rules_dir / LEXICON_FILE)
    return tuple(document["words"])


@cache
def load_originality(rules_dir: Path = RULES_DIR) -> tuple[dict[str, Any], ...]:
    """The banned Japanese and Tamil forms."""
    document = _load_yaml(rules_dir / ORIGINALITY_FILE)
    return tuple(document["banned"])


@cache
def roots(rules_dir: Path = RULES_DIR) -> frozenset[str]:
    """Every citation form the demo wordlist offers."""
    return frozenset(word["form"] for word in load_example_lexicon(rules_dir))


def morphemes(rules_dir: Path = RULES_DIR) -> Iterator[Morpheme]:
    """Every morpheme declared anywhere in the rule tree."""
    for rule in load_rules(rules_dir):
        yield from rule.morphemes


@cache
def suffix_forms(rules_dir: Path = RULES_DIR) -> frozenset[str]:
    return frozenset(m.form for m in morphemes(rules_dir) if m.kind == "suffix")


@cache
def particle_forms(rules_dir: Path = RULES_DIR) -> frozenset[str]:
    return frozenset(m.form for m in morphemes(rules_dir) if m.kind == "particle")


@cache
def word_forms(rules_dir: Path = RULES_DIR) -> frozenset[str]:
    """Forms declared as whole words (the pronouns), which are tokens in their own right."""
    return frozenset(m.form for m in morphemes(rules_dir) if m.kind == "word")


@cache
def word_boundary(rules_dir: Path = RULES_DIR) -> dict[str, Any]:
    """The `word_boundary` block of GR-ORD-001.

    Raises if no rule declares one: a tokenizer with a default separator would be a second,
    silent definition of `word`, which is the thing GR-ORD-001 exists to prevent.
    """
    declared = [
        (rule.id, rule.raw["word_boundary"])
        for rule in load_rules(rules_dir)
        if "word_boundary" in rule.raw
    ]
    if not declared:
        raise ValueError(
            f"no rule declares a word_boundary block; {WORD_BOUNDARY_RULE} must provide one"
        )
    if len(declared) > 1:
        ids = ", ".join(rule_id for rule_id, _ in declared)
        raise ValueError(f"word_boundary is declared more than once ({ids})")
    return declared[0][1]


def separator(rules_dir: Path = RULES_DIR) -> str:
    """The word separator, read from GR-ORD-001 rather than hard-coded."""
    return word_boundary(rules_dir)["separator"]


def tokenize(sentence: str, rules_dir: Path = RULES_DIR) -> list[str]:
    """Split a romanized sentence into words, as GR-ORD-001 defines them.

    Deliberately strict: it splits on the declared separator and nothing else, so a double
    space or a tab produces an empty token and is reported by the caller instead of being
    tidied away. Normalising here would hide exactly the spacing errors the invalid examples
    are testing for.
    """
    return sentence.split(separator(rules_dir)) if sentence else []
