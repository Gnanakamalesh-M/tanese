Tanese is SOV and consistently head-final: modifiers precede what they modify, relative and
subordinate clauses precede their heads, and the verb closes the clause. Relations between
arguments are carried by postposition particles rather than by position, so the arguments
themselves may be reordered freely before the verb without changing who did what.

The morphology is agglutinative and suffixing only — no prefixes, no infixes, no stem
changes. A root is invariant, and a fully specified verb is its root plus up to four suffixes
in a fixed order: aspect, tense, mood, politeness. There is no agreement of any kind. The
verb does not vary for person, number or gender; pronouns carry person, plural is an optional
noun suffix, and grammatical gender does not exist. A single verb form therefore serves every
subject, which is the largest single simplification in the language and the one that most
reduces what a learner or a parser has to know.

Politeness is a three-way contrast — casual, neutral, formal — and it is marked **once per
clause**, on the final verb, rather than spread across the sentence as it is in Japanese. The
casual level is the empty slot, which keeps the shortest form the most informal.

Particles are separate words and suffixes are glued on. This is the whole of the word-boundary
definition, it is declared by exactly one rule (`GR-ORD-001`), and every component that needs
to know where a word ends — the tokenizer, the validator, the script converter, the
contradiction checker — reads it from that rule rather than assuming a space. One definition,
one place.

### The known wart

Negation is the mood suffix `-nhi`, which keeps the locked four-slot verb order intact but
means negation cannot co-occur with another mood. The prohibitive and the negative conditional
are therefore two words where their positive counterparts are one, and a negative
desiderative ("does not want to") has no form at all. This is the clearest unresolved problem
in the grammar; section 6 states the condition under which it would be reopened.

### What has been checked

The grammar is held together by twelve mechanical checks (`python scripts/check_grammar.py`),
which prove among other things that no form is claimed for two functions, no function is
claimed by two forms, no rule asserts a slot order that disagrees with the locked one, and
every example is a legal, tokenizable, script-consistent Tanese word sequence. Every one of
those checks is itself tested against a rule set built to break it, so a green run is not
green by accident.

What they do not prove is that the rules are *usable together*. Nothing has been written in
Tanese, so whether these rules compose into a language someone could say anything in is
genuinely unknown. That is what Phase 3 is for.
