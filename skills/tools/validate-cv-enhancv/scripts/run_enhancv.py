#!/usr/bin/env python3
"""Run the Enhancv Resume Checker through a real browser and save a raw capture.

The rules of this check live in the SKILL.md next to this script; the script only
executes them. Every path is an explicit command-line argument resolved by the
caller: nothing is derived from repository layout, and no rules, context or
configuration file is ever read here.

Precheck: the gate statuses are read from the run manifest (`run.md`, contract
`run-manifest`) whose path the caller passes, and the artifacts that must exist
are named by the caller as explicit paths.
"""

import argparse
import asyncio
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

URL = "https://enhancv.com/resources/resume-checker/"
MAX_SIZE_BYTES = 2 * 1024 * 1024
EXPORT_BASENAME_RE = re.compile(r"^[A-Z][A-Za-z]+[A-Z][A-Za-z]+$")

# Status vocabulary recognized in a run manifest. The manifest is free-form
# markdown, so a gate line is located by name and then read for one of these
# words. Anything else is "unclear" — and unclear is never green.
GREEN_STATUS = ("green", "pass", "passed", "ok", "complete", "completed", "done")
RED_STATUS = ("red", "fail", "failed", "failing", "blocked", "error")
NEUTRAL_STATUS = (
    "skipped",
    "skip",
    "pending",
    "in progress",
    "not run",
    "not started",
    "todo",
    "unknown",
    "n a",
)

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


def has_candidate_export_name(path):
    return bool(EXPORT_BASENAME_RE.fullmatch(path.stem))


def require_candidate_export_name(pdf):
    if has_candidate_export_name(pdf):
        return
    raise SystemExit(
        "Enhancv must receive a PDF whose filename matches the final export "
        "pattern FirstNameSurname.pdf, for example JaneDoe.pdf. "
        f"Got: {pdf}"
    )


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


def validate_pdf(pdf):
    if not pdf.exists():
        raise SystemExit(f"PDF not found: {pdf}")
    if pdf.suffix.lower() != ".pdf":
        raise SystemExit(f"Enhancv runner is configured for PDF input only: {pdf}")
    require_candidate_export_name(pdf)
    size = pdf.stat().st_size
    if size > MAX_SIZE_BYTES:
        raise SystemExit(
            f"PDF is {size / 1024 / 1024:.2f}MB; Enhancv currently accepts max 2MB."
        )


def normalize_text(text):
    """Lowercase, and collapse everything that is not a letter or a digit."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def contains_phrase(normalized, phrase):
    return f" {phrase} " in f" {normalized} "


def classify_line(line):
    """Return green/red/neutral for a manifest line, or None when it says nothing."""
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


def require_green_gates(manifest_path, gates):
    """Block unless every requested gate is recorded green in the run manifest."""
    if manifest_path is None:
        raise SystemExit(
            "Pass --run-manifest so the gate statuses can be read, or pass "
            "--skip-gate-check deliberately."
        )

    manifest = Path(manifest_path)
    if not manifest.exists():
        raise SystemExit(f"Run manifest not found: {manifest}")
    try:
        lines = manifest.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise SystemExit(f"Run manifest is unreadable: {manifest}: {exc}") from exc

    if not gates:
        raise SystemExit(
            "No gate names were passed. Name the gates that must be green with "
            "--require-gate, or pass --skip-gate-check deliberately."
        )

    problems = []
    for gate in gates:
        status, evidence = gate_status(lines, gate)
        if status == "green":
            continue
        quoted = "; ".join(evidence) if evidence else "no line names this gate"
        problems.append(f"- {gate}: {status} ({quoted})")

    if problems:
        formatted = "\n".join(problems)
        raise SystemExit(
            "External checks run only after the internal and render gates are "
            f"green. Not green in {manifest}:\n{formatted}"
        )


def require_artifacts(paths, markers, scan_markers):
    """Block unless every declared artifact exists, is non-empty and is clean."""
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
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        hits = [marker for marker in markers if marker.lower() in text]
        if hits:
            problems.append(f"- {path}: contains {', '.join(hits)}")

    if problems:
        formatted = "\n".join(problems)
        raise SystemExit(
            "Required artifacts are missing or carry blocking markers. Resolve "
            "them before submitting the PDF to Enhancv, or adjust "
            f"--require-artifact / --forbid-marker deliberately:\n{formatted}"
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


async def run(args):
    pdf, out, html_path, screenshot_path = resolve_paths(args)
    visible_browser = not args.headless
    manual_wait_seconds = resolve_manual_wait_seconds(args, visible_browser)

    if args.skip_gate_check:
        print(
            "Gate check skipped by explicit request. External checks are meant to "
            "run only after the internal and render gates are green."
        )
    else:
        require_green_gates(args.run_manifest, args.require_gate)

    require_artifacts(
        args.require_artifact,
        args.forbid_marker or list(DEFAULT_FORBIDDEN_MARKERS),
        not args.no_marker_scan,
    )
    validate_pdf(pdf)
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise SystemExit(
            "Playwright is not installed. Install it with "
            "`python3 -m pip install playwright` and "
            "`python3 -m playwright install chromium`."
        ) from exc

    async with async_playwright() as playwright:
        browser_type = getattr(playwright, args.browser)
        browser = await browser_type.launch(headless=args.headless)
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

        try:
            await wait_for_report(
                page,
                args.timeout_ms,
                visible_browser=visible_browser,
                captcha_grace_seconds=manual_wait_seconds,
            )
        except BaseException as exc:
            status = f"Interrupted or failed before completion: {type(exc).__name__}: {exc}"
            await safe_capture_outputs(
                page, out, html_path, screenshot_path, pdf, args.browser, status
            )
            raise
        else:
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
        print(f"Wrote {out}")
        print(f"Wrote {html_path}")
        print(f"Wrote {screenshot_path}")


def main():
    args = parse_args()
    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
