"""The real rule tree, checked rule by rule and example by example.

These tests assert the properties docs/SPEC.md's Phase 1B done-criteria name, over the
actual contents of spec/grammar_rules/ -- so they fail if a later phase edits a rule into
an inconsistent state, not only when the checker script is run by hand.
"""

from __future__ import annotations

import pytest

from tanese_nlp.grammar import contradictions as C
from tanese_nlp.grammar import rules as R
from tanese_nlp.phonology.phonotactics import validate
from tanese_nlp.script.convert import roman_to_script

RULES = R.load_rules()
EXAMPLES = [example for rule in RULES for example in rule.examples]
MIN_RULES = 40


def _ids(items):
    return [item.label if isinstance(item, R.Example) else item.id for item in items]


def test_the_rule_tree_is_not_empty():
    assert RULES, "no rules loaded from spec/grammar_rules/"


def test_done_criterion_rule_count():
    assert len(RULES) >= MIN_RULES


def test_rule_ids_are_unique():
    ids = [rule.id for rule in RULES]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("rule", RULES, ids=_ids(RULES))
def test_done_criterion_two_examples_of_each_polarity(rule: R.Rule):
    assert len(rule.raw["valid"]) >= 2
    assert len(rule.raw["invalid"]) >= 2


@pytest.mark.parametrize("rule", RULES, ids=_ids(RULES))
def test_rules_that_introduce_forms_declare_them(rule: R.Rule):
    """The conditional requirement in grammar_rule.schema.json, asserted independently."""
    if rule.category not in R.MORPHEME_CATEGORIES:
        return
    assert rule.morphemes or (rule.category == "morphology" and rule.slot_order)


@pytest.mark.parametrize("example", EXAMPLES, ids=_ids(EXAMPLES))
def test_every_example_word_is_a_legal_tanese_word(example: R.Example):
    """Invalid examples included: they must fail on grammar, never on phonotactics."""
    for token in R.tokenize(example.roman):
        result = validate(token)
        assert result.ok, f"{token!r}: {result}"


@pytest.mark.parametrize("example", EXAMPLES, ids=_ids(EXAMPLES))
def test_the_script_field_is_the_converters_output(example: R.Example):
    tokens = R.tokenize(example.roman)
    expected = R.separator().join(roman_to_script(token) for token in tokens)
    assert example.tanese == expected


@pytest.mark.parametrize("example", EXAMPLES, ids=_ids(EXAMPLES))
def test_tokenizer_validator_and_script_agree_on_word_count(example: R.Example):
    """One definition of `word` (GR-ORD-001), used in all three places."""
    tokens = R.tokenize(example.roman)
    assert all(tokens), "an empty token means a double separator"
    assert len(tokens) == len(example.tanese.split(R.separator()))
    assert len(tokens) == len([validate(token) for token in tokens])


@pytest.mark.parametrize(
    "example",
    [e for e in EXAMPLES if e.polarity == "valid"],
    ids=_ids([e for e in EXAMPLES if e.polarity == "valid"]),
)
def test_valid_examples_use_declared_forms_only(example: R.Example):
    for token in R.tokenize(example.roman):
        assert C.legal_readings(token), f"{token!r} is not a demo root plus declared suffixes"


def test_word_boundary_is_declared_exactly_once():
    boundary = R.word_boundary()
    assert boundary["suffixes_attached"] is True
    assert boundary["particles_separate"] is True
    assert boundary["separator"] == " "


def test_the_word_separator_is_not_the_romanization_separator():
    """The apostrophe is an intra-word marker; the word separator is a different thing."""
    from tanese_nlp.phonology import spec_load as S

    assert S.separator() == "'"
    assert R.separator() != S.separator()


def test_slot_order_matches_the_locked_decision():
    declared = [rule.slot_order for rule in RULES if rule.slot_order]
    assert declared, "no rule declares the verb slot order"
    for order in declared:
        assert order == C.LOCKED_SLOT_ORDER


@pytest.mark.parametrize(
    ("form", "legal", "why"),
    [
        ("mandu", True, "citation form: no suffix at all"),
        ("manduke", True, "casual non-past: tense present, politeness empty"),
        ("manduso", True, "imperative: a tenseless mood"),
        ("mandukeso", False, "tense with a tense-forbidden mood"),
        ("mandumi", False, "politeness with no tense on an indicative verb"),
        ("mandusunke", False, "politeness before tense"),
        ("mandulo", True, "hortative: tenseless"),
        ("manduthe", True, "polite request: tenseless"),
        ("mandukele", True, "desiderative requires tense, and has it"),
        ("mandule", False, "desiderative with no tense"),
    ],
)
def test_citation_imperative_and_indicative_are_distinguished(form, legal, why):
    """GR-VERB-002, GR-VERB-006 and the moods' `tense` fields, read off the spec."""
    assert bool(C.legal_readings(form)) is legal, why


