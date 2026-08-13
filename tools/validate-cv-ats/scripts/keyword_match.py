#!/usr/bin/env python3
"""Keyword coverage of a candidate document against the job side.

Compares the significant terms of a job-side text (the vacancy text, or the
keyword sets of a requirements profile) with the text of a candidate document,
and reports coverage, missing terms, weakly covered terms and possible
repetition. An optional must-have list is checked separately, phrase by phrase.

The output is EVIDENCE for the ATS check spec (../TOOL.md), never a verdict, and
never a licence to add a keyword the candidate's evidence does not support: an
uncovered term is either a real edit or a gap, and only the reviewing agent can
tell them apart.

All paths are explicit command-line arguments; nothing is derived from
repository layout.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

STOPWORDS = {
    "and", "or", "the", "a", "an", "to", "of", "in", "for", "with", "on", "by",
    "is", "are", "be", "as", "at", "from", "this", "that", "you", "we", "our",
    "your", "will", "can", "have", "has", "their", "they", "them", "it", "into",
    "using",
}

DEFAULT_TOP = 100
DEFAULT_LIST_LIMIT = 60
DEFAULT_WEAK_MAX_COUNT = 1
DEFAULT_OVERUSE_MIN_COUNT = 6
MIN_TERM_LENGTH = 3


def read_text(path: Path) -> str:
    """Read a text file, tolerating imperfect encodings rather than crashing."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def words(text: str) -> list[str]:
    """Tokenize, keeping tech punctuation (c++, c#, node.js) but not trailing dots
    or hyphens, so that "Kafka." and "Kafka" are the same term."""
    tokens = []
    for raw in re.findall(r"[A-Za-z][A-Za-z0-9\+\#\.\-]{1,}", text):
        token = re.sub(r"[.\-]+$", "", raw).lower()
        if len(token) > 1 and token not in STOPWORDS:
            tokens.append(token)
    return tokens


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def load_must_have(path: Path) -> list[str]:
    """One keyword or phrase per line; blank lines and '#' comments ignored."""
    entries = []
    for line in read_text(path).splitlines():
        item = line.strip()
        if item and not item.startswith("#"):
            entries.append(item)
    return entries


def count_phrase(phrase: str, normalized_cv: str) -> int:
    needle = normalize(phrase)
    if not needle:
        return 0
    return normalized_cv.count(needle)


