#!/usr/bin/env python3
"""Probe the concrete dependencies named on the command line.

Used by `setup-master.check-environment`. The agent aggregates the `## Dependencies`
sections of the shipped and registered skills and passes the concrete tool names,
minimum versions and locations here as EXPLICIT ARGUMENTS.

This script never discovers work for itself: it does not read SKILL.md files, user
context, rules files, contracts, or any repository file. It checks exactly what it is
told to check and reports a status for each item.

A missing tool is a reported status, never a crash: the exit code is 0 whenever the
arguments were valid, so the caller reads the report rather than the exit code.

Examples (the names are illustrations of what a skill might declare):

    check_environment.py --tool python3@3.10 --tool pdflatex --json
    check_environment.py --tool pdftotext --version-arg pdftotext=-v
    check_environment.py --path ./some/registered/skill --no-version-probe
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "check-environment/1.0"

# Tried in order until one of them yields something version-shaped.
DEFAULT_VERSION_ARGS = ("--version", "-version", "-V", "-v")

VERSION_RE = re.compile(r"(\d+(?:\.\d+)*)")

STATUS_BOUND = "bound"
STATUS_UNBOUND = "unbound"
STATUS_VERSION_MISMATCH = "version-mismatch"
STATUS_VERSION_UNKNOWN = "version-unknown"
STATUS_UNREADABLE = "unreadable"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="check_environment.py",
        description=(
            "Probe explicitly named tools and locations. Reads no skill, context or "
            "rule files: every item checked is passed as an argument."
        ),
        epilog=(
            "Exit code is 0 for any valid invocation, including one where nothing was "
            "found; 2 only for a usage error."
        ),
    )
    parser.add_argument(
        "--tool",
        action="append",
        default=[],
        metavar="NAME[@MIN_VERSION]",
        help=(
            "A concrete tool a skill declared. Append @MIN_VERSION to require a minimum, "
            "e.g. --tool python3@3.10. Repeatable."
        ),
    )
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        metavar="PATH",
        help=(
            "A location that must exist and be readable, e.g. a registered out-of-repo "
            "skill. Repeatable."
        ),
    )
    parser.add_argument(
        "--version-arg",
        action="append",
        default=[],
        metavar="NAME=ARG[,ARG...]",
        help=(
            "Override the version probe for one tool, e.g. --version-arg pdftotext=-v. "
            "Without it the defaults are tried in order: " + " ".join(DEFAULT_VERSION_ARGS) + "."
        ),
    )
    parser.add_argument(
        "--no-version-probe",
        action="store_true",
        help="Check presence only; never execute a discovered tool.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        metavar="SECONDS",
        help="Per-probe timeout in seconds (default: 10).",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit a machine-readable JSON report instead of the text table.",
    )
    args = parser.parse_args(argv)

    if not args.tool and not args.path:
        parser.error("nothing to check: pass at least one --tool or --path")
    if args.timeout <= 0:
        parser.error("--timeout must be greater than 0")

    overrides: dict[str, list[str]] = {}
    for raw in args.version_arg:
        name, sep, value = raw.partition("=")
        if not sep or not name.strip():
            parser.error(f"--version-arg expects NAME=ARG[,ARG...], got {raw!r}")
        probe = [part for part in value.split(",") if part]
        if not probe:
            parser.error(f"--version-arg {name!r} has no arguments")
        overrides[name.strip()] = probe
    args.version_overrides = overrides
    return args


def parse_version(text: str) -> tuple[int, ...] | None:
    match = VERSION_RE.search(text)
    if not match:
        return None
    try:
        return tuple(int(part) for part in match.group(1).split("."))
    except ValueError:  # pragma: no cover - the regex only matches digits
        return None


def compare_versions(found: tuple[int, ...], minimum: tuple[int, ...]) -> int:
    width = max(len(found), len(minimum))
    left = found + (0,) * (width - len(found))
    right = minimum + (0,) * (width - len(minimum))
    return (left > right) - (left < right)


def format_version(version: tuple[int, ...] | None) -> str | None:
    return ".".join(str(part) for part in version) if version else None


def probe_version(
    executable: str, probe_args: list[list[str]], timeout: float
) -> tuple[tuple[int, ...] | None, str | None]:
    """Return (version, detail). Never raises: any failure becomes a detail string."""
    last_detail: str | None = None
    for probe in probe_args:
        try:
            completed = subprocess.run(  # noqa: S603 - the caller named this executable
                [executable, *probe],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            last_detail = f"version probe {' '.join(probe)!r} timed out"
            continue
        except OSError as exc:
            last_detail = f"version probe {' '.join(probe)!r} failed: {exc.strerror or exc}"
            continue
        output = (completed.stdout or b"") + b"\n" + (completed.stderr or b"")
        version = parse_version(output.decode("utf-8", errors="replace"))
        if version is not None:
            return version, None
        last_detail = f"version probe {' '.join(probe)!r} produced no version string"
    return None, last_detail


def check_tool(spec: str, args: argparse.Namespace) -> dict[str, object]:
    name, sep, raw_minimum = spec.partition("@")
    name = name.strip()
    result: dict[str, object] = {
        "kind": "tool",
        "name": name,
        "min_version": raw_minimum.strip() or None if sep else None,
        "status": STATUS_UNBOUND,
        "location": None,
        "version": None,
        "detail": "",
    }

    if not name:
        result["status"] = STATUS_UNBOUND
        result["detail"] = "empty tool name"
        return result

    minimum = parse_version(raw_minimum) if sep and raw_minimum.strip() else None
    if sep and raw_minimum.strip() and minimum is None:
        result["detail"] = f"unreadable minimum version {raw_minimum.strip()!r}; presence checked only"

    try:
        location = shutil.which(name)
    except OSError as exc:  # pragma: no cover - defensive
        result["detail"] = f"lookup failed: {exc.strerror or exc}"
        return result

    if location is None:
        result["detail"] = "not found on PATH"
        return result

    result["location"] = location
    result["status"] = STATUS_BOUND

    if args.no_version_probe:
        result["detail"] = "presence only (version probe disabled)"
        if minimum is not None:
            result["status"] = STATUS_VERSION_UNKNOWN
            result["detail"] = "minimum version declared but version probe disabled"
        return result

    probe_args = [args.version_overrides[name]] if name in args.version_overrides else [
        [arg] for arg in DEFAULT_VERSION_ARGS
    ]
    version, detail = probe_version(location, probe_args, args.timeout)
    result["version"] = format_version(version)

    if version is None:
        if minimum is not None:
            result["status"] = STATUS_VERSION_UNKNOWN
        result["detail"] = detail or "version could not be determined"
        return result

    if minimum is not None and compare_versions(version, minimum) < 0:
        result["status"] = STATUS_VERSION_MISMATCH
        result["detail"] = f"found {format_version(version)}, minimum {format_version(minimum)}"
    return result


def check_path(raw_path: str) -> dict[str, object]:
    path = Path(raw_path).expanduser()
    result: dict[str, object] = {
        "kind": "path",
        "name": raw_path,
        "min_version": None,
        "status": STATUS_UNBOUND,
        "location": None,
        "version": None,
        "detail": "",
    }
    try:
        exists = path.exists()
    except OSError as exc:
        result["status"] = STATUS_UNREADABLE
        result["detail"] = f"cannot be inspected: {exc.strerror or exc}"
        return result

    if not exists:
        result["detail"] = "does not exist"
        return result

    try:
        result["location"] = str(path.resolve())
    except OSError:
        result["location"] = str(path)
    if not os.access(path, os.R_OK):
        result["status"] = STATUS_UNREADABLE
        result["detail"] = "exists but is not readable"
        return result

    result["status"] = STATUS_BOUND
    result["detail"] = "directory" if path.is_dir() else "file"
    return result


def render_text(report: dict[str, object]) -> str:
    results: list[dict[str, object]] = report["results"]  # type: ignore[assignment]
    headers = ("STATUS", "KIND", "NAME", "DETAIL")
    rows = []
    for item in results:
        detail_parts = []
        if item["version"]:
            detail_parts.append(f"version {item['version']}")
        if item["location"]:
            detail_parts.append(f"at {item['location']}")
        if item["detail"]:
            detail_parts.append(str(item["detail"]))
        rows.append(
            (
                str(item["status"]),
                str(item["kind"]),
                str(item["name"]) + (f"@{item['min_version']}" if item["min_version"] else ""),
                "; ".join(detail_parts),
            )
        )

    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) if rows else len(headers[i]) for i in range(3)]
    lines = ["  ".join(headers[i].ljust(widths[i]) for i in range(3)) + "  " + headers[3]]
    for row in rows:
        lines.append("  ".join(row[i].ljust(widths[i]) for i in range(3)) + "  " + row[3])

    summary: dict[str, int] = report["summary"]  # type: ignore[assignment]
    lines.append("")
    lines.append(", ".join(f"{key}: {value}" for key, value in sorted(summary.items())))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    results = [check_tool(spec, args) for spec in args.tool]
    results.extend(check_path(raw) for raw in args.path)

    summary: dict[str, int] = {}
    for item in results:
        status = str(item["status"])
        summary[status] = summary.get(status, 0) + 1

    report = {
        "schema": SCHEMA,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "results": results,
        "summary": summary,
    }

    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=False))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