@pytest.mark.parametrize(
    ("particle", "function"),
    [
        ("lun", "negative_conditional"),
        ("thon", "prohibitive"),
        ("thenu", "quotative"),
        ("belu", "topic"),
        ("kodhu", "ablative"),
    ],
)
def test_a_multi_mora_particle_is_one_whole_word(particle, function):
    """`lun` is the negative-conditional particle, never `lu` (genitive) plus a stray `n`.

    Three separate claims, because each could break on its own: the form is declared whole,
    the tokenizer keeps it whole, and the segmenter does not take it apart.
    """
    declared = {m.form: m for m in R.morphemes()}
    assert declared[particle].function == function
    assert declared[particle].kind == "particle"

    # the tokenizer treats it as one word, in a real sentence from the rule it belongs to
    sentence = f"uthe dhen ikkedhonhi {particle}"
    assert R.tokenize(sentence) == ["uthe", "dhen", "ikkedhonhi", particle]

    # the segmenter reads it as a whole particle and offers no decomposition at all
    assert C.legal_readings(particle) == [[]]
    assert C._analyses(particle) == []


@pytest.mark.parametrize(
    ("whole", "prefix"),
    [
        ("lun", "lu"),  # genitive particle + a stray `n`
        ("thenu", "the"),  # polite-request mood suffix + `nu`
        ("belu", "be"),
        ("thon", "th"),
    ],
)
def test_a_particle_is_never_read_as_a_shorter_form_plus_a_remainder(whole, prefix):
    """No analysis of the whole form uses the shorter one, and the leftover is not a suffix.

    The leftover is tested against the *suffix* inventory specifically, because that is what
    the segmenter strips. A particle ending in another particle is harmless for the same
    reason -- and `belu` does end in the genitive `lu`, which is why the two inventories are
    asserted disjoint elsewhere and why particles are never stripped (see
    `test_the_segmenter_never_strips_a_particle`).
    """
    remainder = whole[len(prefix) :]

    assert remainder not in R.suffix_forms(), (
        f"{remainder!r} is a declared suffix, so {whole!r} could be stripped apart"
    )
    for analysis in C._analyses(whole):
        assert prefix not in {m.form for m in analysis}


def test_the_segmenter_never_strips_a_particle():
    """Particles are words (GR-ORD-001), so gluing one to a noun must not become legal."""
    assert C.legal_readings("namido") == []
    assert C.legal_readings("naminhu") == []
    assert C.legal_readings("nami") != []


def test_no_single_letter_morpheme_exists():
    """A one-letter form would make almost every word ambiguous to the stripper."""
    for morpheme in R.morphemes():
        assert len(morpheme.form) >= 2, morpheme


def test_every_declared_form_is_a_legal_word_and_not_a_banned_one():
    banned = {entry["form"] for entry in R.load_originality()}
    for morpheme in R.morphemes():
        assert validate(morpheme.form).ok, morpheme.form
        assert morpheme.form not in banned, morpheme.form


def test_particle_and_suffix_inventories_are_disjoint():
    assert not (R.particle_forms() & R.suffix_forms())


def test_demo_lexicon_is_experimental_and_legal():
    for word in R.load_example_lexicon():
        assert word["status"] == "experimental"
        assert validate(word["form"]).ok, word["form"]


def test_every_morpheme_declaring_rule_is_categorised_as_one():
    """The schema's conditional requirement must be doing real work.

    If a rule that introduces a form were filed under `syntax`, the requirement would be
    satisfied vacuously. Its morphemes would still be checked -- checks 1, 2, 3 and 9 ignore
    the category -- but the categorisation would be wrong, so it is an error here.
    """
    assert C.misfiled_morpheme_declarations() == []
    for rule in RULES:
        if rule.morphemes:
            assert rule.category in R.MORPHEME_CATEGORIES, rule.id


def test_declared_morphemes_are_checked_whatever_the_category():
    """The stronger guarantee: the checks iterate over forms, not over categories."""
    declaring = [rule for rule in RULES if rule.morphemes]
    assert len(list(R.morphemes())) == sum(len(rule.morphemes) for rule in declaring)
    assert {rule.category for rule in declaring} <= R.MORPHEME_CATEGORIES


def test_the_whole_checker_passes_on_the_real_spec():
    assert C.check_all() == []
    assert C.missing_morpheme_declarations() == []
    assert C.misfiled_morpheme_declarations() == []
