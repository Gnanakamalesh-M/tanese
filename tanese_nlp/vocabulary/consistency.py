"""Do the vocabulary rules contradict themselves, the phonology, or the grammar?

Thirteen deterministic checks over spec/vocabulary_rules.yaml. No LLM is involved and none
could be: a rule set either contradicts itself or it does not, and an answer that is
sometimes wrong would be worse than no answer.

Errors are returned as strings rather than raised, so one run reports every problem.

What a green run proves, check by check:

    1   every root shape is stated in terms the checker can apply, and the forms this file
        offers as examples of a shape really have that shape
    2   CROSS-PHASE: every permitted root final concatenates legally with every suffix
        declared in spec/grammar_rules/. This is the check that holds RS-FINAL to its
        reason; it fails if a later phase adds a vowel-initial suffix
    3   every compound pattern is multi-word and head-final, so none contradicts
        GR-NOUN-004, and each part of a compound example is a legal word
    4   nothing this file introduces collides with a declared particle, suffix, pronoun or
        demo root
    5   every form introduced here clears both originality gates
    6   the loan tables are well formed: no duplicate or doubly-listed source sound, every
        target is a real grapheme, the repair steps are numbered consecutively, every
        `steps_fired` names a declared step, and the LLM is permitted at one stage only
    7   the adapter reproduces every declared `adaptation_examples` output and every
        declared rejection, by code and by offending sound
    8   every word of a VALID example is accounted for: a demo root, a declared
        illustrative form, an adapted loan, or one of those plus declared suffixes, so a
        valid example cannot introduce a word in passing. Invalid examples are exempt --
        many are invalid precisely because of the form they contain
    9   every example's declared legality is true -- a `legal` example passes the Phase 1A
        validator and round-trips through the script, an `illegal` one actually fails it
    10  the stratum share targets sum to at most 1
    11  CROSS-SPEC: every grapheme named here exists in spec/phonology.yaml, and every
        stratum a semantic field names exists above
    12  VR-* ids are unique and every rule has at least two valid and two invalid examples
    13  no form this file invents has leaked into data/vocabulary/

What it does NOT prove, repeated in README "Not verified" because it bounds the above:

  * A stratum label is unverifiable from a form. Nothing here can catch a native root
    mislabelled `tamil_inspired`, or a loan filed in the wrong semantic field -- those are
    the invalid examples of VR-STR-003 and VR-SEM-001, and they are author-asserted.
  * An `invalid` example is author-asserted in the same sense as in Phase 1B. Check 9
    proves its declared legality -- that a form claimed illegal really is rejected by the
    validator, and a form claimed legal really is a legal word. That it is *bad vocabulary*
    is a claim with a reason, not a result, and closure (check 8) deliberately does not
    apply to it.
  * Check 5 proves no listed source form was reused or approached. It is not evidence of
    absence from Japanese or Tamil, let alone from a third language.
  * The adapter is exercised on the nine declared examples and five declared rejections
    only. It has not been run over a real loanword list.

This module reads spec/ and data/vocabulary/ only. It never reads data/evaluation/.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tanese_nlp.grammar import rules as G
from tanese_nlp.phonology import spec_load as S
from tanese_nlp.phonology import validate
from tanese_nlp.script.convert import roman_to_script, script_to_roman
from tanese_nlp.vocabulary import loanwords as L
from tanese_nlp.vocabulary import rules as V

REPO_ROOT = V.REPO_ROOT
VOCABULARY_DIR = REPO_ROOT / "data" / "vocabulary"

# LOCKED decision 14: the LLM may propose candidates and nothing else.
LLM_STAGE = "candidate_generation"


def _declared_morphemes() -> dict[str, str]:
    """Every form spec/grammar_rules/ declares, mapped to the rule that declares it."""
    return {morpheme.form: morpheme.rule_id for morpheme in G.morphemes()}


# --------------------------------------------------------------------------------------
# 1-2  root shapes
# --------------------------------------------------------------------------------------


def check_root_shapes() -> list[str]:
    """Every declared shape is applicable, and the illustrative forms match their shape."""
    errors: list[str] = []
    counts = V.mora_counts()
    if counts["min"] > counts["max"]:
        errors.append(
            f"check 1: mora_counts min {counts['min']} exceeds max {counts['max']}, so no "
            f"root shape is satisfiable"
        )

    shape_ids = {entry["id"] for entry in V.root_shapes()}
    for required in ("RS-MIN", "RS-MAX", "RS-FINAL", "RS-RESERVED"):
        if required not in shape_ids:
            errors.append(f"check 1: root shape {required} is not declared")

    finals = set(V.permitted_finals())
    for entry in V.illustrative_forms():
        form = entry["form"]
        result = validate(form)
        if not result.ok:
            errors.append(f"check 1: illustrative form {form!r} is not legal: {result}")
            continue
        if not counts["min"] <= result.mora_count <= counts["max"]:
            errors.append(
                f"check 1: illustrative form {form!r} has {result.mora_count} moras, outside "
                f"the declared range {counts['min']}-{counts['max']}"
            )
        if form[-1] not in finals:
            errors.append(
                f"check 1: illustrative form {form!r} ends in {form[-1]!r}, which is not a "
                f"permitted final ({sorted(finals)})"
            )
    return errors


def check_suffix_concatenation() -> list[str]:
    """RS-FINAL's reason, proved: every permitted final takes every declared suffix.

    This is the cross-phase check. RS-FINAL permits exactly the finals that concatenate
    legally with the Phase 1B suffix inventory, so the rule is only true as long as that
    inventory stays consonant-initial. A vowel-initial suffix added in a later phase makes
    this fail rather than making RS-FINAL quietly wrong.
    """
    errors: list[str] = []
    suffixes = sorted(G.suffix_forms())
    if not suffixes:
        return ["check 2: spec/grammar_rules/ declares no suffixes, so RS-FINAL is untested"]

    # A minimal legal stem per permitted final, built from the inventory rather than named,
    # so this does not depend on any particular demo word existing. A vowel final needs an
    # onset before it (`kai` would be hiatus, not a stem), and the moraic nasal needs a
    # vowel before it.
    stems = {
        final: "katan" if final == "n" else f"kat{final}" for final in V.permitted_finals()
    }
    for final, stem in stems.items():
        if not validate(stem).ok:
            errors.append(f"check 2: test stem {stem!r} for final {final!r} is not itself legal")
            continue
        for suffix in suffixes:
            joined = stem + suffix
            result = validate(joined)
            if not result.ok:
                errors.append(
                    f"check 2: a root ending in {final!r} plus suffix -{suffix} gives "
                    f"{joined!r}, which is illegal ({'; '.join(result.codes)}). RS-FINAL "
                    f"claims every permitted final concatenates with every declared suffix"
                )
    return errors


# --------------------------------------------------------------------------------------
# 3  compounds
# --------------------------------------------------------------------------------------


def check_compounds() -> list[str]:
    """No compound pattern may fuse or be head-initial, and the examples must match."""
    errors: list[str] = []
    for entry in V.compound_patterns():
        if entry["written"] != "separate_words":
            errors.append(
                f"check 3: compound pattern {entry['id']} is written {entry['written']!r}; "
                f"GR-NOUN-004 declares compounds unfused and lists the fused spelling as "
                f"invalid, so this contradicts an official rule"
            )
        if entry["head"] not in ("final", "none"):
            errors.append(
                f"check 3: compound pattern {entry['id']} has head {entry['head']!r}; LOCKED "
                f"decision 1 makes the language head-final"
            )

    separator = G.separator()
    for rule in V.load_rules():
        if rule.category != "compound":
            continue
        for example in rule.examples:
            if example.polarity != "valid" or example.legality != "legal":
                continue
            words = G.tokenize(example.roman)
            if any(not word for word in words):
                errors.append(
                    f"check 3: {example.label} {example.roman!r} has an empty token, so it is "
                    f"not tokenizable by GR-ORD-001"
                )
            if len(words) < 2 and rule.id != "VR-COMP-002":
                errors.append(
                    f"check 3: {example.label} {example.roman!r} is one word, but a compound "
                    f"entry is two or more (VR-COMP-001, separated by {separator!r})"
                )
    return errors


# --------------------------------------------------------------------------------------
# 4-5  collisions and originality
# --------------------------------------------------------------------------------------


def check_reserved_collisions() -> list[str]:
    """RS-RESERVED: no form introduced here may equal a declared morpheme or demo root."""
    errors: list[str] = []
    morphemes = _declared_morphemes()
    roots = G.roots()
    for form in sorted(V.declared_forms()):
        if form in morphemes:
            errors.append(
                f"check 4: {form!r} equals a form declared by {morphemes[form]} in "
                f"spec/grammar_rules/, which RS-RESERVED forbids"
            )
        if form in roots:
            errors.append(
                f"check 4: {form!r} equals a demo root in "
                f"spec/grammar_rules/_example_lexicon.yaml; a form invented here must be "
                f"distinct from one invented there, or the two files disagree about it"
            )
    return errors


def _banned_forms() -> list[str]:
    """The spellable entries of the originality list -- the only ones a form could equal."""
    return [entry["form"] for entry in G.load_originality() if not entry.get("unspellable")]


def check_originality() -> list[str]:
    """Both gates, applied to every form this file introduces."""
    errors: list[str] = []
    gate = V.originality()["new_root_gate"]
    floor = gate["min_edit_distance"]
    banned = _banned_forms()

    for form in sorted(V.declared_forms()):
        nearest, distance = min(
            ((other, V.levenshtein(form, other)) for other in banned),
            key=lambda pair: pair[1],
        )
        if distance == 0:
            errors.append(
                f"check 5: {form!r} equals the listed source form {nearest!r}, which the "
                f"hard gate (LOCKED decision 3) forbids outright"
            )
        elif distance < floor:
            errors.append(
                f"check 5: {form!r} is edit distance {distance} from the listed source form "
                f"{nearest!r}, below the declared floor of {floor}"
            )
    return errors


# --------------------------------------------------------------------------------------
# 6-7  the loan tables and the adapter
# --------------------------------------------------------------------------------------


def check_loan_tables() -> list[str]:
    """The substitution, unmapped, repair and pipeline tables must be well formed."""
    errors: list[str] = []
    document = V.document()

    seen: dict[str, str] = {}
    for table_name, entries in (
        ("loan_substitutions", document["loan_substitutions"]),
        ("unmapped", document["unmapped"]),
    ):
        for entry in entries:
            source = entry["source"]
            if source in seen:
                errors.append(
                    f"check 6: source sound {source!r} is listed in both {seen[source]} and "
                    f"{table_name}; a sound is either mapped or deliberately unmapped"
                )
            else:
                seen[source] = table_name

    graphemes = set(S.vowels()) | set(S.consonants())
    for entry in document["loan_substitutions"]:
        target = entry["tanese"]
        if target == "":
            continue  # deletion, which the schema documents
        try:
            parts = L.split_graphemes(target)
        except ValueError as exc:
            errors.append(f"check 6: substitution {entry['source']!r} -> {target!r}: {exc}")
            continue
        for part in parts:
            if part not in graphemes:
                errors.append(
                    f"check 6: substitution {entry['source']!r} -> {target!r} uses {part!r}, "
                    f"which is not a grapheme in spec/phonology.yaml"
                )

    steps = [entry["step"] for entry in V.repairs()]
    if steps != list(range(1, len(steps) + 1)):
        errors.append(
            f"check 6: repair steps are numbered {steps}; they must be consecutive from 1, "
            f"because the adapter applies them in that order"
        )

    declared = V.repair_ids()
    for entry in V.adaptation_examples():
        for step in entry["steps_fired"]:
            if step not in declared:
                errors.append(
                    f"check 6: adaptation example {entry['source_word']!r} names step "
                    f"{step!r}, which is not a declared repair"
                )

    for entry in V.pipeline():
        if entry["llm_allowed"] and entry["stage"] != LLM_STAGE:
            errors.append(
                f"check 6: pipeline stage {entry['id']} ({entry['stage']}) allows the LLM. "
                f"LOCKED decision 14 permits it only at {LLM_STAGE}"
            )
    stages = [entry["id"] for entry in V.pipeline()]
    if stages != sorted(stages):
        errors.append(f"check 6: pipeline stages are not in id order: {stages}")
    return errors


def check_adapter_matches_spec() -> list[str]:
    """The adapter must reproduce every declared output and every declared rejection."""
    errors: list[str] = []
    for entry in V.adaptation_examples():
        result = L.adapt(entry["segments"], entry["source_word"])
        if not result.ok:
            errors.append(
                f"check 7: {entry['source_word']!r} should adapt to {entry['expect']!r} but "
                f"was rejected: {result}"
            )
            continue
        if result.form != entry["expect"]:
            errors.append(
                f"check 7: {entry['source_word']!r} adapts to {result.form!r}, but the spec "
                f"declares {entry['expect']!r}"
            )
        if list(result.steps_fired) != entry["steps_fired"]:
            errors.append(
                f"check 7: {entry['source_word']!r} fired {list(result.steps_fired)}, but the "
                f"spec declares {entry['steps_fired']}"
            )

    for entry in V.adaptation_rejections():
        result = L.adapt(entry["segments"], entry["source_word"])
        if result.ok:
            errors.append(
                f"check 7: {entry['source_word']!r} should be rejected with {entry['code']} "
                f"on {entry['offending']!r}, but adapted to {result.form!r}"
            )
            continue
        if result.code != entry["code"]:
            errors.append(
                f"check 7: {entry['source_word']!r} was rejected {result.code}, but the spec "
                f"declares {entry['code']}"
            )
        if result.offending != entry["offending"]:
            errors.append(
                f"check 7: {entry['source_word']!r} was rejected on {result.offending!r}, but "
                f"the spec names {entry['offending']!r}"
            )

    # Every deliberately unmapped sound must actually be refused, not just listed.
    for source, code in sorted(V.unmapped().items()):
        result = L.adapt(["k", "a", source], f"ka+{source}")
        if result.ok:
            errors.append(
                f"check 7: unmapped sound {source!r} was adapted to {result.form!r} instead of "
                f"being rejected {code}"
            )
        elif result.code != code or result.offending != source:
            errors.append(
                f"check 7: unmapped sound {source!r} was rejected as "
                f"{result.code}/{result.offending!r}, not {code}/{source!r}"
            )
    return errors


# --------------------------------------------------------------------------------------
# 8-9  the examples
# --------------------------------------------------------------------------------------


def _accounted_forms() -> set[str]:
    """Every word an example may be built from."""
    return (
        set(G.roots())
        | set(_declared_morphemes())
        | set(V.declared_forms())
        | set(G.particle_forms())
        | set(G.suffix_forms())
        | set(G.word_forms())
    )


def _segmentable(word: str, known: set[str]) -> bool:
    """Is `word` a known form, or a known form plus declared suffixes?

    The same naive stripping as the grammar checker's segmenter, and with the same
    limitation: no notion of productivity or ambiguity. It is used only to confirm an
    example word is accounted for, which is all check 8 claims.
    """
    if word in known:
        return True
    for suffix in G.suffix_forms():
        if word.endswith(suffix) and len(word) > len(suffix):
            if _segmentable(word[: -len(suffix)], known):
                return True
    return False


def check_example_closure() -> list[str]:
    """Every word of a VALID example is a demo root, a form declared here, or a derivation.

    Valid examples only: see the comment below.
    """
    errors: list[str] = []
    known = _accounted_forms()
    for example in V.examples():
        if example.polarity != "valid":
            # An invalid example is frequently invalid *because* of the form it contains --
            # a banned source form, a malformed root, a changed stem -- so closure cannot
            # apply to it. The same scoping as the grammar checker's check 9. Invalid
            # examples are still held to check 9 here.
            continue
        for word in example.words:
            if not word:
                errors.append(f"check 8: {example.label} {example.roman!r} has an empty token")
                continue
            if _segmentable(word, known):
                continue
            errors.append(
                f"check 8: {example.label} uses {word!r}, which is not a demo root, a form "
                f"declared in spec/vocabulary_rules.yaml, or either plus declared suffixes. "
                f"An example may not introduce a word in passing"
            )
    return errors


def check_example_legality() -> list[str]:
    """Each example's declared legality must be true, and a legal one must round-trip."""
    errors: list[str] = []
    for example in V.examples():
        words = example.words
        results = {word: validate(word) for word in words if word}
        illegal = {word: result for word, result in results.items() if not result.ok}

        if example.legality == "illegal":
            if not illegal:
                errors.append(
                    f"check 9: {example.label} {example.roman!r} is declared "
                    f"`phonotactics: illegal`, but every word in it is legal. Either the "
                    f"label or the example is wrong"
                )
            if example.tanese is not None:
                errors.append(
                    f"check 9: {example.label} is declared illegal but carries a script form. "
                    f"An illegal word has none -- the converter refuses to produce one"
                )
            continue

        if illegal:
            detail = "; ".join(f"{word}: {'/'.join(r.codes)}" for word, r in illegal.items())
            errors.append(
                f"check 9: {example.label} {example.roman!r} is declared legal but is not "
                f"({detail})"
            )
            continue

        if example.tanese is None:
            errors.append(
                f"check 9: {example.label} {example.roman!r} is legal but has no script form"
            )
            continue

        expected = " ".join(roman_to_script(word) for word in words)
        if example.tanese != expected:
            errors.append(
                f"check 9: {example.label} script form does not match its romanization\n"
                f"           declared: {example.tanese}\n"
                f"           expected: {expected}"
            )
            continue
        back = " ".join(script_to_roman(part) for part in example.tanese.split(" "))
        if back != example.roman:
            errors.append(
                f"check 9: {example.label} does not round-trip: {example.roman!r} -> script "
                f"-> {back!r}"
            )
    return errors


