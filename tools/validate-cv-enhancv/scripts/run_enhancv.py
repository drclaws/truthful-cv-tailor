#!/usr/bin/env python3
"""Run the Enhancv Resume Checker through a real browser and save a raw capture.

The rules of this check live in the TOOL.md next to this script; the script only
executes them. Every path is an explicit command-line argument resolved by the
caller: nothing is derived from repository layout, and no rules, context or
configuration file is ever read here.

Precheck: the gate statuses are read from the run manifest (`run.md`, contract
`run-manifest`) whose path the caller passes, and the artifacts that must exist
are named by the caller as explicit paths.

Outcome, not exit code: the script reports one of `completed`, `not-completed`,
`blocked` or `skipped` on stdout (and, with --status-json, as a JSON file), and
exits 0 whenever the arguments were valid. An unbound browser stack is
`skipped` with instructions — a reported status, never a crash. Exit 2 means the
command line itself was wrong; exit 130 means the run was interrupted.

    run_enhancv.py --pdf <export.pdf> --raw-out <run>/external/enhancv_raw.md \
        --run-manifest <run>/run.md --require-gate "fact check" \
        --require-artifact <run>/final_cv.md
"""

import argparse
import asyncio
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

URL = "https://enhancv.com/resources/resume-checker/"
DEFAULT_MAX_INPUT_MB = 2.0

STATUS_COMPLETED = "completed"
STATUS_NOT_COMPLETED = "not-completed"
STATUS_BLOCKED = "blocked"
STATUS_SKIPPED = "skipped"

# Status vocabulary recognized in a run manifest. A gate line is located by name
# and then read for one of these words. Anything else is "unclear" — and unclear
# is never green.
#
# The run-manifest contract records gates in a table whose state column holds
# `green`, `red`, `not reached`, or `waived by the user, with the reason`. Those
# four are covered below, and a table row is read CELL BY CELL: the requirement
# column of a gate row routinely contains words like "pass" or "skipped" as part
# of what the gate requires, and reading the whole line would let that text
# outvote the state cell. A cell counts as a status only when it OPENS with one
# of these words; the worst status found across a row wins.
GREEN_STATUS = ("green", "pass", "passed", "ok", "complete", "completed", "done")
RED_STATUS = ("red", "fail", "failed", "failing", "blocked", "error")
NEUTRAL_STATUS = (
    "skipped",
    "skip",
    "pending",
    "in progress",
    "not run",
    "not started",
    "not reached",
    "waived",
    "todo",
    "unknown",
    "n a",
)
# Labels a state cell may carry before the status word itself.
STATUS_LABELS = ("current state ", "state ", "status ")

# Markers that make an artifact unfit to be the basis of an external submission.
# Applied to the artifacts the caller declared as required; replaceable with
# --forbid-marker, disableable with --no-marker-scan.
DEFAULT_FORBIDDEN_MARKERS = (
    "todo",
    "placeholder",
    "do not send",
    "returned empty text",
)

BINARY_SUFFIXES = frozenset({".pdf", ".png", ".jpg", ".jpeg", ".docx", ".zip"})

# Launch failures that mean "the browser stack is not bound on this machine"
# rather than "the service or the page misbehaved".
UNBOUND_LAUNCH_HINTS = (
    "executable doesn't exist",
    "playwright install",
    "no such file or directory",
)


