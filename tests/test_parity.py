"""
Parity tests: verify that readable-regex produces identical results
to equivalent raw `re` patterns across a wide range of complexity.
"""

import re

import pytest
from readable_regex import regex


# ── Helpers ─────────────────────────────────────────────────────────

def assert_same_findall(readable, raw_pattern, text, flags=0):
    """Assert find_all results match re.findall results."""
    raw = re.compile(raw_pattern, flags)
    assert readable.find_all(text) == raw.findall(text)


def assert_same_search(readable, raw_pattern, text, flags=0):
    """Assert both find (or don't find) a match, and the match value is the same."""
    raw = re.compile(raw_pattern, flags)
    r_match = readable.search(text)
    raw_match = raw.search(text)
    if raw_match is None:
        assert r_match is None
    else:
        assert r_match is not None
        assert r_match.group() == raw_match.group()


def assert_same_sub(readable, raw_pattern, text, repl, flags=0):
    """Assert replace results match re.sub results."""
    raw = re.compile(raw_pattern, flags)
    assert readable.replace(text, repl) == raw.sub(repl, text)


def assert_same_split(readable, raw_pattern, text, flags=0):
    """Assert split results match re.split results."""
    raw = re.compile(raw_pattern, flags)
    assert readable.split(text) == raw.split(text)


def assert_same_match_bool(readable, raw_pattern, text, flags=0):
    """Assert test() matches whether re.search finds anything."""
    raw = re.compile(raw_pattern, flags)
    assert readable.test(text) == (raw.search(text) is not None)


# ── Simple patterns ─────────────────────────────────────────────────

class TestSimpleParity:
    """Basic single-component patterns."""

    def test_single_digit(self):
        text = "a1b2c3"
        assert_same_findall(regex.digit, r"\d", text)

    def test_single_word_char(self):
        text = "hello world!"
        assert_same_findall(regex.word, r"\w", text)

    def test_single_whitespace(self):
        text = "a b\tc\nd"
        assert_same_findall(regex.whitespace, r"\s", text)

    def test_any_char(self):
        text = "abc"
        assert_same_findall(regex.any_char, r".", text)

    def test_single_letter(self):
        text = "a1b2c3"
        assert_same_findall(regex.letter, r"[a-zA-Z]", text)

    def test_literal_text(self):
        text = "foo bar foo baz"
        assert_same_findall(regex.then("foo"), r"foo", text)

    def test_literal_with_special_chars(self):
        text = "price is $10.00 or $20.00"
        assert_same_findall(regex.then("$10.00"), re.escape("$10.00"), text)


class TestPluralParity:
    """Plural forms (one or more)."""

    def test_digits(self):
        text = "abc 123 def 456 ghi"
        assert_same_findall(regex.digits, r"\d+", text)

    def test_words(self):
        text = "hello world! foo bar."
        assert_same_findall(regex.words, r"\w+", text)

    def test_whitespaces(self):
        text = "a   b  c d"
        assert_same_findall(regex.whitespaces, r"\s+", text)

    def test_letters(self):
        text = "abc123def456"
        assert_same_findall(regex.letters, r"[a-zA-Z]+", text)

    def test_any_chars(self):
        text = "hello"
        assert_same_findall(regex.any_chars, r".+", text)


# ── Anchored patterns ───────────────────────────────────────────────

class TestAnchorParity:
    def test_starts_with(self):
        r = regex.starts_with("Hello")
        for text in ["Hello world", "hello world", "Say Hello"]:
            assert_same_match_bool(r, r"^Hello", text)

    def test_ends_with(self):
        r = regex.ends_with("world")
        for text in ["hello world", "world hello", "world"]:
            assert_same_match_bool(r, r"world$", text)

    def test_full_line(self):
        r = regex.starts_with().digits.ends_with()
        for text in ["12345", "abc", "123abc", ""]:
            assert_same_match_bool(r, r"^\d+$", text)


# ── Quantifier patterns ─────────────────────────────────────────────

class TestQuantifierParity:
    def test_exactly(self):
        r = regex.digit.exactly(3)
        text = "12 123 1234 12345"
        assert_same_findall(r, r"\d{3}", text)

    def test_between(self):
        r = regex.digit.between(2, 4)
        text = "1 12 123 1234 12345"
        assert_same_findall(r, r"\d{2,4}", text)

    def test_optional(self):
        r = regex.then("colour").then("s").optional
        for text in ["colour", "colours", "color"]:
            assert_same_search(r, r"colours?", text)

    def test_zero_or_more(self):
        r = regex.then("go").then("o").zero_or_more.then("al")
        for text in ["gal", "goal", "goooal", "gool"]:
            assert_same_search(r, r"goo*al", text)


