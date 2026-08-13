#!/usr/bin/env python3
"""Check that an exported CV PDF still extracts as text.

Runs the text-extraction half of the render gate sequence of the `render-cv-pdf`
tool: extract the PDF twice — plain reading order and layout-preserving —
and report whether the required headings and contact signals survived in both.

Everything the script checks is passed as an EXPLICIT ARGUMENT. It reads no
TOOL.md, no template policy, no user context and no rules file, and it assumes
no repository layout: the agent resolves the values and hands them over.

The extraction binary is discovered on PATH with `shutil.which` — no hardcoded
tool locations. When it is not available the script reports the check as SKIPPED
and exits 3; a missing dependency is a recorded outcome, not a crash.

Reading both extracts by eye is still part of the gate: this script reports
signals, it cannot see incoherent cross-column interleaving.

Exit codes:
    0  pass     — every required signal was found in both extracts
    1  fail     — a required signal is missing, or an extract came back empty
    2  usage    — bad arguments
    3  skipped  — the extraction binary is unavailable or could not be executed
    4  input    — the PDF does not exist or cannot be read

Examples:

    pdf_text_check.py <export>.pdf
    pdf_text_check.py <export>.pdf --json --excerpt 0
    pdf_text_check.py <export>.pdf --heading summary --heading experience
    pdf_text_check.py <export>.pdf --pdftotext /path/to/pdftotext
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

SCHEMA = "pdf-text-check/1.0"

DEFAULT_HEADINGS = ("summary", "skills", "experience", "education")
DEFAULT_REQUIRED_CONTACTS = {
    "email": r"\bemail\s*:\s*[\w.+-]+@[\w.-]+\.\w+",
    "phone": r"\bphone\s*:\s*(\+\d{1,3}[\s-]?)?[\(\d][\d\s\-\(\)]{7,}",
}
DEFAULT_OPTIONAL_CONTACTS = {
    "linkedin": r"linkedin\.com",
}

STATUS_PASS = "pass"
STATUS_FAIL = "fail"
STATUS_SKIPPED = "skipped"
STATUS_ERROR = "error"

EXIT_CODES = {STATUS_PASS: 0, STATUS_FAIL: 1, STATUS_SKIPPED: 3, STATUS_ERROR: 4}


def parse_signal_options(
    raw_values: list[str], option: str, parser: argparse.ArgumentParser
) -> dict[str, str]:
    signals: dict[str, str] = {}
    for raw in raw_values:
        name, sep, pattern = raw.partition("=")
        if not sep or not name.strip() or not pattern:
            parser.error(f"{option} expects NAME=REGEX, got {raw!r}")
        try:
            re.compile(pattern)
        except re.error as exc:
            parser.error(f"{option} {name.strip()!r} has an invalid regex: {exc}")
        signals[name.strip()] = pattern
    return signals


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pdf_text_check.py",
        description=(
            "Extract an exported PDF twice (reading order and layout-preserving) and "
            "report whether the required headings and contact signals survived."
        ),
        epilog=(
            "Exit codes: 0 pass, 1 fail, 2 usage error, 3 skipped (extraction binary "
            "unavailable), 4 the PDF could not be read."
        ),
    )
    parser.add_argument("pdf", metavar="PDF", help="Path to the exported PDF to check.")
    parser.add_argument(
        "--pdftotext",
        default="pdftotext",
        metavar="NAME_OR_PATH",
        help=(
            "Extraction binary to use: a name looked up on PATH, or an explicit path. "
            "Default: pdftotext."
        ),
    )
    parser.add_argument(
        "--heading",
        action="append",
        default=[],
        metavar="TEXT",
        help=(
            "A heading that must appear in both extracts (case-insensitive). Repeatable. "
            "Without it the defaults are used: " + ", ".join(DEFAULT_HEADINGS) + "."
        ),
    )
    parser.add_argument(
        "--no-default-headings",
        action="store_true",
        help="Do not fall back to the default heading set when --heading is omitted.",
    )
    parser.add_argument(
        "--contact",
        action="append",
        default=[],
        metavar="NAME=REGEX",
        help=(
            "A required contact signal, as a name and a regex. Repeatable. Replaces the "
            "default set (" + ", ".join(sorted(DEFAULT_REQUIRED_CONTACTS)) + ")."
        ),
    )
    parser.add_argument(
        "--optional-contact",
        action="append",
        default=[],
        metavar="NAME=REGEX",
        help=(
            "A signal that is reported but never fails the check. Repeatable. Replaces "
            "the default set (" + ", ".join(sorted(DEFAULT_OPTIONAL_CONTACTS)) + ")."
        ),
    )
    parser.add_argument(
        "--excerpt",
        type=int,
        default=1000,
        metavar="CHARS",
        help="Characters of each extract to print for eyeballing (0 disables; default: 1000).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        metavar="SECONDS",
        help="Per-extraction timeout in seconds (default: 60).",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit a machine-readable JSON report instead of the text report.",
    )
    args = parser.parse_args(argv)

    if args.excerpt < 0:
        parser.error("--excerpt must not be negative")
    if args.timeout <= 0:
        parser.error("--timeout must be greater than 0")

    headings = [item.strip() for item in args.heading if item.strip()]
    if not headings and not args.no_default_headings:
        headings = list(DEFAULT_HEADINGS)
    args.headings = headings

    args.required_contacts = (
        parse_signal_options(args.contact, "--contact", parser)
        if args.contact
        else dict(DEFAULT_REQUIRED_CONTACTS)
    )
    args.optional_contacts = (
        parse_signal_options(args.optional_contact, "--optional-contact", parser)
        if args.optional_contact
        else dict(DEFAULT_OPTIONAL_CONTACTS)
    )
    return args


def resolve_binary(spec: str) -> str | None:
    """Resolve an extraction binary by name on PATH, or as an explicit path."""
    separators = [os.sep] + ([os.altsep] if os.altsep else [])
    if any(separator in spec for separator in separators):
        candidate = Path(spec).expanduser()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
        return None
    return shutil.which(spec)


def extract(
    binary: str, pdf: Path, extra_args: list[str], timeout: float
) -> tuple[str | None, str]:
    """Return (text, detail). text is None when the extraction could not be run."""
    command = [binary, *extra_args, str(pdf), "-"]
    try:
        completed = subprocess.run(  # noqa: S603 - the caller named this executable
            command,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, f"timed out after {timeout:g}s"
    except OSError as exc:
        return None, f"could not be executed: {exc.strerror or exc}"
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        return None, f"exit {completed.returncode}: {detail or 'no stderr output'}"
    return completed.stdout.decode("utf-8", errors="replace"), ""


def inspect(text: str, args: argparse.Namespace) -> dict[str, object]:
    lower = text.lower()
    headings = {heading: heading.lower() in lower for heading in args.headings}
    required = {
        name: bool(re.search(pattern, text, re.IGNORECASE))
        for name, pattern in args.required_contacts.items()
    }
    optional = {
        name: bool(re.search(pattern, text, re.IGNORECASE))
        for name, pattern in args.optional_contacts.items()
    }
    missing = [name for name, found in headings.items() if not found]
    missing += [name for name, found in required.items() if not found]
    return {
        "characters": len(text),
        "empty": not text.strip(),
        "headings": headings,
        "required_contacts": required,
        "optional_contacts": optional,
        "missing": missing,
    }


def render_text(
    report: dict[str, object], args: argparse.Namespace, extracts: dict[str, str]
) -> str:
    lines = ["# PDF text extraction check", ""]
    lines.append(f"PDF: {report['pdf']}")
    lines.append(f"Extractor: {report['extractor'] or 'not found'}")
    lines.append(f"Status: {report['status']}")
    for note in report["notes"]:  # type: ignore[union-attr]
        lines.append(f"Note: {note}")

    for label, result in report["extractions"].items():  # type: ignore[union-attr]
        lines.append("")
        lines.append(f"## {label} extraction")
        if result.get("detail"):
            lines.append(f"- did not run: {result['detail']}")
            continue
        lines.append(f"- extracted characters: {result['characters']}")
        for heading, found in result["headings"].items():
            lines.append(f"- heading `{heading}`: {'yes' if found else 'NO'}")
        for name, found in result["required_contacts"].items():
            lines.append(f"- required signal `{name}`: {'yes' if found else 'NO'}")
        for name, found in result["optional_contacts"].items():
            lines.append(f"- optional signal `{name}`: {'yes' if found else 'no'}")
        if args.excerpt and extracts.get(label):
            lines.append("")
            lines.append(f"First {args.excerpt} characters:")
            lines.append("```text")
            lines.append(extracts[label][: args.excerpt])
            lines.append("```")

    if extracts:
        lines.append("")
        lines.append(
            "Read both extracts before export: this check reports signals, it cannot see "
            "incoherent cross-column interleaving or lost side-column text."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    pdf = Path(args.pdf).expanduser()

    report: dict[str, object] = {
        "schema": SCHEMA,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pdf": str(pdf),
        "extractor": None,
        "status": STATUS_PASS,
        "notes": [],
        "extractions": {},
    }
    notes: list[str] = report["notes"]  # type: ignore[assignment]
    extractions: dict[str, dict[str, object]] = report["extractions"]  # type: ignore[assignment]
    extracts: dict[str, str] = {}

    def emit(status: str) -> int:
        report["status"] = status
        if args.as_json:
            print(json.dumps(report, indent=2, sort_keys=False))
        else:
            print(render_text(report, args, extracts))
        return EXIT_CODES[status]

    if not pdf.is_file():
        notes.append(f"{pdf} does not exist or is not a file")
        return emit(STATUS_ERROR)
    if not os.access(pdf, os.R_OK):
        notes.append(f"{pdf} exists but is not readable")
        return emit(STATUS_ERROR)

    binary = resolve_binary(args.pdftotext)
    if binary is None:
        notes.append(
            f"extraction binary {args.pdftotext!r} was not found; install a "
            "Poppler-compatible toolchain, or pass --pdftotext with an explicit path. "
            "The extraction gate did not run."
        )
        return emit(STATUS_SKIPPED)
    report["extractor"] = binary

    for label, extra_args in (("normal", []), ("layout", ["-layout"])):
        text, detail = extract(binary, pdf, extra_args, args.timeout)
        if text is None:
            notes.append(f"{label} extraction did not run: {detail}")
            extractions[label] = {"detail": detail}
            continue
        extracts[label] = text
        extractions[label] = inspect(text, args)

    if not extracts:
        notes.append("neither extraction could be run; the gate was not evaluated")
        return emit(STATUS_SKIPPED)

    failed = False
    for label, result in extractions.items():
        if result.get("detail"):
            failed = True
            continue
        if result["empty"]:
            notes.append(
                f"{label} extraction returned no text: is the PDF scanned or malformed?"
            )
            failed = True
        if result["missing"]:
            missing = ", ".join(str(item) for item in result["missing"])  # type: ignore[union-attr]
            notes.append(f"{label} extraction is missing: {missing}")
            failed = True

    return emit(STATUS_FAIL if failed else STATUS_PASS)


if __name__ == "__main__":
    sys.exit(main())
