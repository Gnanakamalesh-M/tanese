# Change proposals
Any change to a LOCKED decision or official rule goes here first: what, why, alternatives, impact. Wait for approval.

---

## CH-001 — Grammar rule format: add machine-readable fields (Phase 1B)

**Status: applied with approval, 2026-10-16. No LOCKED decision changed.**

**What.** `docs/SPEC.md` documents the grammar rule format. Phase 1B adds these fields to
`spec/schemas/grammar_rule.schema.json`:

| Field | Required? | Purpose |
| --- | --- | --- |
| `morphemes` | required for `particle`, `pronoun`, `politeness`; a `morphology` rule must have this **or** `slot_order` | declares each form with its slot, function and kind, so forms can be compared mechanically |
| `slot_order` | optional | the verb suffix slot order a rule asserts |
| `word_boundary` | optional, declared by exactly one rule (GR-ORD-001) | what counts as one word: the single definition used by the tokenizer, the validator calls and the script conversion |
| `asserts` | optional | `requires` / `forbids` feature keys, so two rules can be checked for opposing claims |
| `alternatives`, `problems` | optional | designs rejected, and known costs — already the convention in `spec/phonology.yaml` |
| `gloss` on an example | optional | morpheme-by-morpheme gloss |

`category` was also closed to an enum (`word_order`, `syntax`, `morphology`, `particle`,
`pronoun`, `politeness`, `discourse`). Without that, a typo'd category would silently skip
the conditional `morphemes` requirement.

**Why.** The Phase 1B done-criterion is "no two rules contradict (checked by a script)". A
rule format of prose plus examples gives a script nothing to compare: it can only match
example strings, which catches a direct clash and nothing else. With the fields above, the
checker in `tanese_nlp/grammar/contradictions.py` detects a form claimed for two functions,
two forms claimed for one function, a slot order that disagrees with LOCKED decision 6, a
suffix in a slot that does not exist, and a feature required by one rule and forbidden by
another — none of which is visible in prose.

**Alternatives considered.** Keep the format exactly as documented and write a prose-only
checker. Rejected: it would have reduced the contradiction check to string comparison of
examples, and the done-criterion would have been met in letter only.

**Impact.** Additive. Every field in the original format is still required, so a rule
written to the SPEC.md format still validates — except that `category` must now be one of
the seven listed names. The only file that changed outside Phase 1B's own additions is
`tests/unit/test_speccheck.py`, whose fixture used `category: test`.

**What is NOT changed.** No LOCKED decision. In particular decision 6 (the verb slot order)
stands as written, which is why negation shares the mood slot and prohibition and negative
conditionals are analytic — see CH-002 below for the consequence that may need revisiting.

---

## CH-002 — Possible future proposal: a dedicated negation slot

**Status: not proposed. Recorded so Phase 3 has somewhere to point.**

