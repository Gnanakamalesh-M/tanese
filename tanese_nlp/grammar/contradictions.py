"""Does the grammar contradict itself?

Twelve deterministic checks over spec/grammar_rules/. No LLM is involved and none could be:
a rule set either contradicts itself or it does not, and an answer that is sometimes wrong
would be worse than no answer. Checks 1-9 are about the rules, 10-12 keep the demo wordlist
out of the real lexicon.

Errors are returned as strings rather than raised, so one run reports every problem.

Two limitations, repeated in README "Not verified" because they bound what a green run
means:

  * Checks 5 and 6 compare normalised example strings. Two rules whose prose disagrees while
    their examples do not overlap will pass.
  * An `invalid` example is author-asserted. Nothing here proves it is ungrammatical -- the
    rule-based grammar checker that could is Phase 4. What is proved is that it is
    phonotactically legal, spelled consistently with the script, tokenizable, and not
    claimed valid by another rule.

This module reads spec/ and data/vocabulary/ only. It never reads data/evaluation/.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

from tanese_nlp.grammar import rules as R
from tanese_nlp.phonology.phonotactics import validate
from tanese_nlp.script.convert import roman_to_script

# LOCKED decision 6. The merged slot order must equal this exactly; a rule that disagrees is
# not a difference of opinion, it is a contradiction with docs/SPEC.md.
LOCKED_SLOT_ORDER = ["root", "aspect", "tense", "mood", "politeness"]
VERB_SUFFIX_SLOTS = [slot for slot in LOCKED_SLOT_ORDER if slot != "root"]
NOUN_SUFFIX_SLOTS = ["number"]

REPO_ROOT = R.REPO_ROOT
VOCABULARY_DIR = REPO_ROOT / "data" / "vocabulary"


# --------------------------------------------------------------------------------------
# a naive segmenter, used by checks 3 and 9
# --------------------------------------------------------------------------------------
# This is NOT the Phase 4 morphological analyzer. It strips declared suffixes from the end
# of a token and asks whether anything in the demo wordlist is left, with backtracking and
# no notion of productivity, semantics or ambiguity resolution. It is good enough to catch
# a typo or an undeclared form in an example, which is all it is used for.


def _analyses(token: str) -> list[list[R.Morpheme]]:
    """Every way `token` reads as a demo root plus declared suffixes, innermost first."""
    found: list[list[R.Morpheme]] = []
    if token in R.roots():
        found.append([])
    for morpheme in R.morphemes():
        if morpheme.kind != "suffix":
            continue
        if not token.endswith(morpheme.form) or len(token) <= len(morpheme.form):
            continue
        stem = token[: -len(morpheme.form)]
        found.extend(inner + [morpheme] for inner in _analyses(stem))
    return found


def _slot_sequence_ok(suffixes: Iterable[R.Morpheme]) -> bool:
    """Do these suffixes sit in distinct slots, in the locked order?

    A noun suffix may not mix with verb suffixes: the locked order describes the verb only,
    and GR-NOUN-001's `-nen` has nothing to do with it.
    """
    suffixes = list(suffixes)
    classes = {m.word_class for m in suffixes}
    if len(classes) > 1:
        return False
    slots = [m.slot for m in suffixes]
    if len(set(slots)) != len(slots):
        return False  # a slot used twice
    expected = NOUN_SUFFIX_SLOTS if classes == {"noun"} else VERB_SUFFIX_SLOTS
    if any(slot not in expected for slot in slots):
        return False
    positions = [expected.index(slot) for slot in slots]
    return positions == sorted(positions)


def _tense_rule_ok(suffixes: Iterable[R.Morpheme]) -> bool:
    """GR-VERB-006: tense is obligatory unless a tenseless mood says otherwise."""
    suffixes = list(suffixes)
    if not any(m.word_class == "verb" for m in suffixes):
        return True  # not a verb form; nothing to say
    has_tense = any(m.slot == "tense" for m in suffixes)
    moods = [m for m in suffixes if m.is_mood]
    if moods and moods[0].tense == "forbidden":
        return not has_tense
    return has_tense


def legal_readings(token: str) -> list[list[R.Morpheme]]:
    """The analyses of `token` that break neither the slot order nor the tense rule."""
    if token in R.particle_forms() or token in R.word_forms():
        return [[]]
    return [
        analysis
        for analysis in _analyses(token)
        if _slot_sequence_ok(analysis) and _tense_rule_ok(analysis)
    ]


# --------------------------------------------------------------------------------------
# checks 1-4: the declared system
# --------------------------------------------------------------------------------------


def check_form_uniqueness() -> list[str]:
    """1. No form may carry two different functions."""
    by_form: dict[str, list[R.Morpheme]] = {}
    for morpheme in R.morphemes():
        by_form.setdefault(morpheme.form, []).append(morpheme)
    errors: list[str] = []
    for form, entries in sorted(by_form.items()):
        functions = {entry.function for entry in entries}
        if len(functions) > 1:
            where = ", ".join(f"{e.rule_id}={e.function}" for e in entries)
            errors.append(f"check 1: form {form!r} is claimed for several functions ({where})")
    return errors


def check_function_uniqueness() -> list[str]:
    """2. No (slot, function) pair may be claimed by two different forms."""
    by_key: dict[tuple[str, str], list[R.Morpheme]] = {}
    for morpheme in R.morphemes():
        by_key.setdefault((morpheme.slot, morpheme.function), []).append(morpheme)
    errors: list[str] = []
    for (slot, function), entries in sorted(by_key.items()):
        forms = {entry.form for entry in entries}
        if len(forms) > 1:
            where = ", ".join(f"{e.rule_id}={e.form}" for e in entries)
            errors.append(
                f"check 2: ({slot}, {function}) is claimed by several forms ({where}); "
                f"declare one and give the other its own function"
            )
    return errors


def check_slot_order() -> list[str]:
    """3. Every slot_order claim agrees with LOCKED decision 6, and with the mood entries."""
    errors: list[str] = []

    for rule in R.load_rules():
        order = rule.slot_order
        if order is None:
            continue
        if order != LOCKED_SLOT_ORDER:
            errors.append(
                f"check 3: {rule.id} declares slot order {order}, which contradicts LOCKED "
                f"decision 6 ({LOCKED_SLOT_ORDER}); propose the change in docs/CHANGES.md "
                f"before asserting it here"
            )

    declared_orders = [rule.slot_order for rule in R.load_rules() if rule.slot_order]
    for first, second in zip(declared_orders, declared_orders[1:], strict=False):
        if first != second:
            errors.append(f"check 3: two rules declare different slot orders: {first} vs {second}")

    for morpheme in R.morphemes():
        if morpheme.kind != "suffix":
            continue
        expected = NOUN_SUFFIX_SLOTS if morpheme.word_class == "noun" else VERB_SUFFIX_SLOTS
        if morpheme.slot not in expected:
            errors.append(
                f"check 3: {morpheme.rule_id} puts suffix {morpheme.form!r} in slot "
                f"{morpheme.slot!r}, which is not a {morpheme.word_class} slot ({expected})"
            )
        if morpheme.tense is not None and not morpheme.is_mood:
            errors.append(
                f"check 3: {morpheme.rule_id} gives {morpheme.form!r} a `tense` field, but it "
                f"is in slot {morpheme.slot!r}; only mood suffixes license or forbid tense"
            )

    return errors


def check_assertions() -> list[str]:
    """4. No feature key is required by one rule and forbidden by another."""
    required: dict[str, list[str]] = {}
    forbidden: dict[str, list[str]] = {}
    for rule in R.load_rules():
        for key in rule.requires:
            required.setdefault(key, []).append(rule.id)
        for key in rule.forbids:
            forbidden.setdefault(key, []).append(rule.id)
    return [
        f"check 4: feature {key!r} is required by {', '.join(required[key])} and forbidden by "
        f"{', '.join(forbidden[key])}"
        for key in sorted(set(required) & set(forbidden))
    ]


# --------------------------------------------------------------------------------------
# checks 5-9: the examples
# --------------------------------------------------------------------------------------


def _normalise(sentence: str) -> str:
    return " ".join(sentence.split()).strip().lower()


def _all_examples() -> list[R.Example]:
    return [example for rule in R.load_rules() for example in rule.examples]


def check_example_cross_consistency() -> list[str]:
    """5. No sentence is valid in one rule and invalid in another."""
    valid: dict[str, list[str]] = {}
    invalid: dict[str, list[str]] = {}
    for example in _all_examples():
        bucket = valid if example.polarity == "valid" else invalid
        bucket.setdefault(_normalise(example.roman), []).append(example.rule_id)
    errors: list[str] = []
    for sentence in sorted(set(valid) & set(invalid)):
        if set(valid[sentence]) == set(invalid[sentence]):
            continue  # reported by check 6, which gives a better message
        errors.append(
            f"check 5: {sentence!r} is valid in {', '.join(sorted(set(valid[sentence])))} but "
            f"invalid in {', '.join(sorted(set(invalid[sentence])))}"
        )
    return errors


def check_example_self_consistency() -> list[str]:
    """6. No rule lists the same sentence as both valid and invalid."""
    errors: list[str] = []
    for rule in R.load_rules():
        valid = {_normalise(e.roman) for e in rule.examples if e.polarity == "valid"}
        invalid = {_normalise(e.roman) for e in rule.examples if e.polarity == "invalid"}
        for sentence in sorted(valid & invalid):
            errors.append(f"check 6: {rule.id} lists {sentence!r} as both valid and invalid")
        for polarity in ("valid", "invalid"):
            entries = [e for e in rule.examples if e.polarity == polarity]
            if len(entries) != len({_normalise(e.roman) for e in entries}):
                errors.append(f"check 6: {rule.id} repeats a {polarity} example")
    return errors


def check_phonotactics() -> list[str]:
    """7. Every word of every example is a legal Tanese word.

    Invalid examples included: their wrongness must be grammatical, not phonotactic. An
    example that is not even pronounceable tests nothing about the grammar, and it could not
    be converted to script for check 8 either.
    """
    errors: list[str] = []
    for example in _all_examples():
        tokens = R.tokenize(example.roman)
        if any(token == "" for token in tokens):
            errors.append(
                f"check 7: {example.label} {example.roman!r} has an empty word; words are "
                f"separated by exactly one {R.separator()!r} (GR-ORD-001)"
            )
            continue
        for token in tokens:
            result = validate(token)
            if not result.ok:
                codes = ", ".join(result.codes)
                errors.append(
                    f"check 7: {example.label} word {token!r} is not a legal Tanese word "
                    f"[{codes}]: {result.violations[0].message}"
                )
    return errors


def check_script_fidelity() -> list[str]:
    """8. The `tanese` field is the converter's output for the `roman` field, word by word."""
    errors: list[str] = []
    separator = R.separator()
    for example in _all_examples():
        tokens = R.tokenize(example.roman)
        try:
            expected = separator.join(roman_to_script(token) for token in tokens)
        except ValueError:
            continue  # the word itself is illegal; check 7 reports it
        if example.tanese != expected:
            errors.append(
                f"check 8: {example.label} tanese field is {example.tanese!r} but the "
                f"converter gives {expected!r}"
            )
    return errors