class Outcome:
    """What happened, in the vocabulary the calling reviewer records."""

    def __init__(self, status, summary, details=None, captures=None, instructions=None):
        self.status = status
        self.summary = summary
        self.details = list(details or [])
        self.captures = list(captures or [])
        self.instructions = list(instructions or [])

    def as_dict(self):
        return {
            "status": self.status,
            "summary": self.summary,
            "details": self.details,
            "captures": [str(path) for path in self.captures],
            "instructions": self.instructions,
        }

    def emit(self, status_json_path=None):
        print(f"status: {self.status}")
        print(self.summary)
        for line in self.details:
            print(line)
        for path in self.captures:
            print(f"capture: {path}")
        if self.instructions:
            print("\nWhat to do:")
            for line in self.instructions:
                print(f"  {line}")
        if status_json_path:
            path = Path(status_json_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(self.as_dict(), indent=2) + "\n", encoding="utf-8"
            )
            print(f"status file: {path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Upload a final CV PDF to the Enhancv Resume Checker through a real "
            "browser and save the raw capture. All paths are explicit arguments."
        )
    )
    parser.add_argument("--pdf", required=True, help="Path to the PDF to submit.")
    parser.add_argument(
        "--raw-out", required=True, help="Path for the raw markdown capture."
    )
    parser.add_argument(
        "--html-out",
        help="Path for the raw page HTML. Default: --raw-out with an .html suffix.",
    )
    parser.add_argument(
        "--screenshot-out",
        help="Path for the full-page screenshot. Default: --raw-out with a .png suffix.",
    )
    parser.add_argument(
        "--status-json",
        help="Optional path for the machine-readable outcome of this invocation.",
    )
    parser.add_argument(
        "--run-manifest",
        help=(
            "Path to the run manifest (run.md, contract run-manifest) whose gate "
            "statuses open this step. Required unless --skip-gate-check is passed."
        ),
    )
    parser.add_argument(
        "--require-gate",
        action="append",
        default=[],
        metavar="NAME",
        help=(
            "Name of a gate that must be recorded green in the run manifest. "
            "Repeatable; the caller decides which gates matter."
        ),
    )
    parser.add_argument(
        "--require-artifact",
        action="append",
        default=[],
        metavar="PATH",
        help=(
            "Path to an artifact that must exist and be non-empty before "
            "submitting. Repeatable."
        ),
    )
    parser.add_argument(
        "--forbid-marker",
        action="append",
        default=[],
        metavar="TEXT",
        help=(
            "Text whose presence in a required artifact blocks the submission. "
            "Repeatable; replaces the built-in default marker list."
        ),
    )
    parser.add_argument(
        "--no-marker-scan",
        action="store_true",
        help="Check that required artifacts exist, without scanning their text.",
    )
    parser.add_argument(
        "--skip-gate-check",
        action="store_true",
        help=(
            "Submit without reading the run manifest. Deliberate override only: "
            "external checks are gated behind the internal and render gates."
        ),
    )
    parser.add_argument(
        "--export-name-pattern",
        metavar="REGEX",
        help=(
            "Regular expression the export filename (without suffix) must match. "
            "The naming rule belongs to the calling workflow; pass it here to have "
            "it enforced. Omitted: the name is not checked."
        ),
    )
    parser.add_argument(
        "--max-input-mb",
        type=float,
        default=DEFAULT_MAX_INPUT_MB,
        help=(
            "Maximum accepted input size in MB. Default 2, the service limit at "
            "the time of writing."
        ),
    )
    parser.add_argument("--url", default=URL, help="Enhancv checker URL.")
    parser.add_argument(
        "--browser",
        choices=("chromium", "firefox", "webkit"),
        default="chromium",
        help=(
            "Playwright browser engine to use. Default chromium; pick firefox or "
            "webkit when local policy forbids Chromium-based browsers, including "
            "Google Chrome for Testing."
        ),
    )
    parser.add_argument(
        "--browser-channel",
        help=(
            "Browser channel to launch instead of the bundled build, e.g. a "
            "locally installed stable browser. Machine-specific binding."
        ),
    )
    parser.add_argument(
        "--browser-executable",
        help=(
            "Name or path of the browser binary to launch. A bare name is "
            "resolved on PATH. Machine-specific binding."
        ),
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Hide the browser window (not suitable for captcha or other manual steps).",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=180000,
        help="Maximum wait for upload/report processing.",
    )
    parser.add_argument(
        "--manual-wait-seconds",
        type=int,
        default=None,
        help=(
            "Extra time for manual captcha/login/email steps after upload. "
            "Defaults to 120 when the browser is visible, 0 in headless mode."
        ),
    )
    return parser.parse_args()


