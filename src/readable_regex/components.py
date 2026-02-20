from __future__ import annotations

import re
from enum import Enum
from typing import Protocol, Sequence


class Component(Protocol):
    def compile(self) -> str: ...


class Literal:
    def __init__(self, text: str) -> None:
        self.text = text

    def compile(self) -> str:
        return re.escape(self.text)


class AnchorType(Enum):
    START = "^"
    END = "$"


class Anchor:
    def __init__(self, anchor_type: AnchorType) -> None:
        self.anchor_type = anchor_type

    def compile(self) -> str:
        return self.anchor_type.value


class CharClassType(Enum):
    DIGIT = r"\d"
    WORD = r"\w"
    WHITESPACE = r"\s"
    ANY = "."
    LETTER = "[a-zA-Z]"


NEGATED_MAP = {
    CharClassType.DIGIT: r"\D",
    CharClassType.WORD: r"\W",
    CharClassType.WHITESPACE: r"\S",
    CharClassType.ANY: r"[^\s\S]",  # negation of . (nothing matches)
    CharClassType.LETTER: r"[^a-zA-Z]",
}


class CharClass:
    def __init__(self, class_type: CharClassType) -> None:
        self.class_type = class_type

    def compile(self) -> str:
        return self.class_type.value


class NegatedCharClass:
    def __init__(self, class_type: CharClassType) -> None:
        self.class_type = class_type

    def compile(self) -> str:
        return NEGATED_MAP[self.class_type]


class AnyOf:
    def __init__(self, items: Sequence[str]) -> None:
        self.items = list(items)

    def compile(self) -> str:
        if all(len(item) == 1 for item in self.items):
            escaped = "".join(re.escape(ch) for ch in self.items)
            return f"[{escaped}]"
        escaped_items = [re.escape(item) for item in self.items]
        return f"(?:{'|'.join(escaped_items)})"


class Group:
    def __init__(self, content: Sequence[Component]) -> None:
        self.content = list(content)

    def compile(self) -> str:
        from readable_regex.compiler import compile_components

        inner = compile_components(self.content)
        return f"({inner})"


class QuantifierKind(Enum):
    ONE_OR_MORE = "+"
    ZERO_OR_MORE = "*"
    OPTIONAL = "?"
    EXACT = "exact"
    RANGE = "range"


class Quantifier:
    def __init__(
        self,
        target: Component,
        kind: QuantifierKind,
        count: int | None = None,
        min_count: int | None = None,
        max_count: int | None = None,
    ) -> None:
        self.target = target
        self.kind = kind
        self.count = count
        self.min_count = min_count
        self.max_count = max_count

    def compile(self) -> str:
        inner = self.target.compile()
        needs_wrap = (
            len(inner) > 1
            and not isinstance(self.target, (CharClass, NegatedCharClass, Group))
            and not (inner.startswith("(") and inner.endswith(")"))
            and not (inner.startswith("[") and inner.endswith("]"))
        )
        if needs_wrap:
            inner = f"(?:{inner})"

        if self.kind == QuantifierKind.EXACT:
            return f"{inner}{{{self.count}}}"
        elif self.kind == QuantifierKind.RANGE:
            return f"{inner}{{{self.min_count},{self.max_count}}}"
        else:
            return f"{inner}{self.kind.value}"


class ExcludeFilter:
    """Represents a character class with certain characters excluded."""

    def __init__(self, base: CharClassType, excluded_chars: str) -> None:
        self.base = base
        self.excluded_chars = excluded_chars

    def compile(self) -> str:
        # Build a negated character class that excludes both the negation
        # of the base class and the excluded characters.
        # e.g., \w excluding '_' → [^\W_]
        negated_base = NEGATED_MAP[self.base]
        escaped_excluded = re.escape(self.excluded_chars)

        # If negated base is a simple escape like \W, use it directly in bracket
        if negated_base.startswith("\\"):
            return f"[^{negated_base}{escaped_excluded}]"
        # If it's a bracket expression like [^a-zA-Z], extract the inner part
        if negated_base.startswith("[^") and negated_base.endswith("]"):
            inner = negated_base[2:-1]
            return f"[^{inner}{escaped_excluded}]"
        # Fallback
        return f"[^{negated_base}{escaped_excluded}]"