# ── Alternation ──────────────────────────────────────────────────────

class TestAlternationParity:
    def test_any_of_single_chars(self):
        r = regex.any_of("a", "e", "i", "o", "u")
        text = "hello world"
        assert_same_findall(r, r"[aeiou]", text)

    def test_any_of_words(self):
        r = regex.any_of("cat", "dog", "bird")
        text = "I have a cat and a dog but not a bird or fish"
        assert_same_findall(r, r"(?:cat|dog|bird)", text)

    def test_any_of_special_chars(self):
        r = regex.any_of("-", ".", "_")
        text = "a-b.c_d e"
        assert_same_findall(r, r"[\-\._]", text)


# ── Capture group patterns ───────────────────────────────────────────

class TestCaptureParity:
    def test_single_group(self):
        r = regex.capture(regex.digits)
        raw = re.compile(r"(\d+)")
        text = "abc 123 def 456"
        assert r.find_all(text) == raw.findall(text)

    def test_multiple_groups(self):
        r = regex.capture(regex.words).then("=").capture(regex.words)
        raw = re.compile(r"(\w+)=(\w+)")
        text = "key=value foo=bar x=1"
        assert r.find_all(text) == raw.findall(text)

    def test_group_search(self):
        r = regex.capture(regex.digits).then("-").capture(regex.digits)
        raw = re.compile(r"(\d+)-(\d+)")
        text = "range: 10-20"
        r_m = r.search(text)
        raw_m = raw.search(text)
        assert r_m.group(1) == raw_m.group(1)
        assert r_m.group(2) == raw_m.group(2)


# ── Negated classes ──────────────────────────────────────────────────

class TestNegatedParity:
    def test_non_digits(self):
        r = regex.exclude.digits
        text = "a1b2c3"
        assert_same_findall(r, r"\D+", text)

    def test_non_words(self):
        r = regex.exclude.words
        text = "hello, world! foo."
        assert_same_findall(r, r"\W+", text)

    def test_non_whitespace(self):
        r = regex.exclude.whitespaces
        text = "hello world foo"
        assert_same_findall(r, r"\S+", text)


# ── Flag patterns ────────────────────────────────────────────────────

class TestFlagParity:
    def test_ignore_case(self):
        r = regex.then("hello").ignore_case
        for text in ["hello", "HELLO", "Hello", "hElLo", "world"]:
            assert_same_match_bool(r, r"hello", text, re.IGNORECASE)

    def test_multiline(self):
        r = regex.starts_with().digits.ends_with().multiline
        text = "abc\n123\ndef\n456"
        assert_same_findall(r, r"^\d+$", text, re.MULTILINE)


# ── Medium complexity (multi-component chains) ───────────────────────