def resolve_paths(args):
    pdf = Path(args.pdf)
    out = Path(args.raw_out)
    html_path = Path(args.html_out) if args.html_out else out.with_suffix(".html")
    screenshot_path = (
        Path(args.screenshot_out) if args.screenshot_out else out.with_suffix(".png")
    )
    return pdf, out, html_path, screenshot_path


def check_pdf(pdf, max_input_mb, export_name_pattern):
    """Input checks: it exists, it is a PDF, it fits the size limit, it is named
    the way the caller says exports are named."""
    problems = []
    if not pdf.exists():
        return [f"- {pdf}: not found"]
    if not pdf.is_file():
        return [f"- {pdf}: not a file"]
    if pdf.suffix.lower() != ".pdf":
        problems.append(f"- {pdf}: this check accepts PDF input only")

    max_bytes = int(max_input_mb * 1024 * 1024)
    size = pdf.stat().st_size
    if size > max_bytes:
        problems.append(
            f"- {pdf}: {size / 1024 / 1024:.2f}MB exceeds the {max_input_mb:g}MB limit"
        )
    if size == 0:
        problems.append(f"- {pdf}: empty file")

    if export_name_pattern:
        try:
            matcher = re.compile(export_name_pattern)
        except re.error as exc:
            problems.append(f"- --export-name-pattern is not a valid regex: {exc}")
        else:
            if not matcher.fullmatch(pdf.stem):
                problems.append(
                    f"- {pdf.name}: does not match the export naming rule "
                    f"{export_name_pattern!r} passed by the caller"
                )
    return problems


