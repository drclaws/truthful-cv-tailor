#!/usr/bin/env python3
"""Check whether derived CV evidence indexes are stale versus source files."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


DEFAULT_INDEXES = [
    Path("data/master/experience_bank.md"),
    Path("data/master/projects.md"),
    Path("data/master/skills_matrix.md"),
]


def fmt_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(timespec="seconds")


def has_source_metadata(path: Path) -> bool:
    if not path.exists():
        return False
    head = path.read_text(encoding="utf-8", errors="replace")[:1000]
    return "## Source Metadata" in head


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare canonical source file mtimes with derived CV evidence indexes."
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Canonical source file path. Repeat for multiple files.",
    )
    parser.add_argument(
        "--index",
        action="append",
        default=[],
        help="Derived index file path. Defaults to experience_bank, projects, and skills_matrix.",
    )
    args = parser.parse_args()

    sources = [Path(p) for p in args.source]
    indexes = [Path(p) for p in args.index] if args.index else DEFAULT_INDEXES

    print("# Source Freshness Check")
    print()

    existing_sources = [p for p in sources if p.exists()]
    missing_sources = [p for p in sources if not p.exists()]

    if missing_sources:
        print("## Missing sources")
        for path in missing_sources:
            print(f"- `{path}`")
        print()

    if not existing_sources:
        print("No source files were provided or found. For external non-file inputs, use `00_source_audit.md`.")
        newest_source_mtime = None
    else:
        newest_source = max(existing_sources, key=lambda p: p.stat().st_mtime)
        newest_source_mtime = newest_source.stat().st_mtime
        print("## Sources")
        for path in sorted(existing_sources):
            print(f"- `{path}`: {fmt_mtime(path)}")
        print()
        print(f"Newest source: `{newest_source}` at {fmt_mtime(newest_source)}")
        print()

    print("## Derived indexes")
    exit_code = 0
    for index in indexes:
        if not index.exists():
            print(f"- `{index}`: MISSING")
            exit_code = 1
            continue

        metadata = "present" if has_source_metadata(index) else "missing"
        stale = newest_source_mtime is not None and index.stat().st_mtime < newest_source_mtime
        status = "STALE" if stale else "fresh-or-unchecked"
        if stale or metadata == "missing":
            exit_code = 1
        print(f"- `{index}`: {fmt_mtime(index)}; metadata {metadata}; {status}")

    print()
    if exit_code:
        print("Verdict: refresh required before evidence mapping.")
    else:
        print("Verdict: no file-mtime refresh required.")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
