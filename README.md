# Tanese

Tanese is a constructed language inspired by Tamil and Japanese, plus an NLP/LLM toolkit
built around it. It is a student project: the aim is something finishable, internally
consistent, and honestly evaluated — not a complete real-world language ecosystem.

Tamil and Japanese are inspirations only. Tanese has its own phonology, script, grammar,
and vocabulary, and nothing in it is a copy of either source language.

> **Status: Phase 1B (grammar core) complete.** Tanese now has a sound inventory, a
> canonical spelling, a writing system and a grammar — 54 rules, all machine-readable in
> `spec/`, checked for self-contradiction by a script. There is still no vocabulary: the
> words in the grammar examples are explicitly-marked placeholders, not a lexicon. See
> [Not verified](#not-verified) below.

## How the project is organised

`spec/*.yaml` is the source of truth for the language. Documentation is derived from it,
never the other way round. Rules define Tanese; the LLM assists but never changes official
rules or vocabulary.

| Path | Contents |
| --- | --- |
| `docs/SPEC.md` | Locked decisions, current phase, per-phase done-criteria |
| `docs/VISION.md` | Long-form context (not built from directly) |
| `docs/CHANGES.md` | Proposed changes to locked decisions |
| `spec/` | Machine-readable language rules (YAML) |
| `spec/schemas/` | JSON Schemas the rule files are validated against |
| `tanese_nlp/phonology/` | Romanization lexer and phonotactic validator |
| `spec/grammar_rules/` | The grammar: one YAML file per topic, plus two support files |
| `tanese_nlp/script/` | Romanization ↔ script converter |
| `tanese_nlp/grammar/` | Rule loader, tokenizer, contradiction checker |
| `tanese_nlp/` | Python toolkit (tokenizer, morphology, grammar, embeddings, …) |
| `data/` | Vocabulary, grammar, translation, conversation, evaluation data |
| `llm/` | Prompts, RAG, fine-tuning, LLM evaluation |
| `backend/`, `frontend/` | Web app (Phase 6) |
| `scripts/` | Plain-python entry points; no `make` |
| `tests/` | Unit and integration tests |

Most of these directories are currently empty placeholders for later phases. `data/` in
particular is still entirely empty — Phase 1B added no data files, only spec and code.

## Install

Requires **Python 3.11** (the version CI uses).

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` uses exact pins, resolved and verified on Python 3.11.9.

## Running the checks

One command runs everything, and CI runs the same one:

```
python scripts/run_checks.py
```

It runs four steps and stops at the first failure:

1. **lint** — `ruff check .`
2. **tests** — `pytest`
3. **yaml-schema** — `scripts/check_yaml_schema.py`, validating every `spec/*.yaml`
   against `spec/schemas/` and checking that grammar-rule ids are globally unique
4. **grammar** — `scripts/check_grammar.py`, the twelve contradiction checks over
   `spec/grammar_rules/`, which also prints the rule and example counts

Each can also be run on its own, as can the word generator:

```
python scripts/check_yaml_schema.py
python scripts/check_grammar.py
python scripts/gen_words.py
```

All scripts work from any working directory.

## The language so far (Phase 1A)

Everything below is defined in `spec/phonology.yaml`, `spec/romanization.yaml` and
`spec/script.yaml`, which are the source of truth; this section only summarises them.

**Sounds.** Five vowels (`a i u e o`) with a length contrast, and 16 consonants including a
retroflex series: `p b t d th dh k g s m n nh r l w y`. There is no `/h/` phoneme — which is
what lets `h` act as a pure retroflex marker, so `th dh nh` are single consonants and
nothing can be confused with a non-existent `ha`.

**Spelling** is the canonical form (locked decision 12) and is plain lowercase ASCII: long
vowels double (`kaa`), geminates repeat the whole onset (`kaththa`), the moraic nasal is `n`,
and an apostrophe marks a moraic `n` before a vowel, `y` or `w` (`kan'a` is /kan.a/, while
`kana` is /ka.na/). The parse is deterministic longest-match, so every legal word has exactly
one spelling and every spelling exactly one reading.

**Words** are built from moras, of which there are four kinds: syllabic `(C)V`, a length
mora, the moraic nasal, and a gemination mora. Syllables are `(C)V(N)`, so a long vowel is
two moras rather than one.

**Script** is an original featural abugida. 21 hand-designed atoms (6 place frames, 7 manner
marks, 5 vowel marks, 3 standalone marks) compose 17 bases and, from those, one glyph per
legal mora. Unlike Indic abugidas it has no inherent vowel and no virama: every syllabic
glyph carries an explicit vowel mark. The canonical script form is the dot-joined id
sequence, with a Private Use Area codepoint per mora reserved for later rendering.

```
kaatha   -> TS-KA.TS-LONG.TS-THA  -> kaatha
kan'a    -> TS-KA.TS-NASAL.TS-A   -> kan'a
kaththa  -> TS-KA.TS-GEM.TS-THA   -> kaththa
```

Rejections name the constraint they broke, so they can be explained rather than just counted:

```
kaia     PT-008  vowel 'i' has no onset and is not word-initial
kanya    PT-010  a moraic n before a vowel, y or w must be written with an apostrophe
kanhnha  PT-007  'nh' may not be geminated
kaaa     PT-009  a vowel may be lengthened only once
```

The design decisions behind all of this — why 16 consonants, why `h` marks retroflexion, why
`/n/` cannot geminate, why hiatus is banned — are recorded with their alternatives and known
problems in the `reason`, `alternatives` and `problems` fields of the spec files themselves.

## The grammar so far (Phase 1B)

`spec/grammar_rules/*.yaml` is the source of truth; this section summarises it.

**Shape of the language.** SOV and head-final: modifiers, relative clauses and subordinate
clauses all precede what they modify, and the verb closes the clause. Relations are carried
by postposition particles, not by word order, so arguments may be reordered freely before
the verb. A root and its suffixes are one word; every particle is a separate word.

**Particles** (13). Eight relations — `dhen` subject, `do` object, `thin` dative/goal,
`lu` genitive, `ban` locative, `sen` instrumental, `nhu` comitative, `kodhu` ablative — plus
five clause-level ones: `belu` topic, `wen` yes/no question, `thenu` quotative, `thon`
prohibitive, `lun` negative conditional. A noun phrase takes exactly one.

**Verbs** are `ROOT - ASPECT - TENSE - MOOD - POLITENESS` (locked decision 6), suffixing
only, with an invariant root and no agreement for person, number or gender.

```
mandu              eat (citation form -- not a finite verb)
manduke            eats                       mandu-ke        eat-NPST
manduridhosun      was eating (formal)        mandu-ri-dho-sun  eat-PROG-PST-FORMAL
mandukenhimi       does not eat (neutral)     mandu-ke-nhi-mi   eat-NPST-NEG-NEUTRAL
manduso            eat!                       mandu-so        eat-IMP
mandukenhi thon    do not eat                 (two words -- see below)
```

Three politeness levels, marked once per clause on the final verb: casual is the empty
slot, `-mi` is neutral, `-sun` is formal. Tense is obligatory on an indicative verb, which
is what keeps the casual `manduke` distinct from the citation form `mandu`; the three
command moods (`-so` imperative, `-the` request, `-lo` hortative) are declared tenseless
and forbid it instead.

**The known wart.** Negation `-nhi` sits in the mood slot, so it cannot combine with another
mood. The prohibitive and the negative conditional are therefore two words where their
positive counterparts are one (`manduso` → `mandukenhi thon`; `ikkedhobo` → `ikkedhonhi
lun`), and "does not want to" has no form at all. Each affected rule says so in its
`problems` field, and `docs/CHANGES.md` CH-002 records the slot change that would fix it if
Phase 3 shows the analytic forms do not work.

Every particle and suffix form is checked against `spec/grammar_rules/_originality.yaml`, a
list of 61 Japanese and Tamil particles, case endings, verbal endings and honorifics that a
Tanese form may not equal (locked decision 3). That check is what removed three forms from
the first draft: `kun` (Japanese honorific), `ge` (one vowel from Japanese *ga*) and `maa`
(colloquial Tamil address particle), replaced by `wen`, `dhen` and `belu`.

## Phase 1B results

Produced by `.venv\Scripts\python.exe scripts\check_grammar.py`:

```
== counts
  rules                54 in 10 files
  valid examples       108
  invalid examples     108
  declared morphemes   33 (13 particles, 14 suffixes)
  demo words           41 (experimental, not vocabulary)
  banned source forms  61

== checks
  ok    check 1 form uniqueness
  ok    check 2 function uniqueness
  ok    check 3 slot order
  ok    check 4 assertion conflict
  ok    check 5 example cross-check
  ok    check 6 example self-consistency
  ok    check 7 phonotactics
  ok    check 8 script fidelity
  ok    check 9 lexicon closure + originality
  ok    check 10 demo words legal
  ok    check 11 demo words experimental
  ok    check 12 demo words not in vocabulary
  ok    morpheme declarations by category
  ok    morpheme-declaring rules are categorised as such
```

What each check proves is in the module docstring of
`tanese_nlp/grammar/contradictions.py`; what they do **not** prove is in
[Not verified](#not-verified). Every check is itself tested by building a rule set that
breaks it (`tests/unit/test_contradictions.py`), so a green run is not green by accident.

Against `docs/SPEC.md`'s Phase 1B done-criteria:

| Criterion | Evidence |
| --- | --- |
| `spec/grammar_rules/*.yaml` covering word order, noun morphology, verb morphology, TAM, negation, questions, commands, pronouns, particles, politeness | ten rule files, one per topic; counts per file printed by `scripts\check_grammar.py` |
| ≥ 40 rules | **54**, printed by `scripts\check_grammar.py`, which fails below 40 |
| ≥ 2 valid + 2 invalid examples each | lowest observed is 2 and 2, printed by the same script; also asserted per rule in `tests/unit/test_grammar_rules.py` |
| Schema check passes | `scripts\check_yaml_schema.py` → `ok`, against an extended `grammar_rule.schema.json` (see `docs/CHANGES.md` CH-001) |
| No two rules contradict, checked by a script | the twelve checks above |

The example words come from `spec/grammar_rules/_example_lexicon.yaml`: 41 placeholder roots
that exist only so the examples can be read. They are **not** vocabulary — each is marked
`status: experimental`, the schema for that file permits no other value, and check 12 fails
if any of them ever appears in `data/vocabulary/`. Locked decision 14 reserves official
words for the Phase 2 pipeline, which must re-derive any of these it wants rather than copy
them.

`pytest` reports **1909 passed** (`.venv\Scripts\python.exe -m pytest`), up from 978 after
Phase 1A. Most of the growth is parametrised: each of the 216 examples is checked four
ways. All 33 declared morphemes sit in rules of category `particle` (13), `morphology` (8
rules declaring 11 suffixes), `pronoun` (2) and `politeness` (1); no rule filed under
`syntax` declares a form, which is asserted rather than assumed.

## Phase 1A results

Produced by `.venv\Scripts\python.exe scripts\gen_words.py`:

```
200 legal words, seed 1704
mora ids covered: 86/86
```

The generator builds to explicit coverage quotas and raises if any is unmet, so the corpus
cannot silently under-cover the glyph table: 94 words contain a long vowel, 73 a geminate,
50 a moraic nasal (10 of them the apostrophe case), and each retroflex consonant appears in
at least 22 words. These are legal *forms*, not vocabulary — nothing has a meaning yet, and
nothing is official (locked decision 14 reserves that for the Phase 2 pipeline).

Against `docs/SPEC.md`'s Phase 1A done-criteria:

| Criterion | Evidence |
| --- | --- |
| `spec/phonology.yaml`, `spec/script.yaml`, `spec/romanization.yaml` | all three exist and pass `python scripts/check_yaml_schema.py` against new schemas in `spec/schemas/` |
| Phonotactic validator | `tanese_nlp/phonology/` — `validate()` returns the broken constraint id, not just a boolean |
| Romanization ↔ script converter | `tanese_nlp/script/convert.py` — both the id form and the PUA form |
| Round-trip on 200 generated legal words | `tests/unit/test_script_roundtrip.py`, both script forms, and the corpus is asserted to cover all 86 mora ids |
| Validator accepts 30 legal, rejects 30 illegal | `tests/unit/test_phonotactics.py` — both lists are hand-written literals, independent of the generator, and each illegal word asserts the specific constraint it must trip |

`pytest` reports **978 passed** (`.venv\Scripts\python.exe -m pytest`), up from 22 after
Phase 0. Most of that growth is parametrised cases: the 200-word corpus is checked four ways.

## Phase 0 results

Produced by `.venv\Scripts\python.exe scripts\run_checks.py` on Python 3.11.9:

```
== summary
  PASS  lint
  PASS  tests
  PASS  yaml-schema

All checks passed.
```

`pytest` reports **22 passed** (`.venv\Scripts\python.exe -m pytest`). Those 22 tests cover
the schema validator and the check-runner wiring only — there is nothing else to test yet.

CI is green: [run #1](https://github.com/Gnanakamalesh-M/tanese/actions) on commit `5f47648`
ran the same `python scripts/run_checks.py` on Python 3.11 on a clean Ubuntu runner, after a
fresh `pip install -r requirements.txt`.

## Not verified

Honest list of things written but not actually demonstrated:

- **Installing from `requirements.txt` on Windows.** The clean install is verified on the CI
  runner's Ubuntu + Python 3.11 only; the local pins were read back from an already-populated
  `.venv`, so a from-scratch install on Windows has not been run.
- **CI on the Phase 1A and 1B commits.** All numbers above are from local runs on Python
  3.11.9. Phase 0's CI run #1 was green on commit `5f47648`; nothing since has been pushed.
- **Invalid examples are author-asserted.** The 108 invalid examples are labelled
  ungrammatical by me, with a reason each. Nothing *proves* they are: the rule-based grammar
  checker that could reject them is Phase 4. What the checks do prove is that each is a
  legal Tanese word sequence, spelled consistently with the script, tokenizable, and not
  claimed valid by any other rule. Until Phase 4 runs over them, "invalid" means "I say so,
  with a reason".
- **Contradictions that live only in prose.** Checks 5 and 6 compare example strings. Two
  rules whose `description` or `reason` disagree, while their examples do not overlap, will
  pass. Only the declared forms, slots, slot order and `asserts` keys are compared
  semantically; the prose is not.
- **The originality list is not exhaustive.** `_originality.yaml` holds the 61 Japanese and
  Tamil forms I could enumerate by hand, with a source and gloss each. A Tanese form that
  passes check 9 is *not* thereby proven absent from Japanese or Tamil, let alone from any
  third language — the check proves only that no listed form was reused. The `unspellable`
  flags in that file are verified against the phonotactic validator; the list's coverage is
  not verified at all.
- **The grammar has not been used.** No corpus, no conversation and no translation has been
  written in Tanese, so whether these 54 rules are usable together — rather than merely
  non-contradictory — is unknown. That is what Phase 3 is for. Three gaps are already known
  and recorded in the rules' own `problems` fields: a topicalised argument loses its
  relation (GR-PART-009), an embedded yes/no question has no form (GR-Q-004), and a
  negative desiderative has no form (GR-TAM-005).
- **The demo wordlist has had no collision checking.** The 41 placeholder roots were checked
  for phonotactic legality and exact duplication only. The collision detector (exact,
  phonetic, orthographic, semantic) is Phase 2, so two of them may well be confusably
  similar.
- **The glyph shapes.** `spec/script.yaml` describes each atom's shape in prose and reserves a
  PUA codepoint per mora, but nothing has been rendered — there is no SVG, no font and no
  image anywhere in the repo. Whether the 86 glyphs are actually legible, and in particular
  whether the three retroflexes are distinguishable from their alveolar counterparts, is
  unknown. Rendering is Phase 6.
- **Pronounceability.** The phonology is argued from general phonetics (which consonants can
  be audibly held, which contrasts a speaker could learn), not tested with speakers. No one
  has spoken Tanese.
- **The segmenter used by the checks is naive.** `contradictions.legal_readings()` strips
  declared suffixes with backtracking and asks whether a demo root is left. It has no notion
  of productivity, semantics or ambiguity resolution, and it is not the morphological
  analyzer — that is Phase 4. It is good enough to catch a typo or an undeclared form in an
  example, which is all it is used for.
- Everything from Phase 1C onward: the generated language specification, vocabulary, corpus,
  tokenizer, morphological analyzer, grammar checker, embeddings, RAG, translation, the web
  app, and all evaluation numbers. None of it exists yet.

## Evaluation and honesty notes

When results do arrive, they will follow the project's standing rules:

- every number in this README names the command that produced it;
- every method is compared against a fair baseline (plain rules, keyword search, no-RAG),
  reported even when the fancier method loses;
- translation metrics such as BLEU and chrF are **self-referential** for Tanese, because the
  language has no native speakers and the reference translations are produced by the same
  rule set being evaluated. They measure internal consistency, not translation quality.

## Roadmap

Phase 0 skeleton → 1A phonology/script → 1B grammar core → 1C spec document → 2 lexicon →
3 corpus → 4 NLP toolkit → 5 RAG/LLM → 6 web app → 7 evaluation report. Done-criteria for
each are in `docs/SPEC.md`.
