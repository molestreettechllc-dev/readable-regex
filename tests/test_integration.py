from readable_regex import regex


class TestEmailLike:
    def test_matches_email(self):
        pattern = regex.words.then("@").words.then(".").words
        assert pattern.test("user@example.com") is True
        assert pattern.pattern == r"\w+@\w+\.\w+"

    def test_rejects_non_email(self):
        pattern = (
            regex
            .starts_with()
            .words.then("@").words.then(".").words
            .ends_with()
        )
        assert pattern.test("no-at-sign") is False


class TestDigitsExtraction:
    def test_extract_digits(self):
        result = regex.digits.find_all("abc 123 def 456")
        assert result == ["123", "456"]


class TestPhoneNumber:
    def test_us_phone(self):
        pattern = (
            regex
            .starts_with()
            .then("(").optional
            .digit.exactly(3)
            .then(")").optional
            .any_of("-", " ", ".")
            .digit.exactly(3)
            .any_of("-", " ", ".")
            .digit.exactly(4)
            .ends_with()
        )
        assert pattern.test("123-456-7890") is True
        assert pattern.test("(123) 456-7890") is True
        assert pattern.test("123.456.7890") is True


class TestIPAddress:
    def test_ip_address(self):
        pattern = (
            regex
            .starts_with()
            .digit.between(1, 3).then(".")
            .digit.between(1, 3).then(".")
            .digit.between(1, 3).then(".")
            .digit.between(1, 3)
            .ends_with()
        )
        assert pattern.test("192.168.1.1") is True
        assert pattern.test("10.0.0.255") is True
        assert pattern.test("not an ip") is False


class TestCaseInsensitive:
    def test_ignore_case_search(self):
        pattern = regex.starts_with("hello").ignore_case
        assert pattern.test("HELLO world") is True
        assert pattern.test("Hello World") is True


class TestImmutabilityIntegration:
    def test_branching_produces_independent_patterns(self):
        base = regex.starts_with("prefix-")
        digits_pattern = base.digits.ends_with()
        words_pattern = base.words.ends_with()

        assert digits_pattern.test("prefix-123") is True
        assert digits_pattern.test("prefix-abc") is False
        assert words_pattern.test("prefix-abc") is True
        assert words_pattern.test("prefix-abc123") is True

        # base itself is unchanged
        assert base.pattern == "^prefix\\-"


class TestCaptureGroups:
    def test_group_extraction(self):
        pattern = (
            regex
            .capture(regex.words)
            .then("=")
            .capture(regex.any_chars)
        )
        m = pattern.search("color=blue")
        assert m is not None
        assert m.group(1) == "color"
        assert m.group(2) == "blue"


class TestExcludeIntegration:
    def test_negated_class(self):
        # Match non-digit characters
        result = regex.exclude.digits.find_all("a1b2c3")
        assert result == ["a", "b", "c"]

    def test_excluding_filter(self):
        # Words without underscore
        import re
        pattern = regex.words.excluding("_")
        compiled = pattern.compile()
        assert compiled.fullmatch("hello") is not None
        assert compiled.fullmatch("hello_world") is None


class TestReplaceIntegration:
    def test_censor_digits(self):
        result = regex.digits.replace("Call 555-1234 now", "***")
        assert result == "Call ***-*** now"


class TestSplitIntegration:
    def test_split_csv(self):
        result = regex.then(",").whitespace.zero_or_more.split("a, b,c, d")
        assert result == ["a", "b", "c", "d"]