def check_lexicon_closure_and_originality() -> list[str]:
    """9. Valid examples use declared forms only, and no declared form is a banned one."""
    errors: list[str] = []

    for example in _all_examples():
        if example.polarity != "valid":
            # An invalid example is often invalid *because* a form is misused, so closure
            # cannot apply to it. It is still held to checks 7 and 8.
            continue
        for token in R.tokenize(example.roman):
            if not token:
                continue  # reported by check 7
            if not legal_readings(token):
                errors.append(
                    f"check 9: {example.label} word {token!r} does not read as a demo root "
                    f"plus declared suffixes (spec/grammar_rules/_example_lexicon.yaml)"
                )

    banned = {entry["form"]: entry for entry in R.load_originality()}
    for morpheme in R.morphemes():
        entry = banned.get(morpheme.form)
        if entry is not None:
            errors.append(
                f"check 9: {morpheme.rule_id} declares {morpheme.form!r}, which is "
                f"{entry['source']} {entry['gloss']} (LOCKED decision 3)"
            )

    # The `unspellable` flag is a claim about Tanese, so it is verified rather than trusted.
    for entry in R.load_originality():
        legal = validate(str(entry["form"])).ok
        claimed = bool(entry.get("unspellable", False))
        if legal == claimed:
            errors.append(
                f"check 9: _originality.yaml entry {entry['form']!r} is marked "
                f"unspellable={claimed}, but the phonotactic validator says "
                f"{'legal' if legal else 'illegal'}"
            )

    return errors


