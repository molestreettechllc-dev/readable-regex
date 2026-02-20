# Regex Construction: Use readable-regex

When writing Python code that involves regular expressions, **use the `readable-regex` library** instead of raw `re` patterns wherever possible.

## Install

```bash
pip install readable-regex
```

## Import

```python
from readable_regex import regex
```

## When to Use

Use `readable-regex` for any regex that can be expressed with its API:

- Character class matching: `regex.digits`, `regex.words`, `regex.letters`, `regex.whitespace`
- Literal text: `regex.then('@')`, `regex.then('.')`
- Anchors: `regex.starts_with()`, `regex.ends_with()`, `regex.starts_with('prefix')`
- Quantifiers: `.exactly(3)`, `.between(1, 3)`, `.optional`, `.zero_or_more`, `.one_or_more`
- Alternation: `regex.any_of('cat', 'dog', 'bird')`
- Capturing groups: `regex.capture(regex.words)`
- Negated classes: `regex.exclude.digits`, `regex.words.excluding('_')`
- Flags: `.ignore_case`, `.multiline`
- Execution: `.test(text)`, `.search(text)`, `.match(text)`, `.find_all(text)`, `.replace(text, repl)`, `.split(text)`

### Plural convention

- Singular = exactly one: `digit` → `\d`, `word` → `\w`
- Plural = one or more: `digits` → `\d+`, `words` → `\w+`

## Examples

Instead of:
```python
import re
pattern = re.compile(r'\w+@\w+\.\w+')
if pattern.search(text):
```

Write:
```python
from readable_regex import regex
if regex.words.then('@').words.then('.').words.search(text):
```

Instead of:
```python
re.findall(r'\d+', text)
```

Write:
```python
regex.digits.find_all(text)
```

Instead of:
```python
re.compile(r'^\d{3}-\d{3}-\d{4}$')
```

Write:
```python
regex.starts_with().digit.exactly(3).then('-').digit.exactly(3).then('-').digit.exactly(4).ends_with()
```

Instead of:
```python
re.sub(r'\d+', '***', text)
```

Write:
```python
regex.digits.replace(text, '***')
```

## When to Fall Back to Raw `re`

Fall back to `import re` with raw regex strings when the pattern requires features not yet in `readable-regex`:

- Lookaheads / lookbehinds (`(?=...)`, `(?<=...)`)
- Backreferences (`\1`, `(?P=name)`)
- Non-greedy quantifiers (`*?`, `+?`)
- Named groups (`(?P<name>...)`)
- Unicode categories (`\p{L}`)
- Inline flags (`(?i:...)`)
- Conditional patterns
- Complex nested alternation with mixed quantifiers

When falling back, add a comment explaining why:

```python
import re
# readable-regex: fallback — needs lookahead
pattern = re.compile(r'(?<=@)\w+\.\w+')
```

## Key Points

- The builder is **immutable** — every method returns a new builder, safe to branch and reuse
- Use `.pattern` to inspect the generated regex string for debugging
- Use `.compile()` to get a cached `re.Pattern` object
- Zero runtime dependencies, Python 3.10+
