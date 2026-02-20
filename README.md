# readable-regex

A fluent, chainable Python API for building regular expressions that read like English.

**[Documentation](https://molestreettechllc-dev.github.io/readable-regex/)**

## Install

```bash
pip install readable-regex
```

## Quick Start

```python
from readable_regex import regex

# Email pattern
regex.words.then('@').words.then('.').words.test("user@example.com")  # True

# Phone number
regex.digit.exactly(3).then('-').digit.exactly(3).then('-').digit.exactly(4).test("123-456-7890")  # True

# Extract all numbers
regex.digits.find_all("Order #42 has 3 items totaling $129")  # ['42', '3', '129']
```

## Vocabulary

The API uses a **plural convention**: singular = exactly one, plural = one or more.

### Items — what you match

| Singular | Plural (1+) | Regex |
|---|---|---|
| `digit` | `digits` | `\d` / `\d+` |
| `word` | `words` | `\w` / `\w+` |
| `letter` | `letters` | `[a-zA-Z]` / `[a-zA-Z]+` |
| `whitespace` | `whitespaces` | `\s` / `\s+` |
| `any_char` | `any_chars` | `.` / `.+` |
| `then('text')` | — | escaped literal |
| `any_of('a', 'b')` | — | `[ab]` or `(?:foo\|bar)` |

### Modifiers — how you constrain

| Modifier | Example | Effect |
|---|---|---|
| `exactly(n)` | `digit.exactly(3)` | `\d{3}` |
| `between(n, m)` | `digit.between(1, 3)` | `\d{1,3}` |
| `optional` | `digit.optional` | `\d?` |
| `zero_or_more` | `digit.zero_or_more` | `\d*` |
| `starts_with(text?)` | `starts_with('Hello')` | `^Hello` |
| `ends_with(text?)` | `ends_with('!')` | `!$` |
| `ignore_case` | — | case-insensitive flag |
| `multiline` | — | multiline flag |
| `exclude.digits` | — | `\D+` (negated class) |
| `excluding('_')` | `words.excluding('_')` | `[^\W_]+` |
| `capture(builder)` | `capture(regex.words)` | `(\w+)` |

### Execution — terminal methods

| Method | Returns |
|---|---|
| `test(text)` | `bool` |
| `search(text)` | `re.Match \| None` |
| `match(text)` | `re.Match \| None` |
| `find_all(text)` | `list[str]` |
| `replace(text, repl)` | `str` |
| `split(text)` | `list[str]` |
| `compile()` | `re.Pattern` (cached) |
| `.pattern` | raw regex string |

## Examples

### Email validation

```python
email = regex.words.then('@').words.then('.').words
email.test("user@example.com")   # True
email.test("bad@@address")       # False
email.pattern                    # '\w+@\w+\.\w+'
```

### Phone number

```python
phone = (
    regex
    .digit.exactly(3).then('-')
    .digit.exactly(3).then('-')
    .digit.exactly(4)
)
phone.test("123-456-7890")  # True
phone.pattern               # '\d{3}\-\d{3}\-\d{4}'
```

### IP address

```python
ip = (
    regex
    .digit.between(1, 3).then('.')
    .digit.between(1, 3).then('.')
    .digit.between(1, 3).then('.')
    .digit.between(1, 3)
)
ip.test("192.168.1.1")  # True
```

### Capturing groups

```python
kv = regex.capture(regex.words).then('=').capture(regex.any_chars)
m = kv.search("color=blue")
m.group(1)  # 'color'
m.group(2)  # 'blue'
```

### Case-insensitive matching

```python
greeting = regex.starts_with('hello').ignore_case
greeting.test("HELLO world")  # True
greeting.test("hey there")    # False
```

### Search and replace

```python
regex.digits.replace("My SSN is 123-45-6789", "***")
# 'My SSN is ***-***-***'
```

### Splitting text

```python
regex.then(',').whitespace.zero_or_more.split("a, b,c, d")
# ['a', 'b', 'c', 'd']
```

### Negated classes

```python
regex.exclude.digits.find_all("a1b2c3")  # ['a', 'b', 'c']
regex.words.excluding('_').pattern        # '[^\W_]+'
```

### Immutable builder — safe reuse

```python
base = regex.starts_with('LOG-')
errors = base.then('ERROR').any_chars
warns  = base.then('WARN').any_chars

errors.test("LOG-ERROR disk full")  # True
warns.test("LOG-WARN low memory")   # True
base.pattern                        # '^LOG\-' (unchanged)
```

## Requirements

- Python 3.10+
- Zero runtime dependencies

## License

MIT