# --------------------------------------------------------------------------------------
# checks 10-12: containment of the demo wordlist
# --------------------------------------------------------------------------------------


def check_demo_words_legal() -> list[str]:
    """10. Every demo word is a legal Tanese word."""
    errors: list[str] = []
    for word in R.load_example_lexicon():
        result = validate(word["form"])
        if not result.ok:
            errors.append(
                f"check 10: demo word {word['form']!r} is illegal [{', '.join(result.codes)}]"
            )
    seen: set[str] = set()
    for word in R.load_example_lexicon():
        if word["form"] in seen:
            errors.append(f"check 10: demo word {word['form']!r} is listed twice")
        seen.add(word["form"])
    return errors


def check_demo_words_experimental() -> list[str]:
    """11. No demo word claims official status."""
    return [
        f"check 11: demo word {word['form']!r} has status {word['status']!r}; the demo "
        f"wordlist is experimental only (LOCKED decisions 14-15)"
        for word in R.load_example_lexicon()
        if word["status"] != "experimental"
    ]


def _strings_in(node: Any) -> Iterable[str]:
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _strings_in(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings_in(value)


def check_demo_words_not_in_vocabulary(
    vocabulary_dir: Path = VOCABULARY_DIR,
) -> list[str]:
    """12. No demo word has been copied into data/vocabulary/.

    data/vocabulary/ is empty until Phase 2, so this passes trivially today and becomes a
    tripwire the moment official.yaml exists: a word that wants to be official must be
    re-derived through the Phase 2 pipeline, which may reject it, not copied across from
    here.
    """
    if not vocabulary_dir.is_dir():
        return []
    errors: list[str] = []
    demo = R.roots()
    for path in sorted(vocabulary_dir.rglob("*.yaml")):
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"check 12: {path.name} is not valid YAML: {exc}")
            continue
        leaked = sorted(demo.intersection(_strings_in(document)))
        for form in leaked:
            errors.append(
                f"check 12: demo word {form!r} appears in data/vocabulary/{path.name}; demo "
                f"words are not vocabulary and must not be copied into the lexicon"
            )
    return errors


