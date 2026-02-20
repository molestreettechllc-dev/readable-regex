from readable_regex.components import (
    Anchor,
    AnchorType,
    AnyOf,
    CharClass,
    CharClassType,
    ExcludeFilter,
    Group,
    Literal,
    NegatedCharClass,
    Quantifier,
    QuantifierKind,
)


class TestLiteral:
    def test_plain_text(self):
        assert Literal("hello").compile() == "hello"

    def test_escapes_special_chars(self):
        assert Literal("a.b").compile() == r"a\.b"
        assert Literal("(x)").compile() == r"\(x\)"

    def test_empty_string(self):
        assert Literal("").compile() == ""


class TestAnchor:
    def test_start(self):
        assert Anchor(AnchorType.START).compile() == "^"

    def test_end(self):
        assert Anchor(AnchorType.END).compile() == "$"


class TestCharClass:
    def test_digit(self):
        assert CharClass(CharClassType.DIGIT).compile() == r"\d"

    def test_word(self):
        assert CharClass(CharClassType.WORD).compile() == r"\w"

    def test_whitespace(self):
        assert CharClass(CharClassType.WHITESPACE).compile() == r"\s"

    def test_any(self):
        assert CharClass(CharClassType.ANY).compile() == "."

    def test_letter(self):
        assert CharClass(CharClassType.LETTER).compile() == "[a-zA-Z]"


class TestNegatedCharClass:
    def test_not_digit(self):
        assert NegatedCharClass(CharClassType.DIGIT).compile() == r"\D"

    def test_not_word(self):
        assert NegatedCharClass(CharClassType.WORD).compile() == r"\W"

    def test_not_whitespace(self):
        assert NegatedCharClass(CharClassType.WHITESPACE).compile() == r"\S"

    def test_not_letter(self):
        assert NegatedCharClass(CharClassType.LETTER).compile() == "[^a-zA-Z]"


class TestAnyOf:
    def test_single_chars_use_bracket(self):
        assert AnyOf(["a", "b", "c"]).compile() == "[abc]"

    def test_multi_char_uses_alternation(self):
        assert AnyOf(["foo", "bar"]).compile() == "(?:foo|bar)"

    def test_mixed_lengths_uses_alternation(self):
        assert AnyOf(["a", "bb"]).compile() == "(?:a|bb)"

    def test_escapes_special_chars(self):
        assert AnyOf([".", "-"]).compile() == r"[\.\-]"


class TestGroup:
    def test_wraps_content(self):
        assert Group([Literal("abc")]).compile() == "(abc)"

    def test_multiple_components(self):
        content = [Literal("a"), CharClass(CharClassType.DIGIT)]
        assert Group(content).compile() == r"(a\d)"


class TestQuantifier:
    def test_one_or_more(self):
        assert Quantifier(CharClass(CharClassType.DIGIT), QuantifierKind.ONE_OR_MORE).compile() == r"\d+"

    def test_zero_or_more(self):
        assert Quantifier(CharClass(CharClassType.WORD), QuantifierKind.ZERO_OR_MORE).compile() == r"\w*"

    def test_optional(self):
        assert Quantifier(CharClass(CharClassType.DIGIT), QuantifierKind.OPTIONAL).compile() == r"\d?"

    def test_exact(self):
        assert Quantifier(CharClass(CharClassType.DIGIT), QuantifierKind.EXACT, count=3).compile() == r"\d{3}"

    def test_range(self):
        assert Quantifier(CharClass(CharClassType.DIGIT), QuantifierKind.RANGE, min_count=1, max_count=3).compile() == r"\d{1,3}"

    def test_wraps_literal(self):
        assert Quantifier(Literal("abc"), QuantifierKind.ONE_OR_MORE).compile() == "(?:abc)+"

    def test_single_char_literal_no_wrap(self):
        assert Quantifier(Literal("a"), QuantifierKind.ONE_OR_MORE).compile() == "a+"

    def test_no_double_wrap_group(self):
        assert Quantifier(Group([Literal("x")]), QuantifierKind.OPTIONAL).compile() == "(x)?"


class TestExcludeFilter:
    def test_word_excluding_underscore(self):
        result = ExcludeFilter(CharClassType.WORD, "_").compile()
        assert result == r"[^\W_]"

    def test_letter_excluding_chars(self):
        result = ExcludeFilter(CharClassType.LETTER, "x").compile()
        assert result == r"[^a-zA-Zx]"
