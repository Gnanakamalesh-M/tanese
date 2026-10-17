# Tanese

Tanese is a constructed language inspired by Tamil and Japanese, plus an NLP/LLM toolkit
built around it. It is a student project: the aim is something finishable, internally
consistent, and honestly evaluated — not a complete real-world language ecosystem.

Tamil and Japanese are inspirations only. Tanese has its own phonology, script, grammar,
and vocabulary, and nothing in it is a copy of either source language.

> **Status: Phase 1C (vocabulary rules + specification document) complete.** Tanese now has
> a sound inventory, a canonical spelling, a writing system, a grammar of 54 rules, and 20
> rules saying how a word may be formed — all machine-readable in `spec/` and checked for
> self-contradiction by scripts. The whole language is published as one generated document,
> [the Tanese Language Specification](docs/language-specification.md).
>
> There is still **no vocabulary**. The words in the examples are explicitly-marked
> placeholders and illustrations, not a lexicon, and a check fails if any of them reaches
> `data/vocabulary/`. See [Not verified](#not-verified) below.

## How the project is organised

`spec/*.yaml` is the source of truth for the language. Documentation is derived from it,
never the other way round. Rules define Tanese; the LLM assists but never changes official
rules or vocabulary.

| Path | Contents |
| --- | --- |
| `docs/SPEC.md` | Locked decisions, current phase, per-phase done-criteria |
| `docs/VISION.md` | Long-form context (not built from directly) |
| `docs/CHANGES.md` | Proposed changes to locked decisions |
| `docs/language-specification.md` | **The Tanese Language Specification v0.1** — generated, do not edit |
| `docs/_rationale/` | Hand-written narrative the specification splices in |
| `spec/` | Machine-readable language rules (YAML) |
| `spec/schemas/` | JSON Schemas the rule files are validated against |
| `tanese_nlp/phonology/` | Romanization lexer and phonotactic validator |
| `spec/grammar_rules/` | The grammar: one YAML file per topic, plus two support files |
| `tanese_nlp/script/` | Romanization ↔ script converter |
| `tanese_nlp/grammar/` | Rule loader, tokenizer, contradiction checker |
| `tanese_nlp/vocabulary/` | Vocabulary rule loader, loanword adapter, consistency checker |
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

It runs six steps and stops at the first failure:

1. **lint** — `ruff check .`
2. **tests** — `pytest`
3. **yaml-schema** — `scripts/check_yaml_schema.py`, validating every `spec/*.yaml`
   against `spec/schemas/` and checking that grammar-rule ids are globally unique
4. **grammar** — `scripts/check_grammar.py`, the twelve contradiction checks over
   `spec/grammar_rules/`, which also prints the rule and example counts
5. **vocabulary** — `scripts/check_vocabulary.py`, the thirteen consistency checks over
   `spec/vocabulary_rules.yaml`, which also prints the Phase 1C counts and three
   measurement reports
6. **spec-doc** — `scripts/gen_spec_doc.py --check`, which fails if
   `docs/language-specification.md` has drifted from `spec/`. It writes nothing

Each can also be run on its own, as can the word generator and the document build:

```
python scripts/check_yaml_schema.py
python scripts/check_grammar.py
python scripts/check_vocabulary.py
python scripts/gen_words.py
python scripts/gen_spec_doc.py
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

## The vocabulary rules (Phase 1C)

`spec/vocabulary_rules.yaml` is the source of truth; this section summarises it, and
[the Tanese Language Specification](docs/language-specification.md) is the full generated
document.

Phase 1C says how a Tanese *word* may be formed. It deliberately adds **no vocabulary**:
locked decisions 14–15 reserve official words for the Phase 2 pipeline and a separate file.

**Where words come from.** Five strata, and what separates them is *how a word was coined*,
not how it sounds. A `tamil_inspired` word borrows a Tamil habit — fine semantic
granularity, a separate root where English uses a word plus a modifier — and its form is
coined natively. A `japanese_inspired` word borrows the habit of covering a large meaning
space by compounding a small stock of roots, and its form is coined natively too. Locked
decision 3 forbids a Tanese particle from equalling a common Japanese or Tamil one; Phase 1C
applies the same gate to content words. Only the `loan` stratum borrows a form, and it is
confined to one semantic field with a 0.06 share target.

The honest cost: the two inspired strata are invisible in the words themselves, and the
stratum label is unverifiable from a form. No check can catch a native root mislabelled
`tamil_inspired`.

**Root shapes.** Two to four moras, ending in a vowel or the moraic `n`. The permitted
finals are not a taste decision — every suffix in `spec/grammar_rules/` is consonant-initial,
so those two finals concatenate legally with all fourteen of them and need no morphophonemic
rule at the join, which matters because the phonology declares no morphophonemics at all.
Check 2 proves it by concatenating every permitted final with every declared suffix on every
run, so a vowel-initial suffix added later fails loudly instead of making the rule quietly
wrong.

**Compounds are two words.** `GR-NOUN-004` is already official and lists the fused spelling
as invalid, so Phase 1C specifies compounds as multi-word lexical entries — `sedha nami` is
the entry "restaurant" — and check 3 fails if a pattern declares itself fused or
head-initial. Fusion was reconsidered and not proposed: a seam raises hiatus and sandhi
questions the phonology has no answers to. See `docs/CHANGES.md` CH-003.

**Loanwords** go through a deterministic, table-driven adapter. One input gives exactly one
output, or an explicit rejection naming the sound responsible; the code holds no
sound-specific knowledge at all.

```
film    [f i l m]            -> pilun       f->p, final nasal -> moraic n, stranded l takes u
bank    [b a n k]            -> banku       nasal before a stop becomes the coda, no vowel added
coat    [k o t_retro]        -> kotha       a, not u, after a final retroflex
silk    [p a t_retro t_retro u] -> paththu  a geminable pair stays a geminate
strike  [s t r a i k]        -> suturawiku  epenthesis twice; a+i would give the gap mora `yi`
shop    [sh O p]             -> rejected VL-UNMAPPED on 'sh'
```

Fourteen source sounds are listed as **unmapped** and a word containing one is refused, not
approximated — each has at least two equally defensible substitutes, and picking one silently
would mean a second person adapting the same word by hand would get a different answer. The
intended consequence is that Tanese currently cannot borrow *thing*, *chair* or *shop*.

**Originality** has two gates. The hard gate is locked decision 3's own wording, exact
equality against the 61-form list. On top of it, a root coined from v0.1 onward must be at
least edit distance 2 from any listed form — the real failure mode being a form one segment
from its source, which was not hypothetical: the demo root `wesu` sat one edit from Japanese
*desu* and has since been retired. A normalised-distance floor was tried first and dropped:
measured against the existing spec it fails twelve already-official Phase 1B morphemes,
because a two-letter suffix cannot be relatively far from a two-letter particle. The absolute
gate is declared non-retroactive, and the 19 existing forms it spares are printed in full by
the check script rather than left implied.

## Phase 1C results

Produced by `.venv\Scripts\python.exe scripts\check_vocabulary.py`:

```
== counts
  rules                20
  valid examples       40
  invalid examples     40 (7 deliberately not legal Tanese)
  strata               5
  root shapes          4
  semantic fields      5
  compound patterns    3
  loan substitutions   38 (14 sounds deliberately unmapped)
  loan repair steps    7
  adaptation examples  9 expected outputs, 5 expected rejections
  pipeline stages      6
  forms introduced     12 (3 illustrative roots + adapted loans, all experimental)

== checks
  ok    check 1 root shapes
  ok    check 2 suffix concatenation
  ok    check 3 compounds unfused
  ok    check 4 reserved collisions
  ok    check 5 originality gates
  ok    check 6 loan tables well formed
  ok    check 7 adapter matches spec
  ok    check 8 example closure
  ok    check 9 example legality + script
  ok    check 10 share targets reachable
  ok    check 11 cross-spec references
  ok    check 12 rule shape
  ok    check 13 illustrations are not vocabulary
```

The same script then prints three reports that never cause a failure, because they are
measurements rather than requirements: the distance from every form the file introduces to
its nearest listed source form (lowest 2, highest 7), the 21 existing forms the
non-retroactive originality gate spares, and the one adapted loan that is a legal word but
exceeds the four-mora root cap (`suturawiku`, 5 moras, from *strike* — predicted by the
`problems` field of the epenthesis rule).

What each check proves, and what it does **not**, is in the module docstring of
`tanese_nlp/vocabulary/consistency.py`. Every check is itself tested by breaking the thing it
checks (`tests/unit/test_vocabulary_consistency.py`), so a green run is not green by accident.

Against `docs/SPEC.md`'s Phase 1C done-criteria:

| Criterion | Evidence |
| --- | --- |
| `spec/vocabulary_rules.yaml` covering native roots, Tamil-inspired, Japanese-inspired, loanword adaptation, compounds | the file exists and passes `scripts\check_yaml_schema.py` against a new `vocabulary_rules.schema.json`; all five strata are declared, asserted by `tests/unit/test_vocabulary_rules.py` |
| `docs/language-specification.md` generated from YAML + human-written rationale | 1418 lines, generated by `scripts\gen_spec_doc.py` from `spec/*.yaml` plus seven hand-written files in `docs/_rationale/`; `scripts\gen_spec_doc.py --check` fails if it drifts, and `run_checks.py` runs that check |
| Internal consistency check passes | the thirteen checks above, including two cross-file ones: check 2 against `spec/grammar_rules/` and check 11 against `spec/phonology.yaml` |
| Unresolved decisions listed | section 6 of the specification: five of them (U-1 to U-5), each with its trigger and its cost, and U-1 names `docs/CHANGES.md` CH-002. A sixth was closed after Phase 1C — see `docs/CHANGES.md` CH-004 — and is recorded under "Closed since v0.1" |

`pytest` reports **2481 passed** (`.venv\Scripts\python.exe -m pytest`), up from 1909 after
Phase 1B. The growth is parametrised: each of the 80 examples is checked for its declared
legality and, if legal, for its script form and its round-trip; and each of the 38 loan
substitutions, 14 unmapped sounds, 9 worked examples and 5 required rejections gets its own
test, so a failure names the rule that broke rather than only the word.

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
- **CI on the Phase 1A, 1B and 1C commits.** All numbers above are from local runs on
  Python 3.11.9. Phase 0's CI run #1 was green on commit `5f47648`; nothing since has been
  pushed.
- **Invalid examples are author-asserted.** The 108 grammar and 40 vocabulary invalid
  examples are labelled ungrammatical or ill-formed by me, with a reason each. Nothing
  *proves* they are: the rule-based grammar checker that could reject them is Phase 4. What
  the checks do prove is that each is either a legal Tanese word sequence — spelled
  consistently with the script, tokenizable, and not claimed valid by any other rule — or,
  for the 7 marked `phonotactics: illegal`, genuinely rejected by the validator. Until
  Phase 4 runs over them, "invalid" means "I say so, with a reason".
- **Contradictions that live only in prose.** Checks 5 and 6 compare example strings. Two
  rules whose `description` or `reason` disagree, while their examples do not overlap, will
  pass. Only the declared forms, slots, slot order and `asserts` keys are compared
  semantically; the prose is not.
- **The originality list is not exhaustive.** `_originality.yaml` holds the 61 Japanese and
  Tamil forms I could enumerate by hand, with a source and gloss each. A Tanese form that
  passes check 9 is *not* thereby proven absent from Japanese or Tamil, let alone from any
  third language — the check proves only that no listed form was reused, and the Phase 1C
  distance gate only that none was closely approached. The `unspellable` flags in that file
  are verified against the phonotactic validator; the list's coverage is not verified at all.
- **The originality gate is not retroactive.** 19 existing forms sit one edit from a listed
  source form, printed in full by `scripts\check_vocabulary.py`. Eighteen are Phase 1B
  particles and suffixes, where the measure means little — a two-letter suffix cannot be far
  from a two-letter particle. The nineteenth is the demo pronoun root `ano`. The two cases
  that were a real problem rather than an artefact of the measure, the demo copula `esu` and
  `wesu` "see", were retired rather than spared (`docs/CHANGES.md` CH-004); at distance 1 the
  gate now rejects either spelling outright, so no list is needed to keep them out.
- **The grammar has not been used.** No corpus, no conversation and no translation has been
  written in Tanese, so whether these 54 rules are usable together — rather than merely
  non-contradictory — is unknown. That is what Phase 3 is for. Three gaps are already known
  and recorded in the rules' own `problems` fields: a topicalised argument loses its
  relation (GR-PART-009), an embedded yes/no question has no form (GR-Q-004), and a
  negative desiderative has no form (GR-TAM-005).
- **The vocabulary rules have produced no vocabulary.** 20 rules say how a word may be
  formed, and not one official word has been formed. Whether the root shapes, strata and
  compound patterns actually yield 300 usable words — and whether the share quotas are
  reachable in practice rather than merely arithmetically — is what Phase 2 will find out.
- **Stratum and semantic-field labels are unverifiable.** Four of the five strata borrow
  structure rather than form, so nothing in a word reveals which habit coined it. No check
  can catch a native root recorded as `tamil_inspired`, or a loan filed outside the one
  field loans are confined to. Those classifications are honest metadata, not results.
- **The loan adapter has seen fourteen inputs.** Nine expected outputs and five expected
  rejections, all hand-derived from the repair steps and written into
  `spec/vocabulary_rules.yaml` so the tests cannot simply confirm whatever the code does.
  That pins down each repair; it is not a real loanword list, and the adapter has never been
  run over one. One known consequence is unresolved: `strike` adapts to `suturawiku`, five
  moras, which is a legal word but over the four-mora root cap (U-3).
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
- Everything from Phase 2 onward: the vocabulary itself, the collision detector, the corpus,
  the tokenizer, the morphological analyzer, the grammar checker, embeddings, RAG,
  translation, the web app, and all evaluation numbers. None of it exists yet.

## Evaluation and honesty notes

When results do arrive, they will follow the project's standing rules:

- every number in this README names the command that produced it;
- every method is compared against a fair baseline (plain rules, keyword search, no-RAG),
  reported even when the fancier method loses;
- translation metrics such as BLEU and chrF are **self-referential** for Tanese, because the
  language has no native speakers and the reference translations are produced by the same
  rule set being evaluated. They measure internal consistency, not translation quality.

## Roadmap

Phase 0 skeleton → 1A phonology/script → 1B grammar core → 1C vocabulary rules + spec document → 2 lexicon →
3 corpus → 4 NLP toolkit → 5 RAG/LLM → 6 web app → 7 evaluation report. Done-criteria for
each are in `docs/SPEC.md`.
