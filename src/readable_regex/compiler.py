from __future__ import annotations

from typing import Sequence

from readable_regex.components import Component


def compile_components(components: Sequence[Component]) -> str:
    return "".join(c.compile() for c in components)
