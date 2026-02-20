import pytest
from readable_regex.builder import RegexBuilder


def rb() -> RegexBuilder:
    return RegexBuilder()


class TestAnchorsAndLiterals:
    def test_starts_with_text(self):
        assert rb().starts_with("Hi").pattern == "^Hi"

    def test_starts_with_no_text(self):
        assert rb().starts_with().pattern == "^"

    def test_ends_with_text(self):
        assert rb().ends_with("bye").pattern == "bye$"

    def test_ends_with_no_text(self):
        assert rb().ends_with().pattern == "$"

    def test_then(self):
        assert rb().then("hello").pattern == "hello"

    def test_then_escapes(self):
        assert rb().then("a.b").pattern == r"a\.b"


class TestSingularItems:
    def test_digit(self):
        assert rb().digit.pattern == r"\d"

    def test_word(self):
        assert rb().word.pattern == r"\w"

    def test_whitespace(self):
        assert rb().whitespace.pattern == r"\s"

    def test_any_char(self):
        assert rb().any_char.pattern == "."

    def test_letter(self):
        assert rb().letter.pattern == "[a-zA-Z]"


class TestPluralItems:
    def test_digits(self):
        assert rb().digits.pattern == r"\d+"

    def test_words(self):
        assert rb().words.pattern == r"\w+"

    def test_whitespaces(self):
        assert rb().whitespaces.pattern == r"\s+"

    def test_any_chars(self):
        assert rb().any_chars.pattern == ".+"

    def test_letters(self):
        assert rb().letters.pattern == "[a-zA-Z]+"


class TestAnyOf:
    def test_single_chars(self):
        assert rb().any_of("a", "b", "c").pattern == "[abc]"

    def test_multi_char(self):
        assert rb().any_of("cat", "dog").pattern == "(?:cat|dog)"


class TestCapture:
    def test_capture_sub_builder(self):
        assert rb().capture(rb().words).pattern == r"(\w+)"

    def test_capture_multi_component(self):
        inner = rb().digits.then("-").digits
        assert rb().capture(inner).pattern == r"(\d+\-\d+)"


class TestQuantifiers:
    def test_exactly(self):
        assert rb().digit.exactly(3).pattern == r"\d{3}"

    def test_between(self):
        assert rb().digit.between(1, 3).pattern == r"\d{1,3}"

    def test_optional(self):
        assert rb().digit.optional.pattern == r"\d?"

    def test_zero_or_more(self):
        assert rb().word.zero_or_more.pattern == r"\w*"

    def test_one_or_more(self):
        assert rb().digit.one_or_more.pattern == r"\d+"

    def test_quantifier_no_component_raises(self):
        with pytest.raises(ValueError):
            rb().exactly(3)


class TestExclude:
    def test_exclude_proxy_digit(self):
        assert rb().exclude.digit.pattern == r"\D"

    def test_exclude_proxy_digits(self):
        assert rb().exclude.digits.pattern == r"\D+"

    def test_exclude_proxy_word(self):
        assert rb().exclude.word.pattern == r"\W"

    def test_exclude_proxy_words(self):
        assert rb().exclude.words.pattern == r"\W+"

    def test_exclude_proxy_whitespace(self):
        assert rb().exclude.whitespace.pattern == r"\S"

    def test_exclude_proxy_letter(self):
        assert rb().exclude.letter.pattern == "[^a-zA-Z]"

    def test_excluding_chars_from_plural(self):
        assert rb().words.excluding("_").pattern == r"[^\W_]+"

    def test_excluding_chars_from_singular(self):
        assert rb().word.excluding("_").pattern == r"[^\W_]"

    def test_excluding_on_non_charclass_raises(self):
        with pytest.raises(ValueError):
            rb().then("hello").excluding("_")


class TestFlags:
    def test_ignore_case(self):
        p = rb().then("hi").ignore_case.compile()
        assert p.match("HI") is not None

    def test_multiline(self):
        p = rb().starts_with("x").multiline.compile()
        assert p.search("a\nxyz") is not None


class TestImmutability:
    def test_branching(self):
        base = rb().starts_with("A")
        a = base.digit
        b = base.word
        assert a.pattern == r"^A\d"
        assert b.pattern == r"^A\w"
        assert base.pattern == "^A"

    def test_flags_independent(self):
        base = rb().then("x")
        ci = base.ignore_case
        ml = base.multiline
        assert ci._flags != ml._flags
        assert len(base._flags) == 0


class TestPatternProperty:
    def test_shows_raw_regex(self):
        p = rb().starts_with("Hello").whitespace.words.ends_with()
        assert p.pattern == r"^Hello\s\w+$"
