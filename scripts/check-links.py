#!/usr/bin/env python3
"""Fail when a repository Markdown link points to a missing local file."""

from __future__ import annotations

import re
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def main() -> int:
    failures = []
    for document in ROOT.rglob("*.md"):
        if ".git" in document.parts:
            continue
        for target in LINK.findall(document.read_text(encoding="utf-8")):
            target = target.strip().split("#", 1)[0]
            if not target or "://" in target or target.startswith(("mailto:", "#")):
                continue
            if not (document.parent / target).resolve().exists():
                failures.append(f"{document.relative_to(ROOT)} -> {target}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("PASS: all local Markdown links resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
