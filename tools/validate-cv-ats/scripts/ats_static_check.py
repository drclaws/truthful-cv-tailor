#!/usr/bin/env python3
"""Static ATS readability signals for a candidate document.

Reads one plain-text or markdown document and reports machine-checkable signals:
which standard headings are present, whether contact facts exist as text, which
formatting-risk patterns appear, bullet statistics, and a crude 0-100 score.

The output is EVIDENCE for the ATS check spec (../TOOL.md), never a verdict: a
pattern hit is a pointer to inspect, and the score is a measurement under this
script's own formula.

All paths are explicit command-line arguments; nothing is derived from
repository layout.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STANDARD_HEADINGS = [
    "summary",
    "professional summary",
    "skills",
    "core skills",
    "experience",
    "professional experience",
    "projects",
    "selected projects",
    "education",
    "certifications",
    "languages",
]

RISK_PATTERNS = {
    "markdown_table": r"\|.+\|",
    "html_tags": r"<[^>]+>",
    "icons_or_symbols": r"[★●◆■✓➤→]",
    "skill_bars": r"(advanced|expert|beginner)\s*[:\-]\s*(\d+%|[█▇▆▅▄▃▂▁]+)",
    "image_reference": r"!\[.*?\]\(.*?\)",
    "placeholder": r"TODO|PLACEHOLDER|\{\{.+?\}\}",
}

DEFAULT_LONG_BULLET_CHARS = 240


def read_text(path: Path) -> str:
    """Read a text file, tolerating imperfect encodings rather than crashing."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def check_headings(text: str) -> list[str]:
    lower = text.lower()
    return [h for h in STANDARD_HEADINGS if h in lower]


def check_risks(text: str) -> list[str]:
    return [
        name
        for name, pattern in RISK_PATTERNS.items()
        if re.search(pattern, text, re.IGNORECASE)
    ]


def check_contact(text: str) -> dict[str, bool]:
    email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    linkedin = "linkedin.com" in text.lower()
    phone = re.search(r"(\+\d{1,3}[\s\-]?)?[\(\d][\d\s\-\(\)]{7,}", text)
    return {"email": bool(email), "phone": bool(phone), "linkedin": linkedin}


def check_bullets(text: str, long_bullet_chars: int) -> dict[str, int]:
    bullets = [
        line for line in text.splitlines() if line.strip().startswith(("-", "*"))
    ]
    long_bullets = [b for b in bullets if len(b) > long_bullet_chars]
    return {"bullet_count": len(bullets), "long_bullets": len(long_bullets)}


def compute_score(
    headings: list[str], risks: list[str], contact: dict[str, bool], bullets: dict[str, int]
) -> int:
    score = 100
    if len(headings) < 4:
        score -= 15
    if risks:
        score -= 10 * len(risks)
    if not contact["email"]:
        score -= 20
    if not contact["phone"]:
        score -= 10
    if bullets["long_bullets"] > 3:
        score -= 10
    return max(score, 0)


def render_markdown(result: dict) -> str:
    lines = ["# Static ATS Check", ""]
    lines.append(f"Document: {result['document']}")
    lines.append("")
    lines.append(f"Score: {result['score']}/100")
    lines.append("")
    lines.append("## Headings found")
    if result["headings"]:
        lines += [f"- {h}" for h in result["headings"]]
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Contact info")
    lines += [
        f"- {key}: {'yes' if value else 'no'}" for key, value in result["contact"].items()
    ]
    lines.append("")
    lines.append("## Formatting risks")
    if result["risks"]:
        lines += [f"- {r}" for r in result["risks"]]
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Bullets")
    lines.append(f"- total bullets: {result['bullets']['bullet_count']}")
    lines.append(
        f"- long bullets (> {result['long_bullet_chars']} chars): "
        f"{result['bullets']['long_bullets']}"
    )
    lines.append("")
    lines.append(
        "Risk patterns are candidates to inspect in the document, not findings by "
        "themselves; the score is this script's own measurement."
    )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ats_static_check.py",
        description=(
            "Report static ATS readability signals for one candidate document "
            "(markdown, or text extracted from a rendered file)."
        ),
        epilog=(
            "Examples:\n"
            "  python3 ats_static_check.py --cv path/to/final_cv.md\n"
            "  python3 ats_static_check.py --cv path/to/extracted.txt --json "
            "--out path/to/capture.json\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--cv",
        required=True,
        type=Path,
        help="path to the document to inspect (required)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="write the report to this path instead of standard output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit JSON instead of markdown",
    )
    parser.add_argument(
        "--long-bullet-chars",
        type=int,
        default=DEFAULT_LONG_BULLET_CHARS,
        metavar="N",
        help=f"bullet length treated as long (default: {DEFAULT_LONG_BULLET_CHARS})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    cv_path = args.cv
    if not cv_path.is_file():
        print(f"error: document not found or not a file: {cv_path}", file=sys.stderr)
        return 2
    try:
        text = read_text(cv_path)
    except OSError as exc:
        print(f"error: cannot read {cv_path}: {exc}", file=sys.stderr)
        return 2

    if not text.strip():
        print(f"warning: {cv_path} is empty", file=sys.stderr)

    headings = check_headings(text)
    risks = check_risks(text)
    contact = check_contact(text)
    bullets = check_bullets(text, args.long_bullet_chars)

    result = {
        "document": str(cv_path),
        "score": compute_score(headings, risks, contact, bullets),
        "headings": headings,
        "contact": contact,
        "risks": risks,
        "bullets": bullets,
        "long_bullet_chars": args.long_bullet_chars,
    }

    report = (
        json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.json
        else render_markdown(result)
    )

    if args.out:
        try:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(report, encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot write {args.out}: {exc}", file=sys.stderr)
            return 2
        print(f"written: {args.out}")
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
