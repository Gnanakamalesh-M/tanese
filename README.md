# Tanese

Tanese is a constructed language inspired by Tamil and Japanese, plus an NLP/LLM toolkit
built around it. It is a student project: the aim is something finishable, internally
consistent, and honestly evaluated — not a complete real-world language ecosystem.

Tamil and Japanese are inspirations only. Tanese has its own phonology, script, grammar,
and vocabulary, and nothing in it is a copy of either source language.

> **Status: Phase 0 (skeleton + CI) complete.** No language content exists yet — no
> phonology, no grammar rules, no vocabulary. See [Not verified](#not-verified) below.

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

The schema check can also be run on its own:

```
python scripts/check_yaml_schema.py
```

Both scripts work from any working directory.

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

## Not verified

Honest list of things written but not actually demonstrated:

- **CI green on a pushed commit.** The workflow in `.github/workflows/ci.yml` exists and runs
  the same `python scripts/run_checks.py` command that passes locally, but this repository
  has **no git remote** and nothing has been pushed, so no CI run has ever executed. The
  workflow itself — GitHub-side caching, `setup-python`, and install from `requirements.txt`
  on a clean Ubuntu runner — is therefore unverified.
- **Installing from `requirements.txt` into a fresh environment.** The pins were read back
  from the existing `.venv` after installation; a clean `pip install -r requirements.txt` has
  not been run.
- Everything from Phase 1A onward: phonology, script, romanization, grammar rules,
  vocabulary, corpus, tokenizer, morphological analyzer, grammar checker, embeddings, RAG,
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

Phase 0 skeleton → 1A phonology/script → 1B grammar core → 1C spec document → 2 lexicon →
3 corpus → 4 NLP toolkit → 5 RAG/LLM → 6 web app → 7 evaluation report. Done-criteria for
each are in `docs/SPEC.md`.
