"""Tanese script: romanization <-> glyph mapping (locked decision 12, one id per mora)."""

from tanese_nlp.script.convert import (
    ID_SEPARATOR,
    pua_to_roman,
    roman_to_pua,
    roman_to_script,
    script_to_roman,
)

__all__ = [
    "ID_SEPARATOR",
    "pua_to_roman",
    "roman_to_pua",
    "roman_to_script",
    "script_to_roman",
]
