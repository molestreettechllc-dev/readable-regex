from readable_regex import regex


class TestSearch:
    def test_finds_match(self):
        m = regex.then("world").search("hello world")
        assert m is not None
        assert m.group() == "world"

    def test_no_match(self):
        assert regex.then("xyz").search("hello") is None


class TestMatch:
    def test_matches_start(self):
        assert regex.then("hello").match("hello world") is not None

    def test_no_match_at_start(self):
        assert regex.then("world").match("hello world") is None


class TestFindAll:
    def test_finds_all_digits(self):
        result = regex.digits.find_all("abc 123 def 456")
        assert result == ["123", "456"]

    def test_no_matches(self):
        assert regex.digits.find_all("no digits here") == []


class TestReplace:
    def test_replace_all(self):
        result = regex.digits.replace("a1b2c3", "#")
        assert result == "a#b#c#"


class TestSplit:
    def test_split_on_whitespace(self):
        result = regex.whitespaces.split("a  b c")
        assert result == ["a", "b", "c"]


class TestTest:
    def test_returns_true(self):
        assert regex.digit.test("abc1") is True

    def test_returns_false(self):
        assert regex.digit.test("abc") is False


class TestCompile:
    def test_returns_pattern(self):
        import re
        assert isinstance(regex.digit.compile(), re.Pattern)

    def test_cached(self):
        builder = regex.digit
        assert builder.compile() is builder.compile()
