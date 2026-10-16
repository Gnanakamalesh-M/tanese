# Tanese

Tanese is a constructed language inspired by Tamil and Japanese, plus an NLP/LLM toolkit
built around it. It is a student project: the aim is something finishable, internally
consistent, and honestly evaluated — not a complete real-world language ecosystem.

Tamil and Japanese are inspirations only. Tanese has its own phonology, script, grammar,
and vocabulary, and nothing in it is a copy of either source language.

> **Status: Phase 1A (phonology, romanization, script) complete.** Tanese now has a sound
> inventory, a canonical spelling and a writing system, all machine-readable in `spec/`.
> There is still no grammar and no vocabulary. See [Not verified](#not-verified) below.

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
| `tanese_nlp/script/` | Romanization ↔ script converter |
| `tanese_nlp/` | Python toolkit (tokenizer, morphology, grammar, embeddings, …) |
| `data/` | Vocabulary, grammar, translation, conversation, evaluation data |
| `llm/` | Prompts, RAG, fine-tuning, LLM evaluation |
| `backend/`, `frontend/` | Web app (Phase 6) |
| `scripts/` | Plain-python entry points; no `make` |
| `tests/` | Unit and integration tests |

Most of these directories are currently empty placeholders for later phases.

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

It runs three steps and stops at the first failure:

1. **lint** — `ruff check .`
2. **tests** — `pytest`
3. **yaml-schema** — `scripts/check_yaml_schema.py`, validating every `spec/*.yaml`
   against `spec/schemas/` and checking that grammar-rule ids are globally unique

The schema check can also be run on its own, as can the word generator:

```
python scripts/check_yaml_schema.py
python scripts/gen_words.py
```

Both scripts work from any working directory.

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
- **CI on the Phase 1A commit.** The numbers above are from a local run on Python 3.11.9.
  Phase 0's CI run #1 was green on commit `5f47648`; Phase 1A has not been pushed.
- **The glyph shapes.** `spec/script.yaml` describes each atom's shape in prose and reserves a
  PUA codepoint per mora, but nothing has been rendered — there is no SVG, no font and no
  image anywhere in the repo. Whether the 86 glyphs are actually legible, and in particular
  whether the three retroflexes are distinguishable from their alveolar counterparts, is
  unknown. Rendering is Phase 6.
- **Pronounceability.** The phonology is argued from general phonetics (which consonants can
  be audibly held, which contrasts a speaker could learn), not tested with speakers. No one
  has spoken Tanese.
- Everything from Phase 1B onward: grammar rules, vocabulary, corpus, tokenizer,
  morphological analyzer, grammar checker, embeddings, RAG, translation, the web app, and all
  evaluation numbers. None of it exists yet.

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