Negation is the mood suffix `-nhi` (GR-NEG-001), which keeps LOCKED decision 6 intact but
means negation cannot co-occur with any other mood. Two of the three casualties are rescued
analytically — the prohibitive (`mandukenhi thon`, GR-NEG-003) and the negative conditional
(`ikkedhonhi lun`, GR-NEG-004) — and the third, a negative desiderative ("does not want
to"), is simply not expressible in v0.1.

If Phase 3 corpus work shows the analytic forms are unusable in practice, the change to
propose here is a negation slot between root and aspect:

    ROOT - NEG - ASPECT - TENSE - MOOD - POLITENESS

That would amend LOCKED decision 6, which decision 6 itself says is reviewable in Phase 1B
"if a concrete problem is found". The problem above is concrete but not yet demonstrated to
be fatal, so nothing is proposed now. Cost if it is: a fully specified verb would reach six
suffixes, and every rule and example mentioning the analytic forms would be rewritten.

---

## CH-003 — Vocabulary rule file format, and two consequences of GR-NOUN-004 (Phase 1C)

**Status: applied with approval, 2026-10-17. No LOCKED decision changed.**

**What.** Phase 1C adds `spec/vocabulary_rules.yaml` and
`spec/schemas/vocabulary_rules.schema.json`. The file is a hybrid: machine tables
(`strata`, `root_shapes`, `originality`, `semantic_fields`, `compound_patterns`,
`loan_substitutions`, `unmapped`, `loan_repairs`, `adaptation_examples`,
`adaptation_rejections`, `pipeline`, `illustrative_forms`) plus a `rules:` list of `VR-*`
entries in the Phase 1B grammar-rule format. Three differences from that format are worth
recording:

| Difference | Why |
| --- | --- |
| `category` is a different closed enum (`stratum`, `root_shape`, `originality`, `compound`, `loan`, `semantics`, `pipeline`) | These rules are about word formation, so the grammar categories do not apply. Closed to an enum for the CH-001 reason: a typo'd category must not silently skip a conditional check. |
| An example may carry `phonotactics: illegal` and then has **no** `tanese` field | Several of these rules are about legality itself, so their invalid examples are deliberately not legal Tanese words. An illegal word has no script form — the converter refuses to produce one — so requiring the field would force a hand-typed fiction. Check 9 asserts the declared legality in both directions: a `legal` example must pass the validator and round-trip, an `illegal` one must actually be rejected. |
| An example may contain a form that is not a demo root | The grammar's lexicon closure (check 9 there) requires every valid example to be built from `_example_lexicon.yaml`. A vocabulary rule has to be able to show an adapted loanword and an illustrative root shape, neither of which is a demo word. Those forms are declared in `illustrative_forms` and `adaptation_examples` and are closed over by check 8, so an example still cannot introduce a word in passing. |

**Why a new schema rather than reusing `grammar_rule.schema.json`.** The machine tables are
the part Phase 2 executes: the loanword adapter contains no sound-specific knowledge at all
and is driven entirely by `loan_substitutions`, `unmapped` and `loan_repairs`. A rule list
of prose plus examples could not drive anything.

**Alternatives considered.** A flat list of `VR-*` rules with no tables, which was the
simpler option and was rejected because the loan substitution table would have had to live
in `description` prose, where no code can read it. Also considered: a pure sectioned config
with no rule entries, rejected because it loses the two-valid-plus-two-invalid discipline
that makes the Phase 1B rules checkable.

**Impact.** Additive. One line in `SCHEMA_MAP` in `tanese_nlp/speccheck.py`, two new steps
in `scripts/run_checks.py` (`vocabulary`, `spec-doc`), and the expected step list in
`tests/unit/test_run_checks.py` extended from four names to six. Nothing in `spec/` outside
the new file changed; nothing in `spec/grammar_rules/` was touched at all.

**What is NOT changed, and nearly was.**

1. **`GR-NOUN-004` (noun-noun compounding) stands exactly as written.** It declares that a
   compound is two separate words with no fusion, and lists the fused spelling `kalunami`
   as an invalid example. Phase 1C had an obvious motive to reopen it — fused compounds are
   shorter and look more like a natural language, and the loanword repair machinery now has
   a glide rule that could serve as the seam rule fusion would need. It was not reopened,
   because the original reason is still the better one: fusion creates a seam, and
   `spec/phonology.yaml` deliberately declares no allophony and no morphophonemics, so there
   is no machinery to govern a join. Compounds are therefore specified as **multi-word
   lexical entries**, and check 3 fails if any compound pattern declares itself fused or
   head-initial.

2. **No derivational morphology was added.** v0.1 has no way to derive an agent noun from a
   verb or a modifier from a noun. A derivational suffix would be a new morpheme needing a
   slot that does not exist in the noun or verb morphology, which would put it straight into
   the Phase 1B contradiction checker's jurisdiction. Adding morphology to solve a lexicon
   problem that has not yet been observed is over-engineering; it is recorded as unresolved
   decision U-4 in the specification instead, with Phase 2 as the trigger.

**One measurement that changed a plan.** The original Phase 1C plan proposed a *normalised*
edit-distance floor of 0.5 against `_originality.yaml` as the originality gate for new roots.
Measuring it against the existing spec before implementing it showed that it fails twelve
already-official Phase 1B morphemes (`ban`, `le`, `lun`, `nen`, `nhe`, `nhi`, `sen`, `sun`,
`the`, `thin`, `thon`, `kodhu`), purely because a two-letter morpheme cannot be relatively
far from a two-letter particle. A gate that condemns the existing official spec is measuring
the wrong thing, so the implemented gate is instead:

- the **hard gate** of LOCKED decision 3 — exact equality — applied to roots as Phase 1B
  already applies it to morphemes; plus
- an **absolute** Levenshtein floor of 2 on roots coined from v0.1 onward, declared
  non-retroactive, with the 21 existing forms it spares printed in full by
  `scripts/check_vocabulary.py` so the exemption is visible rather than implied.

This is a decision about a new Phase 1C gate, not a change to LOCKED decision 3, which is
still enforced exactly as worded.

---

## CH-004 — Two demo roots retired for originality (follow-up to Phase 1C, U-5)

**Status: applied with approval, 2026-10-17. No LOCKED decision changed, and no official
rule or official vocabulary changed.**

**What.** Two roots in `spec/grammar_rules/_example_lexicon.yaml` were replaced:

| Retired | Replacement | Class | Distance to the nearest listed source form |
| --- | --- | --- | --- |
| `esu` | `nutu` | copula ("be") | was 1 (Japanese *desu*), now 3 |
| `wesu` | `bitu` | verb ("see") | was 1 (Japanese *desu*), now 3 |

Every grammar example that used them was rewritten — 8 rule files, 49 lines — including the
`tanese` script field of each affected example, which was regenerated from the romanization
by `tanese_nlp.script.convert` rather than retyped.

**Why.** `esu` was the worst originality case in the project: one edit from Japanese *desu*
**and** carrying the same grammatical function, which is the combination no reader would
accept as independent coinage. `wesu` was one edit from the same form. Both passed the hard
gate of LOCKED decision 3, because that gate is exact equality; both would have failed the
Phase 1C new-root gate (absolute edit distance 2, `VR-ORIG-002`), and were spared only
because that gate is declared non-retroactive. Phase 1C recorded them as unresolved decision
U-5 and recommended retirement; this applies it.

**Alternatives considered.** Leave them and add `esu`/`wesu` to a list of forms Phase 2 may
not re-derive. Rejected as redundant machinery: at distance 1 from *desu*, `VR-ORIG-002`
already rejects either spelling outright, so a Phase 2 candidate spelled `esu` or `wesu`
fails the gate with nothing further written down. A list would have been a second, weaker
statement of a rule that already exists.

**How the replacements were chosen.** Generated and filtered mechanically against every gate
rather than picked by ear: legal under `spec/phonology.yaml`, two moras, ending in a
permitted final, not equal to any declared particle, suffix, pronoun or demo root, not
ending in any declared suffix form, legal in combination with all fourteen suffixes, at
edit distance 3 or more from every spellable entry of `_originality.yaml`, and at edit
distance 3 or more from every existing demo root. The surviving pool was then narrowed to
forms using only single-letter consonants, on the grounds that a copula is the most frequent
verb in the language and should not be the heaviest word in it.

**Impact.** `spec/grammar_rules/` only, plus the prose that described these two forms as
standing exceptions: the `problems` and `new_root_gate_reason` fields of
`spec/vocabulary_rules.yaml`, the `docs/_rationale/` files behind sections 6 and 7 of the
specification, and the README. The demo wordlist still holds 41 words, and the specification
was regenerated.

U-5 is closed. The former U-6 (whether the stratum share targets are right) is renumbered
U-5, and the closed item is recorded under "Closed since v0.1" in section 6 of the
specification rather than deleted, so the reasoning stays on the record.

**What is NOT changed.** No LOCKED decision. No official rule: the demo wordlist is
`status: experimental` throughout and the schema permits no other value there, so this
changes illustrations, not the language. `VR-ORIG-002` keeps its `wesu` invalid example,
which is now the form that motivated the gate rather than a form the gate spares. 19 forms
remain spared by non-retroactivity — eighteen Phase 1B morphemes, where distance 1 from a
two-letter particle means little, and the demo pronoun root `ano` — and
`scripts/check_vocabulary.py` still prints all of them.
