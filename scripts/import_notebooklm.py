#!/usr/bin/env python3
"""Safely import marker-delimited Markdown candidates into a Shared Brain root."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path, PurePosixPath

FILE_RE = re.compile(r"^<!-- FILE: ([^>]+) -->$")
END_MARKER = "<!-- END FILE -->"
ALLOWED_ROOTS = {"brain", "sources"}
BANNED_PARTS = {"archive", "vault", "raw", "inbox", ".git", "secrets"}
MAX_FILE_CHARS = 1_200_000
MAX_FILES = 500


def safe_relative_path(raw: str) -> PurePosixPath:
    value = raw.strip()
    if not value or "\\" in value:
        raise ValueError(f"invalid path syntax: {raw!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ValueError(f"absolute/traversal path rejected: {raw!r}")
    if len(path.parts) < 2 or path.parts[0] not in ALLOWED_ROOTS:
        raise ValueError(f"path must begin with brain/ or sources/: {raw!r}")
    if any(part.lower() in BANNED_PARTS for part in path.parts):
        raise ValueError(f"sensitive path rejected: {raw!r}")
    if path.suffix.lower() != ".md":
        raise ValueError(f"only Markdown files are accepted: {raw!r}")
    return path


def parse_export(text: str) -> list[tuple[PurePosixPath, str]]:
    blocks: list[tuple[PurePosixPath, str]] = []
    seen: set[PurePosixPath] = set()
    current_path: PurePosixPath | None = None
    current_lines: list[str] = []

    for lineno, line in enumerate(text.splitlines(), start=1):
        match = FILE_RE.match(line)
        if match:
            if current_path is not None:
                raise ValueError(f"line {lineno}: nested FILE marker before END FILE")
            current_path = safe_relative_path(match.group(1))
            if current_path in seen:
                raise ValueError(f"line {lineno}: duplicate path {current_path}")
            current_lines = []
            continue

        if line == END_MARKER:
            if current_path is None:
                raise ValueError(f"line {lineno}: END FILE without FILE marker")
            content = "\n".join(current_lines).strip() + "\n"
            if len(content) > MAX_FILE_CHARS:
                raise ValueError(f"{current_path}: exceeds {MAX_FILE_CHARS:,} characters")
            blocks.append((current_path, content))
            seen.add(current_path)
            current_path = None
            current_lines = []
            if len(blocks) > MAX_FILES:
                raise ValueError(f"export contains more than {MAX_FILES} files")
            continue

        if current_path is not None:
            current_lines.append(line)
        elif line.strip():
            raise ValueError(
                f"line {lineno}: non-empty text outside FILE blocks; remove model commentary"
            )

    if current_path is not None:
        raise ValueError(f"missing END FILE for {current_path}")
    if not blocks:
        raise ValueError("no FILE blocks found")
    return blocks


def destination(root: Path, relative: PurePosixPath) -> Path:
    root_resolved = root.resolve()
    dest = root_resolved.joinpath(*relative.parts).resolve()
    try:
        dest.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"destination escaped root: {relative}") from exc
    return dest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("export", type=Path, help="NotebookLM/LLM marker-format export")
    parser.add_argument("--root", type=Path, required=True, help="private Shared Brain root")
    parser.add_argument("--overwrite", action="store_true", help="allow replacing existing files")
    parser.add_argument("--dry-run", action="store_true", help="validate and print without writing")
    args = parser.parse_args()

    try:
        text = args.export.read_text(encoding="utf-8")
        blocks = parse_export(text)
        args.root.mkdir(parents=True, exist_ok=True)

        planned: list[tuple[PurePosixPath, Path, str]] = []
        for rel, content in blocks:
            dest = destination(args.root, rel)
            if dest.exists() and not args.overwrite:
                raise ValueError(f"refusing to overwrite existing file: {rel}; review first or pass --overwrite")
            planned.append((rel, dest, content))

        for rel, dest, content in planned:
            print(f"{'WOULD WRITE' if args.dry_run else 'WRITE'} {rel} ({len(content):,} chars)")
            if not args.dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding="utf-8", newline="\n")

        print(f"OK: {len(planned)} candidate file(s) {'validated' if args.dry_run else 'imported'}")
        print("Review the generated files, then run validate_brain.py before committing.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
