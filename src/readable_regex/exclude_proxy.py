from __future__ import annotations

from typing import TYPE_CHECKING

from readable_regex.components import (
    CharClassType,
    NegatedCharClass,
    Quantifier,
    QuantifierKind,
)

if TYPE_CHECKING:
    from readable_regex.builder import RegexBuilder


class ExcludeProxy:
    """Proxy returned by `regex.exclude` property.

    Provides `.digit`, `.digits`, `.word`, `.words`, etc. that produce
    negated character classes (e.g., `\\D`, `\\W`).
    """

    def __init__(self, builder: RegexBuilder) -> None:
        self._builder = builder

    def _add(self, class_type: CharClassType) -> RegexBuilder:
        return self._builder._extend(NegatedCharClass(class_type))

    def _add_plus(self, class_type: CharClassType) -> RegexBuilder:
        target = NegatedCharClass(class_type)
        return self._builder._extend(Quantifier(target, QuantifierKind.ONE_OR_MORE))

    # Singular (one)
    @property
    def digit(self) -> RegexBuilder:
        return self._add(CharClassType.DIGIT)

    @property
    def word(self) -> RegexBuilder:
        return self._add(CharClassType.WORD)

    @property
    def whitespace(self) -> RegexBuilder:
        return self._add(CharClassType.WHITESPACE)

    @property
    def letter(self) -> RegexBuilder:
        return self._add(CharClassType.LETTER)

    @property
    def any_char(self) -> RegexBuilder:
        return self._add(CharClassType.ANY)

    # Plural (one or more)
    @property
    def digits(self) -> RegexBuilder:
        return self._add_plus(CharClassType.DIGIT)

    @property
    def words(self) -> RegexBuilder:
        return self._add_plus(CharClassType.WORD)

    @property
    def whitespaces(self) -> RegexBuilder:
        return self._add_plus(CharClassType.WHITESPACE)

    @property
    def letters(self) -> RegexBuilder:
        return self._add_plus(CharClassType.LETTER)

    @property
    def any_chars(self) -> RegexBuilder:
        return self._add_plus(CharClassType.ANY)
