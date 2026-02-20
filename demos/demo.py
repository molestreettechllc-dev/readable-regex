r"""
readable-regex v2 demo — fluent regex with plural convention.

  singular = exactly one:   digit → \d, word → \w
  plural = one or more:     digits → \d+, words → \w+
"""

import sys
sys.path.insert(0, "src")

from readable_regex import regex


def section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


# ---------------------------------------------------------------------------
section("1. Email pattern — concise with plurals")
# ---------------------------------------------------------------------------

email = regex.words.then("@").words.then(".").words
print(f"Pattern: {email.pattern}")
for addr in ["user@example.com", "bad@@address", "hello@world.org"]:
    print(f"  {addr!r:25s} -> {email.test(addr)}")


# ---------------------------------------------------------------------------
section("2. Phone number — digit.exactly(n) for fixed widths")
# ---------------------------------------------------------------------------

phone = (
    regex
    .digit.exactly(3).then("-")
    .digit.exactly(3).then("-")
    .digit.exactly(4)
)
print(f"Pattern: {phone.pattern}")
for num in ["123-456-7890", "12-34-5678", "abc-def-ghij"]:
    print(f"  {num!r:20s} -> {phone.test(num)}")


# ---------------------------------------------------------------------------
section("3. IP address — digit.between(1,3)")
# ---------------------------------------------------------------------------

ip = (
    regex
    .digit.between(1, 3).then(".")
    .digit.between(1, 3).then(".")
    .digit.between(1, 3).then(".")
    .digit.between(1, 3)
)
print(f"Pattern: {ip.pattern}")
for addr in ["192.168.1.1", "10.0.0.255", "999.999.999.999", "not.an.ip"]:
    print(f"  {addr!r:25s} -> {ip.test(addr)}")


# ---------------------------------------------------------------------------
section("4. Extract numbers — plurals + find_all")
# ---------------------------------------------------------------------------

text = "Order #42 has 3 items totaling $129"
result = regex.digits.find_all(text)
print(f"Pattern: {regex.digits.pattern}")
print(f"Text:    {text!r}")
print(f"Found:   {result}")


# ---------------------------------------------------------------------------
section("5. Capturing groups")
# ---------------------------------------------------------------------------

kv = regex.capture(regex.words).then("=").capture(regex.any_chars)
text = "color=blue"
m = kv.search(text)
print(f"Pattern: {kv.pattern}")
print(f"Text:    {text!r}")
if m:
    print(f"  Key:   {m.group(1)}")
    print(f"  Value: {m.group(2)}")


# ---------------------------------------------------------------------------
section("6. Case-insensitive matching")
# ---------------------------------------------------------------------------

greeting = regex.starts_with("hello").ignore_case
print(f"Pattern: {greeting.pattern}  (ignore case)")
for t in ["hello world", "HELLO WORLD", "Hello World", "hey there"]:
    print(f"  {t!r:20s} -> {greeting.test(t)}")


# ---------------------------------------------------------------------------
section("7. Search and replace")
# ---------------------------------------------------------------------------

text = "My SSN is 123-45-6789 and PIN is 9876"
result = regex.digits.replace(text, "***")
print(f"Original: {text!r}")
print(f"Censored: {result!r}")


# ---------------------------------------------------------------------------
section("8. Splitting text")
# ---------------------------------------------------------------------------

text = "apple, banana,cherry, date"
result = regex.then(",").whitespace.zero_or_more.split(text)
print(f"Text:  {text!r}")
print(f"Parts: {result}")


# ---------------------------------------------------------------------------
section("9. Negated classes with exclude")
# ---------------------------------------------------------------------------

non_digits = regex.exclude.digits
print(f"Pattern: {non_digits.pattern}")
print(f"Find non-digit runs in 'a1b2c3': {non_digits.find_all('a1b2c3')}")


# ---------------------------------------------------------------------------
section("10. Immutable builder — safe reuse")
# ---------------------------------------------------------------------------

base = regex.starts_with("LOG-")
error_log = base.then("ERROR").any_chars
warn_log = base.then("WARN").any_chars

print(f"Base:  {base.pattern}")
print(f"Error: {error_log.pattern}")
print(f"Warn:  {warn_log.pattern}")

for line in ["LOG-ERROR disk full", "LOG-WARN low memory", "LOG-INFO started"]:
    err = error_log.test(line)
    warn = warn_log.test(line)
    print(f"  {line!r:30s}  error={err}  warn={warn}")


print()
