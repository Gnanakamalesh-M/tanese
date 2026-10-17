Tanese is a constructed language inspired by Tamil and Japanese. This document is its
complete specification as of v0.1: the sounds, the spelling, the writing system, the
grammar, and the rules that say what a Tanese word may be.

It is worth being exact about what "inspired by" means here, because it is the claim most
easily overstated. Tanese takes from Tamil a retroflex consonant series, agglutinative
suffixing morphology, and a habit of carving meaning finely where the distinction matters.
It takes from Japanese a mora-based phonology, a strict ban on consonant clusters, verb-final
clause structure, and a productive compounding habit. It takes **no forms at all**: not a
particle, not a case ending, not a root. Every form in this document was coined for Tanese,
and the one place where resemblance is permitted — adapted loanwords, section 5.6 — is
labelled as such and capped by quota.

### How to read this document

Each section states a decision, then why it was made, then what it costs. The last part is
not decoration. A constructed language is a pile of trade-offs, and a specification that
lists only the benefits is not a specification but an advertisement, so every rule here
carries its known problems alongside its justification, in the same `problems` field of the
same YAML file.

Three things this document is not:

- **A teaching grammar.** It is organised by the structure of the language, not by what a
  learner would need first.
- **A record of usage.** Nothing in Tanese has ever been spoken, and no text has been
  written in it beyond the examples here. Section 7 is specific about what that means.
- **Hand-written.** Everything factual below is generated from `spec/*.yaml`, which is the
  actual source of truth. If this document and `spec/` ever disagree, `spec/` is right and
  `python scripts/gen_spec_doc.py --check` fails until the document is rebuilt.

### What exists and what does not

| Layer | Status |
| --- | --- |
| Phonology, romanization, script | specified and implemented (Phase 1A) |
| Grammar: word order, morphology, particles, politeness | specified and implemented (Phase 1B) |
| Vocabulary rules: how a word may be formed | specified and implemented (Phase 1C) |
| **The vocabulary itself** | **does not exist yet** (Phase 2) |
| Corpus, NLP toolkit, evaluation | do not exist yet (Phases 3–7) |

The absence in the middle of that table is the thing to keep in mind while reading. Tanese
has a complete grammar and no words. Every form in the examples below is either a
placeholder invented so that a rule could be demonstrated, or an illustration of a word
*shape*; none is official vocabulary, and a checker enforces that none of them leaks into
the lexicon when Phase 2 builds it. A rule that looks well-supported here has been tested
against other rules, not against use.
