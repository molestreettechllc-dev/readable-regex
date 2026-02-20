from __future__ import annotations

import re
from typing import Sequence

from readable_regex.compiler import compile_components
from readable_regex.components import (
    Anchor,
    AnchorType,
    AnyOf,
    CharClass,
    CharClassType,
    Component,
    ExcludeFilter,
    Group,
    Literal,
    Quantifier,
    QuantifierKind,
)
from readable_regex.exclude_proxy import ExcludeProxy
from readable_regex.flags import Flag, flags_to_re


class RegexBuilder:
    def __init__(
        self,
        components: tuple[Component, ...] = (),
        flags: frozenset[Flag] = frozenset(),
    ) -> None:
        self._components = components
        self._flags = flags
        self._compiled: re.Pattern[str] | None = None

    def _extend(self, *new_components: Component) -> RegexBuilder:
        return RegexBuilder(self._components + new_components, self._flags)

    def _with_flag(self, flag: Flag) -> RegexBuilder:
        return RegexBuilder(self._components, self._flags | {flag})

    def _quantify_last(self, kind: QuantifierKind, **kwargs: int | None) -> RegexBuilder:
        if not self._components:
            raise ValueError("No component to quantify")
        last = self._components[-1]
        quantified = Quantifier(last, kind, **kwargs)
        return RegexBuilder(self._components[:-1] + (quantified,), self._flags)

    # ── Anchors & Literals ──────────────────────────────────────────

    def starts_with(self, text: str | None = None) -> RegexBuilder:
        parts: list[Component] = [Anchor(AnchorType.START)]
        if text is not None:
            parts.append(Literal(text))
        return self._extend(*parts)

    def ends_with(self, text: str | None = None) -> RegexBuilder:
        parts: list[Component] = []
        if text is not None:
            parts.append(Literal(text))
        parts.append(Anchor(AnchorType.END))
        return self._extend(*parts)

    def then(self, text: str) -> RegexBuilder:
        return self._extend(Literal(text))

    # ── Character Classes (singular = one) ──────────────────────────

    @property
    def digit(self) -> RegexBuilder:
        return self._extend(CharClass(CharClassType.DIGIT))

    @property
    def word(self) -> RegexBuilder:
        return self._extend(CharClass(CharClassType.WORD))

    @property
    def whitespace(self) -> RegexBuilder:
        return self._extend(CharClass(CharClassType.WHITESPACE))

    @property
    def any_char(self) -> RegexBuilder:
        return self._extend(CharClass(CharClassType.ANY))

    @property
    def letter(self) -> RegexBuilder:
        return self._extend(CharClass(CharClassType.LETTER))

    # ── Character Classes (plural = one or more) ────────────────────

    @property
    def digits(self) -> RegexBuilder:
        cc = CharClass(CharClassType.DIGIT)
        return self._extend(Quantifier(cc, QuantifierKind.ONE_OR_MORE))

    @property
    def words(self) -> RegexBuilder:
        cc = CharClass(CharClassType.WORD)
        return self._extend(Quantifier(cc, QuantifierKind.ONE_OR_MORE))

    @property
    def whitespaces(self) -> RegexBuilder:
        cc = CharClass(CharClassType.WHITESPACE)
        return self._extend(Quantifier(cc, QuantifierKind.ONE_OR_MORE))

    @property
    def any_chars(self) -> RegexBuilder:
        cc = CharClass(CharClassType.ANY)
        return self._extend(Quantifier(cc, QuantifierKind.ONE_OR_MORE))

    @property
    def letters(self) -> RegexBuilder:
        cc = CharClass(CharClassType.LETTER)
        return self._extend(Quantifier(cc, QuantifierKind.ONE_OR_MORE))

    # ── Combinators ─────────────────────────────────────────────────

    def any_of(self, *options: str) -> RegexBuilder:
        return self._extend(AnyOf(options))

    def capture(self, content: RegexBuilder) -> RegexBuilder:
        return self._extend(Group(content._components))

    # ── Quantifiers (modify last component) ─────────────────────────

    def exactly(self, n: int) -> RegexBuilder:
        return self._quantify_last(QuantifierKind.EXACT, count=n)

    def between(self, min_n: int, max_n: int) -> RegexBuilder:
        return self._quantify_last(QuantifierKind.RANGE, min_count=min_n, max_count=max_n)

    @property
    def optional(self) -> RegexBuilder:
        return self._quantify_last(QuantifierKind.OPTIONAL)

    @property
    def zero_or_more(self) -> RegexBuilder:
        return self._quantify_last(QuantifierKind.ZERO_OR_MORE)

    @property
    def one_or_more(self) -> RegexBuilder:
        return self._quantify_last(QuantifierKind.ONE_OR_MORE)

    # ── Exclude ─────────────────────────────────────────────────────

    @property
    def exclude(self) -> ExcludeProxy:
        """As property: returns proxy for negated classes.
        e.g., regex.exclude.digits → \\D+
        """
        return ExcludeProxy(self)

    def excluding(self, chars: str) -> RegexBuilder:
        """Filters characters from the last char class component.
        e.g., regex.words.excluding('_') → [^\\W_]+
        """
        if not self._components:
            raise ValueError("No component to filter")

        last = self._components[-1]

        # If last is a quantified char class, unwrap, filter, re-wrap
        if isinstance(last, Quantifier) and isinstance(last.target, CharClass):
            filtered = ExcludeFilter(last.target.class_type, chars)
            new_last = Quantifier(filtered, last.kind, last.count, last.min_count, last.max_count)
            return RegexBuilder(self._components[:-1] + (new_last,), self._flags)

        if isinstance(last, CharClass):
            filtered = ExcludeFilter(last.class_type, chars)
            return RegexBuilder(self._components[:-1] + (filtered,), self._flags)

        raise ValueError("excluding() can only be applied to a character class")

    # ── Flags ───────────────────────────────────────────────────────

    @property
    def ignore_case(self) -> RegexBuilder:
        return self._with_flag(Flag.IGNORE_CASE)

    @property
    def multiline(self) -> RegexBuilder:
        return self._with_flag(Flag.MULTILINE)

    # ── Compilation & Execution ─────────────────────────────────────

    @property
    def pattern(self) -> str:
        return compile_components(self._components)

    def compile(self) -> re.Pattern[str]:
        if self._compiled is None:
            self._compiled = re.compile(self.pattern, flags_to_re(self._flags))
        return self._compiled

    def search(self, text: str) -> re.Match[str] | None:
        return self.compile().search(text)

    def match(self, text: str) -> re.Match[str] | None:
        return self.compile().match(text)

    def find_all(self, text: str) -> list[str]:
        return self.compile().findall(text)

    def replace(self, text: str, repl: str) -> str:
        return self.compile().sub(repl, text)

    def split(self, text: str) -> list[str]:
        return self.compile().split(text)

    def test(self, text: str) -> bool:
        return self.compile().search(text) is not None
