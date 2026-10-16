"""The three spec files must agree with each other.

Phase 1B onwards will edit spec/phonology.yaml (adding a phoneme, closing a gap). Every
assertion here is a set comparison derived from the files themselves, with no hardcoded
counts, so such an edit either stays consistent or fails loudly here -- which is the point:
silent drift between the phonology, its spelling and its glyphs would be invisible otherwise.
"""

from __future__ import annotations

from tanese_nlp.phonology import spec_load as S


def test_romanization_covers_exactly_the_phonology():
    """Every phoneme is spellable and every grapheme spells something."""
    roman = S.romanization()
    vowel_graphemes = {entry["phoneme"] for entry in roman["vowel_graphemes"]}
    consonant_graphemes = {entry["phoneme"] for entry in roman["consonant_graphemes"]}

    assert vowel_graphemes == set(S.vowels())
    assert consonant_graphemes == set(S.consonants())


def test_every_grapheme_is_built_from_alphabet_letters():
    """The alphabet is what the lexer validates against, so nothing may fall outside it."""
    roman = S.romanization()
    for entry in roman["vowel_graphemes"] + roman["consonant_graphemes"]:
        assert set(entry["grapheme"]) <= S.letters(), entry


def test_the_retroflex_marker_is_not_a_phoneme():
    """The whole `h`-digraph scheme is only unambiguous because /h/ does not exist."""
    marker = S.romanization()["retroflex_digraphs"]["marker"]
    assert marker in S.letters()
    assert marker not in S.consonants()
    assert marker not in S.vowels()


def test_declared_retroflex_digraphs_are_the_retroflex_consonants():
    declared = set(S.romanization()["retroflex_digraphs"]["pairs"])
    actual = {key for key, entry in S.consonants().items() if entry["place"] == "retroflex"}
    assert declared == actual


def test_unassigned_digraphs_are_really_unassigned():
    for spelling in S.romanization()["retroflex_digraphs"]["unassigned"]:
        assert spelling not in S.consonants()


def test_script_table_is_exactly_the_legal_mora_set():
    """Locked decision 13: one id per mora. Set equality, not a count."""
    assert set(S.script_glyphs()) == set(S.legal_mora_ids())


def test_script_mora_spellings_parse_back_to_their_own_id():
    """Each syllabic glyph's `mora` field must be the spelling of that very mora."""
    for glyph, entry in S.script_glyphs().items():
        if entry["kind"] != "syllabic":
            assert entry["mora"] is None, glyph
            continue
        onset, vowel = S.split_mora_spelling(entry["mora"])
        assert S.glyph_id(onset, vowel) == glyph


def test_gaps_are_absent_from_the_script_table():
    for onset, vowel in S.gaps():
        assert S.glyph_id(onset, vowel) not in S.script_glyphs()


def test_every_base_corresponds_to_an_onset_or_the_carrier():
    bases = S.script()["bases"]
    onsets = {entry["onset"] for entry in bases}
    assert onsets == {None} | set(S.consonants())
    assert len({entry["id"] for entry in bases}) == len(bases)


def test_every_composition_refers_to_a_declared_atom():
    document = S.script()
    atoms = {entry["id"] for group in document["atoms"].values() for entry in group}
    bases = {entry["id"] for entry in document["bases"]}

    for entry in document["bases"]:
        assert set(entry["composition"]) <= atoms, entry["id"]
    for entry in document["moras"]:
        assert set(entry["composition"]) <= atoms | bases, entry["id"]


def test_bases_are_featurally_distinct():
    """The featural claim in spec/script.yaml: no two onsets share a frame+manner pair."""
    recipes = [tuple(entry["composition"]) for entry in S.script()["bases"]]
    assert len(set(recipes)) == len(recipes)


def test_pua_codepoints_are_unique_and_in_the_private_use_area():
    pua = S.pua_by_id()
    assert set(pua) == set(S.legal_mora_ids())
    assert len(set(pua.values())) == len(pua)
    for char in pua.values():
        assert 0xE000 <= ord(char) <= 0xF8FF, hex(ord(char))


def test_geminable_consonants_are_a_strict_subset():
    """If everything were geminable the `nn` spelling would be ambiguous again."""
    assert S.geminable()
    assert S.geminable() < set(S.consonants())
    # Specifically: no nasal may geminate, which is what makes `nn` unambiguous.
    nasals = {key for key, entry in S.consonants().items() if entry["manner"] == "nasal"}
    assert nasals
    assert not nasals & S.geminable()


def test_constraint_ids_are_unique():
    constraints = S.phonology()["constraints"]
    assert len({entry["id"] for entry in constraints}) == len(constraints)


def test_every_declared_gap_is_a_well_formed_mora_spelling():
    """A gap must name a mora that would otherwise have been legal, not a typo."""
    for onset, vowel in S.gaps():
        assert vowel in S.vowels()
        assert onset is None or onset in S.consonants()
