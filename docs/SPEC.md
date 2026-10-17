# Tanese - Working Spec (Phase-controlled)

Read docs/VISION.md for context only. Work ONLY on the current phase below.

**CURRENT PHASE: 2 (lexicon)**

## LOCKED decisions (do not change without docs/CHANGES.md + approval)
1. Word order: SOV, head-final (modifier before head).
2. Morphology: agglutinative, suffixing only. No prefixes, no infixes.
3. Case/relations: postposition particles after the noun. Particle forms must be original (must NOT equal common Japanese or Tamil particles/case endings).
4. No verb agreement for person/number/gender. Pronouns carry person. Plural is an optional noun suffix.
5. No grammatical gender.
6. Verb suffix order: ROOT - ASPECT - TENSE - MOOD - POLITENESS. (Reviewable in Phase 1B if a concrete problem is found.)
7. Tense: two-way (past / non-past). Future is expressed by non-past + adverb or a mood suffix.
8. Politeness: exactly 3 levels: casual, neutral, formal. Marked only on the verb/copula final suffix, not on every word.
9. Phonology size: 5 vowels (a i u e o) with a length contrast, about 15-18 consonants, including one retroflex series (Tamil-inspired).
10. Syllable structure: mora-based, (C)V(N). Geminate consonants allowed. No other clusters. Word-final: vowel or n only.
11. Accent: fixed on the first mora, not contrastive (no lexical pitch accent in v0.1).
12. Internal representation: ASCII-safe romanization is the canonical text form. The Tanese script is a mapping layer on top (romanization <-> script), never the other way round.
13. Script: original abugida/syllabary-style design with a glyph table (one id per mora). Stored in spec/script.yaml. Custom font and Unicode proposal are OUT OF SCOPE (use SVG/PUA mapping only if needed for the demo).
14. Vocabulary: all words come from the deterministic pipeline (phonotactic check -> morphology check -> collision check -> rank -> human approve). LLM may only propose candidates.
15. Official vs experimental vocabulary live in separate files.

## OUT OF SCOPE (v0.1)
Speech STT/TTS, mobile app, Unicode standardization, language evolution sim, learning platform, foundation-model training, public API hardening.

## Rule file format (spec/grammar_rules/*.yaml)
Every grammar rule is one YAML entry:
```yaml
- id: GR-PART-003
  category: particle
  name: object marker
  description: ...
  reason: why this design / alternatives considered
  inspiration: {source: tamil|japanese|none, original_feature: ..., how_modified: ...}
  pattern: "NP + <particle>"
  valid:   [{tanese: "...", roman: "...", english: "..."}]
  invalid: [{tanese: "...", roman: "...", why: "..."}]
  status: official | experimental
  since: v0.1
```
Rules: at least 2 valid and 2 invalid examples per rule. IDs are unique and stable. Romanization must pass the phonotactic validator.

## Phases and done-criteria

### Phase 0 - Skeleton + CI
- Folder structure, .gitignore, .env.example, CLAUDE.md, README with "Not verified" section.
- scripts/run_checks.py runs lint + unit tests + YAML schema check (plain python).
- CI uses Python 3.11 and is green on a pushed commit (check the run number/commit).
- Done when: run_checks.py passes locally on 3.11 and CI is green for the latest commit.

### Phase 1A - Phonology + romanization + script
- spec/phonology.yaml, spec/script.yaml, spec/romanization.yaml
- Python: phonotactic validator (is this string a legal Tanese word?) + romanization <-> script converter
- Done when: round-trip test (roman -> script -> roman) passes on 200 generated legal words; validator accepts 30 legal and rejects 30 illegal words (listed in tests).

### Phase 1B - Grammar core
- spec/grammar_rules/*.yaml: word order, noun morphology, verb morphology, TAM, negation, questions, commands, pronouns, particles, politeness
- Done when: >= 40 rules, each with >= 2 valid + 2 invalid examples; schema check passes; no two rules contradict (checked by script).

### Phase 1C - Vocabulary rules + spec document
- spec/vocabulary_rules.yaml (native roots, Tamil-inspired, Japanese-inspired, loanword adaptation, compounds)
- docs/language-specification.md generated from YAML + human-written rationale
- Done when: Tanese Language Specification v0.1 exists, internal consistency check passes, unresolved decisions listed.

### Phase 2 - Lexicon
- Collision detector (exact, phonetic, orthographic, semantic) + candidate ranking + dictionary of ~300 words (data/vocabulary/official.yaml)
- Done when: 300 words pass all validators; collision detector scored on planted collisions (precision/recall); experimental/official separated.

### Phase 3 - Corpus
- Valid sentences, planted-invalid sentences (labelled by error type), translation pairs, small conversations
- Done when: >= 300 valid + 300 invalid labelled sentences, >= 150 translation pairs per source language; every sentence passes/fails the validator as labelled; documented data format.

### Phase 4 - NLP toolkit
- Tokenizer, morphological analyzer, rule-based grammar checker, embeddings similarity
- Done when: grammar checker scored (precision/recall/F1) on the held-out invalid set; baseline = naive heuristic; results in docs/RESULTS.md with commands.

### Phase 5 - RAG + LLM
- RAG over spec + dictionary, translation/correction/explanation prompts. LoRA only if justified.
- Done when: Recall@K + MRR for retrieval vs keyword baseline; hallucination/rule-violation rate with RAG vs no-RAG, judged by the rule-based validator.

### Phase 6 - Web app
- Simple UI: translator, dictionary, grammar checker, script converter, assistant.
- Done when: runs locally with one documented command; screenshots in README.

### Phase 7 - Evaluation report
- docs/EVALUATION.md: metrics, tables, error analysis, limitations, honest conclusions.