# --------------------------------------------------------------------------------------
# 10-12  the declared tables themselves
# --------------------------------------------------------------------------------------


def check_share_targets() -> list[str]:
    """The stratum quotas must be reachable: they may not sum to more than the lexicon."""
    total = sum(entry["share_target"] for entry in V.strata())
    if total > 1.000001:  # a float sum of declared decimals
        return [
            f"check 10: stratum share targets sum to {total:.3f}, which is more than the "
            f"whole lexicon; no Phase 2 lexicon could meet them all"
        ]
    return []


def check_cross_spec_references() -> list[str]:
    """Every grapheme and every stratum named here must exist where it is defined."""
    errors: list[str] = []
    graphemes = set(S.vowels()) | set(S.consonants())
    for entry in V.document()["permitted_finals"]:
        for grapheme in entry["graphemes"]:
            if grapheme not in graphemes:
                errors.append(
                    f"check 11: permitted final {grapheme!r} is not a grapheme in "
                    f"spec/phonology.yaml"
                )

    stratum_ids = {entry["id"] for entry in V.strata()}
    for field in V.semantic_fields():
        if field["stratum"] not in stratum_ids:
            errors.append(
                f"check 11: semantic field {field['id']!r} names stratum "
                f"{field['stratum']!r}, which is not declared"
            )

    for entry in V.strata():
        if entry["id"] == "loan" and not entry["borrows_form"]:
            errors.append("check 11: the `loan` stratum must declare borrows_form: true")
        if entry["id"] != "loan" and entry["borrows_form"]:
            errors.append(
                f"check 11: stratum {entry['id']!r} declares borrows_form: true. VR-STR-002 "
                f"permits a borrowed form only in the `loan` stratum"
            )
    return errors