def normalize_text(text):
    """Lowercase, and collapse everything that is not a letter or a digit."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def contains_phrase(normalized, phrase):
    return f" {phrase} " in f" {normalized} "


def opens_with_status(cell):
    """Return the status a table cell opens with, or None when it is not one.

    A state cell says the status and little else ("green", "not reached",
    "waived by the user, with the reason …"). A requirement cell describes what
    the gate needs and may well contain the same words further in — so only the
    opening of the cell counts.
    """
    text = normalize_text(cell)
    for label in STATUS_LABELS:
        if text.startswith(label):
            text = text[len(label):]
            break
    for verdict, words in (
        ("red", RED_STATUS),
        ("neutral", NEUTRAL_STATUS),
        ("green", GREEN_STATUS),
    ):
        for word in words:
            if text == word or text.startswith(f"{word} "):
                return verdict
    return None


def classify_line(line):
    """Return green/red/neutral for a manifest line, or None when it says nothing."""
    if "|" in line:
        # A table row: read the cells, and let the worst status found decide.
        found = {opens_with_status(cell) for cell in line.split("|")}
        for verdict in ("red", "neutral", "green"):
            if verdict in found:
                return verdict
        return None
    normalized = normalize_text(line)
    if any(contains_phrase(normalized, word) for word in RED_STATUS):
        return "red"
    if any(contains_phrase(normalized, word) for word in NEUTRAL_STATUS):
        return "neutral"
    if any(contains_phrase(normalized, word) for word in GREEN_STATUS):
        return "green"
    return None


def gate_status(manifest_lines, gate):
    """Read one gate's status out of the run manifest.

    A gate is green only when at least one line naming it says so and no line
    naming it says anything worse. A gate no line names is `missing`, and missing
    counts as unknown — never as green.
    """
    wanted = normalize_text(gate)
    matches = [
        line for line in manifest_lines if wanted and wanted in normalize_text(line)
    ]
    if not matches:
        return "missing", []

    verdicts = {}
    for line in matches:
        verdict = classify_line(line)
        if verdict:
            verdicts.setdefault(verdict, line.strip())

    for verdict in ("red", "neutral", "green"):
        if verdict in verdicts:
            return verdict, [verdicts[verdict]]
    return "unclear", [line.strip() for line in matches[:3]]


def check_gates(manifest_path, gates):
    """Report every requested gate that is not recorded green in the manifest."""
    if manifest_path is None:
        return [
            "- no --run-manifest was passed: the gate statuses cannot be read "
            "(pass --skip-gate-check deliberately to submit anyway)"
        ]
    if not gates:
        return [
            "- no --require-gate was passed: name the gates that must be green "
            "(or pass --skip-gate-check deliberately)"
        ]

    manifest = Path(manifest_path)
    if not manifest.exists():
        return [f"- run manifest not found: {manifest}"]
    try:
        lines = manifest.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return [f"- run manifest is unreadable: {manifest}: {exc}"]

    problems = []
    for gate in gates:
        status, evidence = gate_status(lines, gate)
        if status == "green":
            continue
        quoted = "; ".join(evidence) if evidence else "no line names this gate"
        problems.append(f"- gate {gate!r}: {status} ({quoted})")
    return problems


def check_artifacts(paths, markers, scan_markers):
    """Report every declared artifact that is missing, empty or marker-flagged."""
    problems = []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            problems.append(f"- {path}: missing")
            continue
        if not path.is_file():
            problems.append(f"- {path}: not a file")
            continue
        if path.stat().st_size == 0:
            problems.append(f"- {path}: empty")
            continue
        if not scan_markers or path.suffix.lower() in BINARY_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace").lower()
        except OSError as exc:
            problems.append(f"- {path}: unreadable: {exc}")
            continue
        hits = [marker for marker in markers if marker.lower() in text]
        if hits:
            problems.append(f"- {path}: contains {', '.join(hits)}")
    return problems


def manual_fallback_instructions(url, pdf, out):
    """The short form of the manual procedure; the full one is in TOOL.md."""
    return [
        f"Open {url} in a normal browser session.",
        f"Upload {pdf} yourself and complete any captcha or security check.",
        f"Copy the full report text verbatim into {out} and save any screenshot "
        f"next to it.",
        "Hand the capture back to the reviewer for normalization; record the "
        "entry as SKIPPED-manual, or as executed if you completed it now.",
        "See the runbook section of this tool's TOOL.md for the full procedure.",
    ]


def resolve_browser_executable(name_or_path):
    """Resolve a machine-specific browser binding, or say why it did not resolve."""
    if not name_or_path:
        return None, None
    candidate = Path(name_or_path)
    if candidate.exists():
        return str(candidate), None
    found = shutil.which(name_or_path)
    if found:
        return found, None
    return None, (
        f"the browser binary {name_or_path!r} recorded for this machine was not "
        "found on PATH and does not exist as a path"
    )


def import_playwright():
    """Import the browser-automation stack, or say it is not bound here."""
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        return None, f"the Playwright Python package is not importable ({exc})"
    return async_playwright, None


def binding_hint():
    """A concrete, non-OS-specific pointer for an unbound stack."""
    cli = shutil.which("playwright")
    if cli:
        return (
            f"The playwright CLI is on PATH at {cli}, but its Python package is "
            "not importable by this interpreter — install it into the interpreter "
            "that runs this script."
        )
    return (
        "Bind the stack with `python3 -m pip install playwright` followed by "
        "`python3 -m playwright install chromium`, then re-run."
    )


def skipped_outcome(reason, url, pdf, out, extra=None, include_binding_hint=True):
    details = [f"- {reason}"]
    if include_binding_hint:
        details.append(f"- {binding_hint()}")
    if extra:
        details.append(f"- {extra}")
    return Outcome(
        STATUS_SKIPPED,
        "Browser automation is not bound in this environment; nothing was "
        "submitted to the service.",
        details=details,
        instructions=manual_fallback_instructions(url, pdf, out),
    )


async def dismiss_cookie_banner(page):
    labels = [
        "Accept",
        "Accept all",
        "I agree",
        "Got it",
        "Allow all",
    ]
    for label in labels:
        try:
            button = page.get_by_role("button", name=label)
            if await button.count():
                await button.first.click(timeout=1500)
                return
        except Exception:
            pass


def resolve_manual_wait_seconds(args, visible_browser):
    if args.manual_wait_seconds is not None:
        return max(0, args.manual_wait_seconds)
    return 120 if visible_browser else 0


def extend_deadline_for_manual_step(deadline, visible_browser, captcha_grace_seconds):
    if not visible_browser or captcha_grace_seconds <= 0:
        return deadline
    now = asyncio.get_running_loop().time()
    return max(deadline, now + captcha_grace_seconds)


async def wait_for_upload_ui(
    page, timeout_ms, visible_browser=False, captcha_grace_seconds=0
):
    deadline = asyncio.get_running_loop().time() + timeout_ms / 1000
    ready_text = [
        "Upload Your Resume",
        "Drop your resume",
        "choose a file",
        "PDF & DOCX only",
    ]
    loading_text = ["loading", "processing", "analyzing", "checking"]

    while asyncio.get_running_loop().time() < deadline:
        try:
            if await page.locator("input[type=file]").count():
                return

            body = (await page.locator("body").inner_text(timeout=2000)).lower()
            if needs_manual_step(body):
                print(
                    "Complete captcha or security check in the browser window "
                    "before upload can continue..."
                )
                deadline = extend_deadline_for_manual_step(
                    deadline, visible_browser, captcha_grace_seconds
                )
            if any(text.lower() in body for text in ready_text):
                return
            if not any(text in body for text in loading_text):
                upload = page.get_by_text("Upload Your Resume", exact=False)
                if await upload.count():
                    return
        except Exception:
            pass

        await page.wait_for_timeout(1000)

    raise RuntimeError("Enhancv upload UI did not become ready before timeout.")


async def upload_resume(page, pdf):
    file_input = page.locator("input[type=file]")
    if await file_input.count() == 0:
        upload = page.get_by_text("Upload Your Resume", exact=False)
        if await upload.count():
            await upload.first.click(timeout=5000)
            await page.wait_for_timeout(1000)

    file_input = page.locator("input[type=file]")
    if await file_input.count() == 0:
        raise RuntimeError("Could not find a file upload input on the Enhancv page.")

    await file_input.first.set_input_files(str(pdf.resolve()))


def report_is_ready(text):
    lower = text.lower()
    has_report_signal = any(
        signal in lower
        for signal in [
            "your score",
            "issues found",
            "score",
            "ats parse",
            "parse rate",
            "issues",
            "resume report",
            "spelling and grammar",
        ]
    )
    has_completed_parse = "we parsed" in lower and "successfully" in lower
    still_processing = any(
        signal in lower
        for signal in [
            "uploading your resume...",
            "processing your resume",
            "analyzing your resume",
            "checking your resume",
            "scanning your resume",
            "loading your report",
        ]
    )
    return (has_report_signal or has_completed_parse) and not still_processing


def needs_manual_step(text):
    lower = text.lower()
    return any(
        signal in lower
        for signal in [
            "captcha",
            "verify you are human",
            "checking if the site connection is secure",
            "complete the security check",
        ]
    )


async def wait_for_report(
    page, timeout_ms, visible_browser=False, captcha_grace_seconds=0
):
    try:
        await page.wait_for_load_state("networkidle", timeout=30000)
    except Exception:
        pass

    deadline = asyncio.get_running_loop().time() + timeout_ms / 1000
    last_text = ""
    stable_hits = 0

    while asyncio.get_running_loop().time() < deadline:
        try:
            text = await page.locator("body").inner_text(timeout=5000)
            if report_is_ready(text):
                if text == last_text:
                    stable_hits += 1
                else:
                    stable_hits = 0
                    last_text = text

                if stable_hits >= 2:
                    return
            elif needs_manual_step(text):
                if visible_browser:
                    print(
                        "Waiting for manual browser step such as captcha/security "
                        "check. Complete it in the open browser window..."
                    )
                    deadline = extend_deadline_for_manual_step(
                        deadline, visible_browser, captcha_grace_seconds
                    )
                else:
                    print(
                        "Captcha or security check detected in headless mode. "
                        "Rerun without --headless so you can complete it manually."
                    )
        except Exception:
            pass

        await page.wait_for_timeout(2000)

    raise RuntimeError("Enhancv report did not finish processing before timeout.")


async def capture_outputs(
    page, out, html_path, screenshot_path, pdf, browser_name, status=None
):
    html_path.write_text(await page.content(), encoding="utf-8")
    await page.screenshot(path=str(screenshot_path), full_page=True)
    visible_text = await page.locator("body").inner_text(timeout=10000)
    out.write_text(
        markdown_report(
            page.url,
            pdf,
            html_path,
            screenshot_path,
            visible_text,
            browser_name,
            status,
        ),
        encoding="utf-8",
    )


def markdown_report(
    url, pdf, html_path, screenshot_path, visible_text, browser_name, status=None
):
    timestamp = datetime.now(timezone.utc).isoformat()
    status_section = ""
    if status:
        status_section = f"""