def render_markdown(result: dict, list_limit: int) -> str:
    def bullets(items: list, fmt) -> list[str]:
        if not items:
            return ["- none"]
        shown = [fmt(i) for i in items[:list_limit]]
        if len(items) > list_limit:
            shown.append(f"- … and {len(items) - list_limit} more")
        return shown

    lines = ["# Keyword Match Report", ""]
    lines.append(f"Job side: {result['job']}")
    lines.append(f"Document: {result['document']}")
    lines.append("")
    lines.append(f"Keyword coverage: {result['coverage_percent']}%")
    lines.append(
        f"(terms considered: {result['terms_considered']}, "
        f"covered: {len(result['covered'])}, missing: {len(result['missing'])})"
    )
    lines.append("")
    lines.append("## Covered")
    lines += bullets(result["covered"], lambda t: f"- {t['term']} (x{t['count']})")
    lines.append("")
    lines.append("## Missing")
    lines += bullets(result["missing"], lambda t: f"- {t}")
    lines.append("")
    lines.append(f"## Weak (covered at most {result['weak_max_count']} time(s))")
    lines += bullets(result["weak"], lambda t: f"- {t['term']} (x{t['count']})")
    lines.append("")
    lines.append(f"## Possible overuse (>= {result['overuse_min_count']} mentions)")
    lines += bullets(result["overuse"], lambda t: f"- {t['term']} (x{t['count']})")

    if result["must_have"] is not None:
        mh = result["must_have"]
        lines.append("")
        lines.append(f"## Must-have coverage: {mh['coverage_percent']}%")
        lines.append("")
        lines.append("### Must-have covered")
        lines += bullets(mh["covered"], lambda t: f"- {t['term']} (x{t['count']})")
        lines.append("")
        lines.append("### Must-have missing")
        lines += bullets(mh["missing"], lambda t: f"- {t}")

    lines.append("")
    lines.append(
        "Counts are text occurrences only. A missing term is a real edit only when "
        "the candidate's evidence supports it; otherwise it is a gap."
    )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="keyword_match.py",
        description=(
            "Report keyword coverage of a candidate document against a job-side "
            "text, with optional must-have phrase checking."
        ),
        epilog=(
            "Examples:\n"
            "  python3 keyword_match.py --job path/to/job_description.md "
            "--cv path/to/final_cv.md\n"
            "  python3 keyword_match.py --job path/to/job_description.md "
            "--cv path/to/final_cv.md --must-have path/to/must_have.txt --json\n"
            "\n"
            "The must-have file holds one keyword or phrase per line; blank lines\n"
            "and lines starting with '#' are ignored.\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--job", required=True, type=Path, help="job-side text (required)")
    parser.add_argument(
        "--cv", required=True, type=Path, help="candidate document to inspect (required)"
    )
    parser.add_argument(
        "--must-have",
        type=Path,
        metavar="PATH",
        help="file with must-have keywords or phrases, one per line",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=DEFAULT_TOP,
        metavar="N",
        help=f"how many frequent job terms to consider (default: {DEFAULT_TOP})",
    )
    parser.add_argument(
        "--list-limit",
        type=int,
        default=DEFAULT_LIST_LIMIT,
        metavar="N",
        help=f"entries printed per list (default: {DEFAULT_LIST_LIMIT})",
    )
    parser.add_argument(
        "--weak-max-count",
        type=int,
        default=DEFAULT_WEAK_MAX_COUNT,
        metavar="N",
        help=(
            "a covered term with at most N mentions is reported as weak "
            f"(default: {DEFAULT_WEAK_MAX_COUNT})"
        ),
    )
    parser.add_argument(
        "--overuse-min-count",
        type=int,
        default=DEFAULT_OVERUSE_MIN_COUNT,
        metavar="N",
        help=(
            "a term with N or more mentions is reported as possible overuse "
            f"(default: {DEFAULT_OVERUSE_MIN_COUNT})"
        ),
    )
    parser.add_argument(
        "--out", type=Path, help="write the report to this path instead of standard output"
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    return parser


def load_input(path: Path, label: str) -> str | None:
    if not path.is_file():
        print(f"error: {label} not found or not a file: {path}", file=sys.stderr)
        return None
    try:
        return read_text(path)
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    job_text = load_input(args.job, "job-side text")
    cv_text = load_input(args.cv, "candidate document")
    if job_text is None or cv_text is None:
        return 2

    for path, text in ((args.job, job_text), (args.cv, cv_text)):
        if not text.strip():
            print(f"warning: {path} is empty", file=sys.stderr)

    job_terms = Counter(words(job_text))
    cv_terms = Counter(words(cv_text))
    normalized_cv = normalize(cv_text)

    considered = [
        term
        for term, _ in job_terms.most_common(max(args.top, 0))
        if len(term) >= MIN_TERM_LENGTH
    ]
    covered = [
        {"term": term, "count": cv_terms[term]} for term in considered if cv_terms[term]
    ]
    missing = [term for term in considered if not cv_terms[term]]
    weak = [entry for entry in covered if entry["count"] <= args.weak_max_count]
    overuse = sorted(
        (entry for entry in covered if entry["count"] >= args.overuse_min_count),
        key=lambda e: e["count"],
        reverse=True,
    )
    coverage = round(len(covered) / max(len(considered), 1) * 100)

    must_have = None
    if args.must_have:
        if not args.must_have.is_file():
            print(
                f"error: must-have list not found or not a file: {args.must_have}",
                file=sys.stderr,
            )
            return 2
        entries = load_must_have(args.must_have)
        mh_covered = []
        mh_missing = []
        for entry in entries:
            count = count_phrase(entry, normalized_cv)
            if count:
                mh_covered.append({"term": entry, "count": count})
            else:
                mh_missing.append(entry)
        must_have = {
            "list": str(args.must_have),
            "entries": len(entries),
            "covered": mh_covered,
            "missing": mh_missing,
            "coverage_percent": round(len(mh_covered) / max(len(entries), 1) * 100),
        }
        if not entries:
            print(f"warning: {args.must_have} contains no entries", file=sys.stderr)

    result = {
        "job": str(args.job),
        "document": str(args.cv),
        "terms_considered": len(considered),
        "coverage_percent": coverage,
        "covered": covered,
        "missing": missing,
        "weak": weak,
        "weak_max_count": args.weak_max_count,
        "overuse": overuse,
        "overuse_min_count": args.overuse_min_count,
        "must_have": must_have,
    }

    report = (
        json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.json
        else render_markdown(result, args.list_limit)
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
