#!/usr/bin/env python3
"""Small, explicit SFZ path-safety primitives used by the library audit contract tests.

This is not a complete SFZ parser or sample-library audit implementation.
"""
from __future__ import annotations
import re

# SFZ assignment values may be quoted or unquoted. Some source exports encode
# line endings as the two literal characters backslash+n; treat that suffix as
# a delimiter so generator opcodes such as *sine are not mistaken for paths.
ASSIGNMENT = re.compile(
    r"""(?im)(?:^|[\s])([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s]+?))(?:\\n|(?=\s|$))"""
)


def normalize_suffix(value: str) -> str:
    """Normalize a path suffix beginning at its Samples root.

    Leading traversal before the Samples root is discarded as legacy prefix
    noise. Traversal within Samples is collapsed, but cannot escape Samples.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError("sample path must be a non-empty string")
    parts = value.replace("\\", "/").split("/")
    start = next((i for i, part in enumerate(parts) if part.casefold() == "samples"), None)
    if start is None:
        raise ValueError(f"sample path does not contain a Samples root: {value!r}")
    normalized = ["Samples"]
    for part in parts[start + 1:]:
        if part in ("", "."):
            continue
        if part == "..":
            if len(normalized) == 1:
                raise ValueError(f"sample path escapes Samples root: {value!r}")
            normalized.pop()
            continue
        if ":" in part:
            raise ValueError(f"drive-qualified component is not allowed: {part!r}")
        normalized.append(part)
    if len(normalized) == 1:
        raise ValueError(f"sample path does not identify a file below Samples: {value!r}")
    return "/".join(normalized)
