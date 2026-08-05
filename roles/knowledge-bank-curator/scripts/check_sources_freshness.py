#!/usr/bin/env python3
"""Compare canonical experience sources with the derived knowledge-bank indexes.

The script answers one question: are the bank indexes still current with respect to the
sources they were built from?

It takes every path as an explicit command-line argument. It never reads user context,
rule files, or contracts -- the calling agent resolves those and passes the results in.

Per-source problems are reported as a status, never as a crash: a source may be missing,
or present but unreadable (permission denied, or a placeholder stub left behind by
cloud-synced storage whose real content has been evicted). Content length is probed, not
just the modification time, because an evicted stub keeps a plausible mtime.

Exit codes:
    0  fresh            -- every index is newer than every readable source and carries
                          its source-metadata heading
    1  refresh-required -- at least one index is missing, stale, or lacks the heading
    3  unknown          -- no index problem found, but at least one source is missing or
                          unreadable, so freshness cannot be decided
    2  is reserved by the argument parser for usage errors.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

EXIT_FRESH = 0
EXIT_REFRESH_REQUIRED = 1
EXIT_UNKNOWN = 3

DEFAULT_METADATA_HEADING = "## Source Metadata"
DEFAULT_PROBE_BYTES = 1024
DEFAULT_HEAD_BYTES = 4096


@dataclass
class Entry:
    """One inspected path: a canonical source or a derived index."""

    path: Path
    kind: str  # "source" | "index"
    status: str  # "ok" | "missing" | "unreadable" | "stale"
    mtime: float | None = None
    size: int | None = None
    detail: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "path": str(self.path),
            "kind": self.kind,
            "status": self.status,
            "mtime": iso(self.mtime),
            "size": self.size,
        }
        if self.detail:
            payload["detail"] = self.detail
        payload.update(self.extra)
        return payload


def iso(mtime: float | None) -> str | None:
    """Local ISO-8601 timestamp for a POSIX mtime, or None."""
    if mtime is None:
        return None
    return datetime.fromtimestamp(mtime).astimezone().isoformat(timespec="seconds")


def probe(path: Path, probe_bytes: int) -> tuple[int, str]:
    """Read up to probe_bytes from a file. Returns (bytes_read, error-detail)."""
    try:
        with path.open("rb") as handle:
            return len(handle.read(probe_bytes)), ""
    except OSError as exc:  # permission denied, evicted placeholder, I/O error
        return 0, f"{type(exc).__name__}: {exc.strerror or exc}"


def newest_file(directory: Path) -> tuple[Path | None, int]:
    """Newest regular file under a directory (recursively) and the file count.

    Dot-prefixed files and directories are skipped: they are sync/state metadata, not
    candidate evidence.
    """
    newest: Path | None = None
    newest_mtime = float("-inf")
    count = 0
    try:
        candidates = sorted(directory.rglob("*"))
    except OSError:
        return None, 0
    for candidate in candidates:
        if any(part.startswith(".") for part in candidate.relative_to(directory).parts):
            continue
        try:
            if not candidate.is_file():
                continue
            mtime = candidate.stat().st_mtime
        except OSError:
            continue
        count += 1
        if mtime > newest_mtime:
            newest, newest_mtime = candidate, mtime
    return newest, count


def inspect_source(raw: str, probe_bytes: int) -> Entry:
    path = Path(raw).expanduser()

    if not path.exists():
        return Entry(path, "source", "missing", detail="path does not exist")

    if path.is_dir():
        newest, count = newest_file(path)
        if newest is None:
            return Entry(
                path,
                "source",
                "unreadable",
                detail="directory holds no readable regular files",
                extra={"files": count},
            )
        read, error = probe(newest, probe_bytes)
        stat = newest.stat()
        if read == 0:
            return Entry(
                path,
                "source",
                "unreadable",
                mtime=stat.st_mtime,
                size=stat.st_size,
                detail=error or f"newest file `{newest}` returned no content",
                extra={"files": count, "newest_file": str(newest)},
            )
        return Entry(
            path,
            "source",
            "ok",
            mtime=stat.st_mtime,
            size=stat.st_size,
            extra={"files": count, "newest_file": str(newest)},
        )

    try:
        stat = path.stat()
    except OSError as exc:
        return Entry(path, "source", "unreadable", detail=f"stat failed: {exc.strerror or exc}")

    read, error = probe(path, probe_bytes)
    if read == 0:
        return Entry(
            path,
            "source",
            "unreadable",
            mtime=stat.st_mtime,
            size=stat.st_size,
            detail=error or "no content could be read (empty file or evicted placeholder)",
        )
    return Entry(path, "source", "ok", mtime=stat.st_mtime, size=stat.st_size)


def inspect_index(
    raw: str,
    newest_source_mtime: float | None,
    heading: str,
    head_bytes: int,
) -> Entry:
    path = Path(raw).expanduser()

    if not path.exists():
        return Entry(path, "index", "missing", detail="index has never been built")

    try:
        stat = path.stat()
    except OSError as exc:
        return Entry(path, "index", "unreadable", detail=f"stat failed: {exc.strerror or exc}")

    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            head = handle.read(head_bytes)
    except OSError as exc:
        return Entry(
            path,
            "index",
            "unreadable",
            mtime=stat.st_mtime,
            size=stat.st_size,
            detail=f"read failed: {exc.strerror or exc}",
        )

    metadata = heading in head
    stale = newest_source_mtime is not None and stat.st_mtime < newest_source_mtime

    if stale:
        status, detail = "stale", "older than the newest readable source"
    elif not metadata:
        status, detail = "stale", f"no `{heading}` block in the first {head_bytes} bytes"
    else:
        status, detail = "ok", ""

    return Entry(
        path,
        "index",
        status,
        mtime=stat.st_mtime,
        size=stat.st_size,
        detail=detail,
        extra={"source_metadata": "present" if metadata else "absent"},
    )


def render_markdown(sources: list[Entry], indexes: list[Entry], newest: Entry | None, verdict: str) -> str:
    lines = ["# Source freshness check", ""]

    lines.append("## Sources")
    if not sources:
        lines.append("- none passed; freshness cannot be decided from file timestamps alone")
    for entry in sources:
        bits = [f"- `{entry.path}`: **{entry.status}**"]
        if entry.mtime is not None:
            bits.append(f"mtime {iso(entry.mtime)}")
        if "files" in entry.extra:
            bits.append(f"{entry.extra['files']} file(s)")
        if entry.detail:
            bits.append(entry.detail)
        lines.append("; ".join(bits))
    if newest is not None:
        lines += ["", f"Newest readable source: `{newest.path}` at {iso(newest.mtime)}"]

    lines += ["", "## Derived indexes"]
    for entry in indexes:
        bits = [f"- `{entry.path}`: **{entry.status}**"]
        if entry.mtime is not None:
            bits.append(f"mtime {iso(entry.mtime)}")
        if "source_metadata" in entry.extra:
            bits.append(f"source metadata {entry.extra['source_metadata']}")
        if entry.detail:
            bits.append(entry.detail)
        lines.append("; ".join(bits))

    lines += ["", f"## Verdict: {verdict}", ""]
    if verdict == "refresh-required":
        lines.append("At least one index is missing, stale, or has no source-metadata block.")
    elif verdict == "unknown":
        lines.append(
            "No index problem was found, but a source is missing or unreadable: the calling "
            "capability decides the fallback (another reader, or a question to the user)."
        )
    else:
        lines.append("Every index is newer than every readable source and carries its metadata block.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check_sources_freshness.py",
        description=(
            "Compare canonical experience sources with derived knowledge-bank indexes. "
            "Every path is an explicit argument; the script reads no context or rule files."
        ),
        epilog="Exit codes: 0 fresh, 1 refresh-required, 3 unknown (source missing or unreadable).",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="PATH",
        help="A canonical experience source (file or directory). Repeat per source.",
    )
    parser.add_argument(
        "--index",
        action="append",
        default=[],
        metavar="PATH",
        help="A derived bank index file. Repeat per index. At least one is required.",
    )
    parser.add_argument(
        "--metadata-heading",
        default=DEFAULT_METADATA_HEADING,
        help=f"Heading that marks an index's source-metadata block (default: {DEFAULT_METADATA_HEADING!r}).",
    )
    parser.add_argument(
        "--probe-bytes",
        type=int,
        default=DEFAULT_PROBE_BYTES,
        help=(
            "How many bytes to read from a source to prove it has content "
            f"(default: {DEFAULT_PROBE_BYTES}). Guards against evicted cloud placeholders."
        ),
    )
    parser.add_argument(
        "--head-bytes",
        type=int,
        default=DEFAULT_HEAD_BYTES,
        help=f"How many bytes of an index to scan for the metadata heading (default: {DEFAULT_HEAD_BYTES}).",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Report format (default: markdown).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.index:
        parser.error("at least one --index is required")
    if args.probe_bytes < 1 or args.head_bytes < 1:
        parser.error("--probe-bytes and --head-bytes must be positive")

    sources = [inspect_source(raw, args.probe_bytes) for raw in args.source]
    readable = [entry for entry in sources if entry.status == "ok" and entry.mtime is not None]
    newest = max(readable, key=lambda entry: entry.mtime or 0.0) if readable else None
    newest_mtime = newest.mtime if newest else None

    indexes = [
        inspect_index(raw, newest_mtime, args.metadata_heading, args.head_bytes)
        for raw in args.index
    ]

    index_problem = any(entry.status != "ok" for entry in indexes)
    source_problem = any(entry.status != "ok" for entry in sources) or not sources

    if index_problem:
        verdict, code = "refresh-required", EXIT_REFRESH_REQUIRED
    elif source_problem:
        verdict, code = "unknown", EXIT_UNKNOWN
    else:
        verdict, code = "fresh", EXIT_FRESH

    if args.format == "json":
        report = {
            "verdict": verdict,
            "exit_code": code,
            "newest_source": str(newest.path) if newest else None,
            "newest_source_mtime": iso(newest_mtime),
            "sources": [entry.as_dict() for entry in sources],
            "indexes": [entry.as_dict() for entry in indexes],
        }
        print(json.dumps(report, indent=2))
    else:
        print(render_markdown(sources, indexes, newest, verdict))

    return code


if __name__ == "__main__":
    sys.exit(main())
