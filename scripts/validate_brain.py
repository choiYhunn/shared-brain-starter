#!/usr/bin/env python3
"""Validate a private Shared Brain before commit/push."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED = [
    "brain/00_CURRENT.md",
    "brain/01_PROFILE.md",
    "brain/02_SOURCE_PRIORITY.md",
    "brain/DECISIONS.md",
    "brain/projects/INDEX.md",
]
ALLOWED_TOP = {"brain", "sources", "inbox"}
MAX_FILE_CHARS = 1_200_000
MAX_MARKDOWN_FILES = 5000

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("openai-style-key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("generic-bearer", re.compile(r"(?i)\bAuthorization\s*:\s*Bearer\s+[A-Za-z0-9._~+/=-]{20,}")),
]

PII_WARNINGS: list[tuple[str, re.Pattern[str]]] = [
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("phone-like", re.compile(r"(?<!\d)(?:\+?\d{1,3}[- .]?)?(?:\d{2,3}[- .]?){2,3}\d{3,4}(?!\d)")),
]


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    errors: list[str] = []
    warnings: list[str] = []

    if not root.exists() or not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2

    for required in REQUIRED:
        if not (root / required).is_file():
            errors.append(f"missing required file: {required}")

    markdown = sorted(root.rglob("*.md"))
    if len(markdown) > MAX_MARKDOWN_FILES:
        errors.append(f"too many Markdown files: {len(markdown)} > {MAX_MARKDOWN_FILES}")

    for path in markdown:
        relative = rel(root, path)
        parts = Path(relative).parts
        if not parts or parts[0] not in ALLOWED_TOP:
            warnings.append(f"non-canonical top-level Markdown file: {relative}")

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"not UTF-8: {relative}")
            continue

        if len(text) > MAX_FILE_CHARS:
            errors.append(f"oversized file: {relative} ({len(text):,} chars)")

        for name, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible {name} secret in {relative}")

        for name, pattern in PII_WARNINGS:
            if pattern.search(text):
                warnings.append(f"review {name} in {relative}; keep only if intentionally needed")

        if "<!-- FILE:" in text or "<!-- END FILE -->" in text:
            warnings.append(f"bootstrap marker remains inside canonical file: {relative}")

    banned_dirs = ["vault", "raw", "secrets", "archive"]
    for name in banned_dirs:
        if (root / name).exists():
            warnings.append(f"sensitive/raw directory exists in repo root: {name}/")

    print(f"Markdown files: {len(markdown)}")
    for warning in sorted(set(warnings)):
        print(f"WARNING: {warning}")
    for error in sorted(set(errors)):
        print(f"ERROR: {error}")

    if errors:
        print(f"FAIL: {len(set(errors))} blocking issue(s), {len(set(warnings))} warning(s)")
        return 1

    print(f"PASS: 0 blocking issues, {len(set(warnings))} warning(s)")
    print("Warnings require human review; PASS does not prove factual correctness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
