from __future__ import annotations

import re
from enum import Enum


class Flag(Enum):
    IGNORE_CASE = "IGNORECASE"
    MULTILINE = "MULTILINE"


def flags_to_re(flags: frozenset[Flag]) -> re.RegexFlag:
    mapping = {
        Flag.IGNORE_CASE: re.IGNORECASE,
        Flag.MULTILINE: re.MULTILINE,
    }
    result = re.RegexFlag(0)
    for flag in flags:
        result |= mapping[flag]
    return result
