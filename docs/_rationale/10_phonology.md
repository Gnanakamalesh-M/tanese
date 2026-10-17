The sound system is the layer every other layer is built on, so it was designed to be small,
unambiguous, and mechanically checkable before anything else existed.

Five vowels with a length contrast, and sixteen consonants including a retroflex series. The
retroflexes are the one feature taken straight from Tamil in character — they are the sound
most Tamil speakers would recognise as familiar and most Japanese speakers as foreign — and
they are what keeps Tanese from sounding simply Japanese, given how much of the syllable
structure is mora-based.

Two consequences of the inventory are worth noticing because they shape everything later:

**There is no /h/.** This is not an omission. The absence of /h/ is what lets the letter `h`
work as a pure retroflex marker, so `th`, `dh` and `nh` are single consonants and no reader
has to wonder whether `tha` is one sound or two. A language with both /h/ and a retroflex
digraph convention would need a third device to tell them apart.

**Six of the sixteen consonants cannot be geminated** — the nasals, the tap and the two
glides. The criterion is phonetic rather than arbitrary: a geminate is a consonant held
across a mora boundary, and these are the consonants a speaker cannot audibly hold without
turning them into something else. It costs the lexicon some word shapes, and it leaves an
asymmetry that has to be taught rather than derived ("why can /t/ double when /n/ cannot?").

Accent is fixed on the first mora and is never contrastive, so it is not written at all. It
is recorded in the spec only so that a future pronunciation guide has one place to read it
from.

The constraint list in 1.4 is the real definition of a legal word, and it is executable:
`tanese_nlp.phonology.validate` returns the id of the constraint a rejected word broke, not
a boolean. That matters for two later phases — Phase 2 has to tell a human *why* a candidate
word was dropped, and Phase 4 has to report it to a learner — so the reason was built in
from the start rather than retrofitted.