class TestMediumParity:
    def test_email(self):
        r = regex.words.then("@").words.then(".").words
        raw = r"\w+@\w+\.\w+"
        for text in ["user@example.com", "bad@@x", "a@b.c", "no-at-sign"]:
            assert_same_match_bool(r, raw, text)
            assert_same_search(r, raw, text)

    def test_phone_number(self):
        r = regex.digit.exactly(3).then("-").digit.exactly(3).then("-").digit.exactly(4)
        raw = r"\d{3}\-\d{3}\-\d{4}"
        for text in ["123-456-7890", "12-34-5678", "abc-def-ghij", "call 555-123-4567 now"]:
            assert_same_match_bool(r, raw, text)

    def test_ip_address(self):
        r = (
            regex
            .digit.between(1, 3).then(".")
            .digit.between(1, 3).then(".")
            .digit.between(1, 3).then(".")
            .digit.between(1, 3)
        )
        raw = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        for text in ["192.168.1.1", "10.0.0.255", "not-an-ip", "1.2.3.4.5"]:
            assert_same_search(r, raw, text)

    def test_date_format(self):
        r = regex.digit.exactly(4).then("-").digit.exactly(2).then("-").digit.exactly(2)
        raw = r"\d{4}\-\d{2}\-\d{2}"
        text = "born on 1990-05-15 and graduated 2012-06-01"
        assert_same_findall(r, raw, text)

    def test_hex_color(self):
        r = regex.then("#").any_of("a", "b", "c", "d", "e", "f", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9").exactly(6).ignore_case
        raw = r"#[abcdef0123456789]{6}"
        for text in ["#ff00aa", "#FF00AA", "#123456", "#xyz123", "no color"]:
            assert_same_match_bool(r, raw, text, re.IGNORECASE)


# ── Replace parity ──────────────────────────────────────────────────

class TestReplaceParity:
    def test_censor_digits(self):
        r = regex.digits
        text = "SSN: 123-45-6789, PIN: 9876"
        assert_same_sub(r, r"\d+", text, "***")

    def test_strip_whitespace_runs(self):
        r = regex.whitespaces
        text = "hello   world   foo"
        assert_same_sub(r, r"\s+", text, " ")

    def test_replace_literal(self):
        r = regex.then("foo")
        text = "foo bar foo baz foo"
        assert_same_sub(r, r"foo", text, "qux")


# ── Split parity ────────────────────────────────────────────────────

class TestSplitParity:
    def test_split_whitespace(self):
        r = regex.whitespaces
        text = "hello   world   foo bar"
        assert_same_split(r, r"\s+", text)

    def test_split_comma_space(self):
        r = regex.then(",").whitespace.zero_or_more
        text = "a, b,c, d"
        assert_same_split(r, r",\s*", text)

    def test_split_pipe(self):
        r = regex.whitespace.zero_or_more.then("|").whitespace.zero_or_more
        text = "a | b|c | d"
        assert_same_split(r, r"\s*\|\s*", text)


# ── Complex real-world patterns ──────────────────────────────────────

class TestComplexParity:
    def test_log_line_extraction(self):
        """Extract timestamp and level from log lines."""
        r = (
            regex
            .capture(regex.digit.exactly(4).then("-").digit.exactly(2).then("-").digit.exactly(2))
            .whitespace
            .capture(regex.any_of("INFO", "WARN", "ERROR"))
        )
        raw = re.compile(r"(\d{4}\-\d{2}\-\d{2})\s((?:INFO|WARN|ERROR))")
        text = "2024-01-15 ERROR something broke\n2024-01-16 INFO all good"
        assert r.find_all(text) == raw.findall(text)

    def test_csv_field_extraction(self):
        """Extract words from comma-separated values."""
        r = regex.words
        raw = re.compile(r"\w+")
        text = "name,age,city,country"
        assert r.find_all(text) == raw.findall(text)

    def test_url_domain_extraction(self):
        """Extract domain-like patterns."""
        r = regex.words.then("://").words.then(".").words
        raw = re.compile(r"\w+://\w+\.\w+")
        for text in [
            "visit https://example.com today",
            "use http://localhost.dev for testing",
            "no url here",
        ]:
            assert_same_search(r, r"\w+://\w+\.\w+", text)

    def test_key_value_pairs(self):
        """Parse key=value pairs from config text."""
        r = regex.capture(regex.words).then("=").capture(regex.words)
        raw = re.compile(r"(\w+)=(\w+)")
        text = "host=localhost port=8080 debug=true"
        assert r.find_all(text) == raw.findall(text)

    def test_markdown_bold(self):
        """Find bold markers in markdown."""
        r = regex.then("**").words.then("**")
        raw = re.compile(r"\*\*\w+\*\*")
        text = "This is **bold** and **strong** text"
        assert r.find_all(text) == raw.findall(text)

    def test_anchored_digits_only(self):
        """Full string must be digits only."""
        r = regex.starts_with().digits.ends_with()
        raw = r"^\d+$"
        for text in ["12345", "abc", "123abc", "   123", ""]:
            assert_same_match_bool(r, raw, text)

    def test_optional_protocol(self):
        """Match URL with optional https://."""
        r = regex.then("http").then("s").optional.then("://").words
        raw = re.compile(r"https?://\w+")
        for text in ["http://example", "https://secure", "ftp://other"]:
            assert_same_search(r, r"https?://\w+", text)

    def test_multiline_anchored(self):
        """Match lines starting with # as comments."""
        r = regex.starts_with("#").any_chars.multiline
        raw = re.compile(r"^#.+", re.MULTILINE)
        text = "# comment\ncode\n# another comment\nmore code"
        assert r.find_all(text) == raw.findall(text)

    def test_repeated_group_extraction(self):
        """Extract all (word, number) pairs."""
        r = regex.capture(regex.words).then(":").capture(regex.digits)
        raw = re.compile(r"(\w+):(\d+)")
        text = "cpu:95 mem:82 disk:45 net:12"
        assert r.find_all(text) == raw.findall(text)

    def test_negated_split(self):
        """Split on non-word characters."""
        r = regex.exclude.words
        raw = re.compile(r"\W+")
        text = "hello-world foo_bar baz!qux"
        assert r.split(text) == raw.split(text)