# --------------------------------------------------------------------------------------
# entry points
# --------------------------------------------------------------------------------------

CHECKS = (
    ("1 form uniqueness", check_form_uniqueness),
    ("2 function uniqueness", check_function_uniqueness),
    ("3 slot order", check_slot_order),
    ("4 assertion conflict", check_assertions),
    ("5 example cross-check", check_example_cross_consistency),
    ("6 example self-consistency", check_example_self_consistency),
    ("7 phonotactics", check_phonotactics),
    ("8 script fidelity", check_script_fidelity),
    ("9 lexicon closure + originality", check_lexicon_closure_and_originality),
    ("10 demo words legal", check_demo_words_legal),
    ("11 demo words experimental", check_demo_words_experimental),
    ("12 demo words not in vocabulary", check_demo_words_not_in_vocabulary),
)


def check_all() -> list[str]:
    """Run every check. Empty list means the grammar is internally consistent."""
    errors: list[str] = []
    for _, check in CHECKS:
        errors.extend(check())
    return errors


def missing_morpheme_declarations() -> list[str]:
    """Categories that must declare morphemes but did not.

    The JSON Schema enforces this too; it is repeated here so `check_grammar.py` reports it
    in the checker's own terms rather than as a schema error from another script.
    """
    missing: list[str] = []
    for rule in R.load_rules():
        if rule.category not in R.MORPHEME_CATEGORIES:
            continue
        if rule.morphemes:
            continue
        # A morphology rule may instead state the arrangement of forms declared elsewhere,
        # which is what GR-VERB-003 does with `slot_order`. Either way it is machine-readable.
        if rule.category == "morphology" and rule.slot_order:
            continue
        missing.append(
            f"{rule.id} is category {rule.category!r} but declares neither morphemes nor "
            f"a slot order"
        )
    return missing


def misfiled_morpheme_declarations() -> list[str]:
    """Rules that declare forms but are filed under a category that does not require it.

    Checks 1, 2, 3 and 9 iterate over every declared morpheme regardless of its rule's
    category, so a form filed under `syntax` is still fully checked -- the conditional
    requirement in the schema governs whether declaring is *mandatory*, not whether a
    declaration is honoured. This is the separate, weaker guarantee: a rule that introduces
    a form should be categorised as one that introduces a form, so that the schema's
    requirement is doing real work rather than being satisfied by accident of filing.
    """
    return [
        f"{rule.id} declares {len(rule.morphemes)} morpheme(s) but is category "
        f"{rule.category!r}; recategorise it as one of {sorted(R.MORPHEME_CATEGORIES)}"
        for rule in R.load_rules()
        if rule.morphemes and rule.category not in R.MORPHEME_CATEGORIES
    ]


def stats() -> dict[str, Any]:
    """The counts that go in the README. Printed, never hand-typed."""
    rule_list = R.load_rules()
    examples = _all_examples()
    by_category: dict[str, int] = {}
    for rule in rule_list:
        by_category[rule.category] = by_category.get(rule.category, 0) + 1
    by_file: dict[str, int] = {}
    for rule in rule_list:
        by_file[rule.source_file] = by_file.get(rule.source_file, 0) + 1
    return {
        "rules": len(rule_list),
        "files": len(by_file),
        "valid_examples": sum(1 for e in examples if e.polarity == "valid"),
        "invalid_examples": sum(1 for e in examples if e.polarity == "invalid"),
        "morphemes": len(list(R.morphemes())),
        "particles": len(R.particle_forms()),
        "suffixes": len(R.suffix_forms()),
        "demo_words": len(R.load_example_lexicon()),
        "banned_forms": len(R.load_originality()),
        "by_category": dict(sorted(by_category.items())),
        "by_file": dict(sorted(by_file.items())),
        "min_valid_per_rule": min((len(r.raw["valid"]) for r in rule_list), default=0),
        "min_invalid_per_rule": min((len(r.raw["invalid"]) for r in rule_list), default=0),
    }
