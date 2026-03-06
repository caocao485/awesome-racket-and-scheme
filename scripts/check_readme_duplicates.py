#!/usr/bin/env python3
"""Check README.md for duplicated awesome-list entries.

The check is normalization-based and catches duplicates by:
1) entry name (case-insensitive, trimmed, internal spaces collapsed)
2) repository URL (ignoring scheme case, trailing slash, and optional `.git`)
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ENTRY_RE = re.compile(r"^- \[([^\]]+)\]\((https?://[^\)]+)\)")


def normalize_name(name: str) -> str:
    return " ".join(name.strip().lower().split())


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return f"{parsed.netloc.lower()}{path.lower()}"


def main() -> int:
    readme = Path("README.md")
    if not readme.exists():
        print("ERROR: README.md not found")
        return 2

    by_name: dict[str, list[tuple[int, str]]] = defaultdict(list)
    by_url: dict[str, list[tuple[int, str]]] = defaultdict(list)

    for lineno, line in enumerate(readme.read_text(encoding="utf-8").splitlines(), start=1):
        match = ENTRY_RE.match(line)
        if not match:
            continue
        raw_name, raw_url = match.groups()
        by_name[normalize_name(raw_name)].append((lineno, raw_name))
        by_url[normalize_url(raw_url)].append((lineno, raw_url))

    has_error = False

    dup_names = {k: v for k, v in by_name.items() if len(v) > 1}
    dup_urls = {k: v for k, v in by_url.items() if len(v) > 1}

    if dup_names:
        has_error = True
        print("Duplicate entry names found:")
        for key, values in sorted(dup_names.items()):
            print(f"  - {key}")
            for lineno, raw_name in values:
                print(f"      line {lineno}: {raw_name}")

    if dup_urls:
        has_error = True
        print("Duplicate repository URLs found:")
        for key, values in sorted(dup_urls.items()):
            print(f"  - {key}")
            for lineno, raw_url in values:
                print(f"      line {lineno}: {raw_url}")

    if has_error:
        return 1

    print("OK: no duplicate README entries detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