def check_rule_shape() -> list[str]:
    """Ids are unique and every rule carries at least two valid and two invalid examples."""
    errors: list[str] = []
    seen: set[str] = set()
    for rule in V.load_rules():
        if rule.id in seen:
            errors.append(f"check 12: duplicate rule id {rule.id!r}")
        seen.add(rule.id)
        for polarity in ("valid", "invalid"):
            count = len(rule.raw.get(polarity, []))
            if count < 2:
                errors.append(
                    f"check 12: {rule.id} has {count} {polarity} example(s); the rule format "
                    f"requires at least 2"
                )
    return errors


# --------------------------------------------------------------------------------------
# 13  nothing invented here is vocabulary
# --------------------------------------------------------------------------------------


def _vocabulary_forms(vocabulary_dir: Path = VOCABULARY_DIR) -> dict[str, str]:
    """Every form in data/vocabulary/, mapped to the file it is in."""
    found: dict[str, str] = {}
    if not vocabulary_dir.is_dir():
        return found
    for path in sorted(vocabulary_dir.glob("*.yaml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            continue
        for entry in document.get("words", []) or []:
            if isinstance(entry, dict) and isinstance(entry.get("form"), str):
                found[entry["form"]] = path.name
    return found


def check_not_vocabulary(vocabulary_dir: Path = VOCABULARY_DIR) -> list[str]:
    """No form invented in this file may appear in data/vocabulary/.

    The same guarantee the grammar's check 12 gives the demo wordlist, extended to the
    illustrative roots and to every adapted loan output. An adapted loan demonstrates the
    adapter; it has had no collision check and no human approval, so it is not a word of the
    language. Phase 2 must re-derive anything it wants through the pipeline, which may
    reject it.
    """
    errors: list[str] = []
    vocabulary = _vocabulary_forms(vocabulary_dir)
    for form in sorted(V.declared_forms()):
        if form in vocabulary:
            errors.append(
                f"check 13: {form!r} is declared in spec/vocabulary_rules.yaml as an "
                f"illustration and also appears in data/vocabulary/{vocabulary[form]}. "
                f"Illustrations are experimental and must not be copied into the lexicon"
            )
    for entry in V.illustrative_forms():
        if entry["status"] != "experimental":
            errors.append(
                f"check 13: illustrative form {entry['form']!r} has status "
                f"{entry['status']!r}; only `experimental` is permitted here"
            )
    return errors


# --------------------------------------------------------------------------------------
# entry points
# --------------------------------------------------------------------------------------

CHECKS = (
    ("1 root shapes", check_root_shapes),
    ("2 suffix concatenation", check_suffix_concatenation),
    ("3 compounds unfused", check_compounds),
    ("4 reserved collisions", check_reserved_collisions),
    ("5 originality gates", check_originality),
    ("6 loan tables well formed", check_loan_tables),
    ("7 adapter matches spec", check_adapter_matches_spec),
    ("8 example closure", check_example_closure),
    ("9 example legality + script", check_example_legality),
    ("10 share targets reachable", check_share_targets),
    ("11 cross-spec references", check_cross_spec_references),
    ("12 rule shape", check_rule_shape),
    ("13 illustrations are not vocabulary", check_not_vocabulary),
)


def check_all() -> list[str]:
    """Run every check. Empty list means the vocabulary rules are internally consistent."""
    errors: list[str] = []
    for _, check in CHECKS:
        errors.extend(check())
    return errors


def originality_report() -> list[tuple[str, str, int]]:
    """Distance from every form this file introduces to its nearest listed source form.

    Reported rather than gated, so the numbers behind check 5 are visible instead of
    implied.
    """
    banned = _banned_forms()
    rows: list[tuple[str, str, int]] = []
    for form in sorted(V.declared_forms()):
        nearest, distance = min(
            ((other, V.levenshtein(form, other)) for other in banned),
            key=lambda pair: pair[1],
        )
        rows.append((form, nearest, distance))
    return sorted(rows, key=lambda row: row[2])


def retroactive_exceptions() -> list[tuple[str, str, int]]:
    """Existing official and demo forms that the new-root gate would have rejected.

    The gate is declared non-retroactive, which is only honest if what it spares is on the
    record. These are reported by scripts/check_vocabulary.py and never cause a failure.
    """
    floor = V.originality()["new_root_gate"]["min_edit_distance"]
    banned = _banned_forms()
    rows: list[tuple[str, str, int]] = []
    for form in sorted(set(G.roots()) | set(_declared_morphemes())):
        nearest, distance = min(
            ((other, V.levenshtein(form, other)) for other in banned),
            key=lambda pair: pair[1],
        )
        if distance < floor:
            rows.append((form, nearest, distance))
    return sorted(rows, key=lambda row: (row[2], row[0]))


def oversized_loans() -> list[tuple[str, str, int]]:
    """Adapted loans that are legal words but exceed the root mora cap (RS-MAX).

    LR-5's `problems` field predicts this; the report makes it a number rather than a
    warning, and names which example it is.
    """
    cap = V.mora_counts()["max"]
    rows: list[tuple[str, str, int]] = []
    for entry in V.adaptation_examples():
        count = validate(entry["expect"]).mora_count
        if count > cap:
            rows.append((entry["source_word"], entry["expect"], count))
    return rows


def stats() -> dict[str, Any]:
    """The counts that go in the README. Printed, never hand-typed."""
    rule_list = V.load_rules()
    example_list = V.examples()
    by_category: dict[str, int] = {}
    for rule in rule_list:
        by_category[rule.category] = by_category.get(rule.category, 0) + 1
    return {
        "rules": len(rule_list),
        "valid_examples": sum(1 for e in example_list if e.polarity == "valid"),
        "invalid_examples": sum(1 for e in example_list if e.polarity == "invalid"),
        "illegal_examples": sum(1 for e in example_list if e.legality == "illegal"),
        "strata": len(V.strata()),
        "root_shapes": len(V.root_shapes()),
        "semantic_fields": len(V.semantic_fields()),
        "compound_patterns": len(V.compound_patterns()),
        "substitutions": len(V.substitutions()),
        "unmapped": len(V.unmapped()),
        "repairs": len(V.repairs()),
        "adaptation_examples": len(V.adaptation_examples()),
        "adaptation_rejections": len(V.adaptation_rejections()),
        "pipeline_stages": len(V.pipeline()),
        "illustrative_forms": len(V.illustrative_forms()),
        "declared_forms": len(V.declared_forms()),
        "by_category": dict(sorted(by_category.items())),
        "min_valid_per_rule": min((len(r.raw["valid"]) for r in rule_list), default=0),
        "min_invalid_per_rule": min((len(r.raw["invalid"]) for r in rule_list), default=0),
    }