## Capture Status

{status}
"""
    return f"""# Enhancv Raw Report

## Source

- Validator: Enhancv Resume Checker
- URL: {url}
- Uploaded PDF: `{pdf}`
- Browser automation: Playwright ({browser_name})
- Captured at: {timestamp}
- Saved HTML: `{html_path}`
- Saved screenshot: `{screenshot_path}`
{status_section}

## Raw Visible Text

```text
{visible_text.strip()}
```
"""


async def safe_capture_outputs(
    page, out, html_path, screenshot_path, pdf, browser_name, status
):
    try:
        await capture_outputs(
            page, out, html_path, screenshot_path, pdf, browser_name, status=status
        )
        print(f"Wrote diagnostic state to {out}")
        print(f"Wrote diagnostic HTML to {html_path}")
        print(f"Wrote diagnostic screenshot to {screenshot_path}")
    except Exception as exc:
        fallback = markdown_report(
            "capture_failed",
            pdf,
            html_path,
            screenshot_path,
            "",
            browser_name,
            status=f"Capture failed: {type(exc).__name__}: {exc}",
        )
        out.write_text(fallback, encoding="utf-8")
        print(f"Wrote fallback diagnostic report to {out}")


def precheck(args, pdf):
    """Everything that must hold before anything is sent to a third party."""
    problems = []
    if args.skip_gate_check:
        print(
            "Gate check skipped by explicit request. External checks are meant to "
            "run only after the internal and render gates are green."
        )
    else:
        problems += check_gates(args.run_manifest, args.require_gate)

    problems += check_artifacts(
        args.require_artifact,
        args.forbid_marker or list(DEFAULT_FORBIDDEN_MARKERS),
        not args.no_marker_scan,
    )
    problems += check_pdf(pdf, args.max_input_mb, args.export_name_pattern)
    return problems


async def submit(args, pdf, out, html_path, screenshot_path, async_playwright):
    visible_browser = not args.headless
    manual_wait_seconds = resolve_manual_wait_seconds(args, visible_browser)
    executable, binding_problem = resolve_browser_executable(args.browser_executable)
    if binding_problem:
        return skipped_outcome(
            binding_problem, args.url, pdf, out, include_binding_hint=False
        )

    launch_kwargs = {"headless": args.headless}
    if args.browser_channel:
        launch_kwargs["channel"] = args.browser_channel
    if executable:
        launch_kwargs["executable_path"] = executable

    async with async_playwright() as playwright:
        browser_type = getattr(playwright, args.browser)
        try:
            browser = await browser_type.launch(**launch_kwargs)
        except Exception as exc:
            message = str(exc)
            if any(hint in message.lower() for hint in UNBOUND_LAUNCH_HINTS):
                return skipped_outcome(
                    f"the {args.browser} build could not be launched ({type(exc).__name__})",
                    args.url,
                    pdf,
                    out,
                    extra=message.splitlines()[0] if message else None,
                )
            return Outcome(
                STATUS_NOT_COMPLETED,
                "The browser stack is bound but the browser did not start.",
                details=[f"- {type(exc).__name__}: {message.splitlines()[0]}"],
                instructions=manual_fallback_instructions(args.url, pdf, out),
            )

        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        page.set_default_timeout(args.timeout_ms)

        if visible_browser:
            print(
                f"Opening a visible {args.browser} window. Complete any captcha "
                "or security checks in the browser when prompted."
            )
        else:
            print(
                f"Running {args.browser} with --headless. Captcha and other "
                "manual steps cannot be completed interactively."
            )

        try:
            await page.goto(args.url, wait_until="domcontentloaded")
            await dismiss_cookie_banner(page)
            await wait_for_upload_ui(
                page,
                args.timeout_ms,
                visible_browser=visible_browser,
                captcha_grace_seconds=manual_wait_seconds,
            )
            await upload_resume(page, pdf)

            if manual_wait_seconds:
                print(
                    f"Waiting {manual_wait_seconds}s for manual steps after upload..."
                )
                await page.wait_for_timeout(manual_wait_seconds * 1000)

            await wait_for_report(
                page,
                args.timeout_ms,
                visible_browser=visible_browser,
                captcha_grace_seconds=manual_wait_seconds,
            )
        except KeyboardInterrupt:
            await safe_capture_outputs(
                page,
                out,
                html_path,
                screenshot_path,
                pdf,
                args.browser,
                "Interrupted by the user before completion.",
            )
            await browser.close()
            raise
        except Exception as exc:
            status = (
                f"Interrupted or failed before completion: {type(exc).__name__}: {exc}"
            )
            await safe_capture_outputs(
                page, out, html_path, screenshot_path, pdf, args.browser, status
            )
            await browser.close()
            return Outcome(
                STATUS_NOT_COMPLETED,
                "The service was reachable but the procedure did not finish; the "
                "partial capture is diagnostic material, not a report.",
                details=[f"- {type(exc).__name__}: {exc}"],
                captures=[out, html_path, screenshot_path],
                instructions=manual_fallback_instructions(args.url, pdf, out),
            )

        await capture_outputs(
            page,
            out,
            html_path,
            screenshot_path,
            pdf,
            args.browser,
            status="Report appeared complete according to runner readiness checks.",
        )
        await browser.close()

    return Outcome(
        STATUS_COMPLETED,
        "The service returned a report and the raw capture was saved verbatim.",
        captures=[out, html_path, screenshot_path],
    )


async def run(args):
    pdf, out, html_path, screenshot_path = resolve_paths(args)

    problems = precheck(args, pdf)
    if problems:
        return Outcome(
            STATUS_BLOCKED,
            "Nothing was submitted: the preconditions of this check are not met.",
            details=problems,
        )

    async_playwright, missing = import_playwright()
    if missing:
        return skipped_outcome(missing, args.url, pdf, out)

    out.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    return await submit(args, pdf, out, html_path, screenshot_path, async_playwright)


def main():
    args = parse_args()
    try:
        outcome = asyncio.run(run(args))
    except KeyboardInterrupt:
        Outcome(
            STATUS_NOT_COMPLETED,
            "Interrupted by the user; any partial capture was saved.",
        ).emit(args.status_json)
        sys.exit(130)
    outcome.emit(args.status_json)


if __name__ == "__main__":
    main()
