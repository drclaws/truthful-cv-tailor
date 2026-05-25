#!/usr/bin/env python3
"""Run Enhancv Resume Checker through a real browser and save a raw report."""

import argparse
import asyncio
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

URL = "https://enhancv.com/resources/resume-checker/"
MAX_SIZE_BYTES = 2 * 1024 * 1024
EXPORT_BASENAME_RE = re.compile(r"^[A-Z][A-Za-z]+[A-Z][A-Za-z]+$")
LOCAL_VALIDATION_FILES = [
    "05_fact_validation.md",
    "06_ats_validation.md",
    "07_position_match.md",
    "08_final_cv.md",
    "pdf_text_check.md",
]


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


def default_pdf_for_job(base):
    exports = base / "exports"
    candidates = sorted(
        path for path in exports.glob("*.pdf") if has_candidate_export_name(path)
    )
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        formatted = "\n".join(f"- {path}" for path in candidates)
        raise SystemExit(
            "Multiple candidate-named PDF exports found. Pass the intended file "
            f"with --pdf:\n{formatted}"
        )
    invalid = sorted(exports.glob("*.pdf"))
    if invalid:
        formatted = "\n".join(f"- {path}" for path in invalid)
        raise SystemExit(
            "No PDF export matches FirstNameSurname.pdf. Rename or create the "
            f"candidate-named export before running Enhancv:\n{formatted}"
        )
    return exports / "FirstNameSurname.pdf"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Upload a final CV PDF to Enhancv Resume Checker via Playwright."
    )
    parser.add_argument("--job", help="Job output folder name under outputs/.")
    parser.add_argument("--pdf", help="Path to the PDF to upload.")
    parser.add_argument("--out", help="Path for the raw markdown report.")
    parser.add_argument("--url", default=URL, help="Enhancv checker URL.")
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
    parser.add_argument(
        "--skip-local-validation-gate",
        action="store_true",
        help="Allow upload without checking local validation artifacts first.",
    )
    return parser.parse_args()


def resolve_paths(args):
    base = None
    if args.job:
        base = Path("outputs") / args.job
        pdf = Path(args.pdf) if args.pdf else default_pdf_for_job(base)
        out = (
            Path(args.out)
            if args.out
            else base / "external_validators" / "enhancv_raw.md"
        )
    else:
        if not args.pdf or not args.out:
            raise SystemExit("Use either --job or both --pdf and --out.")
        pdf = Path(args.pdf)
        out = Path(args.out)

    return pdf, out, out.with_suffix(".html"), out.with_suffix(".png"), base


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


def require_local_validations(base):
    if base is None:
        return

    missing = [name for name in LOCAL_VALIDATION_FILES if not (base / name).exists()]
    if missing:
        formatted = "\n".join(f"- {base / name}" for name in missing)
        raise SystemExit(
            "Enhancv must run after local validations and PDF extraction checks. "
            f"Missing:\n{formatted}"
        )

    risky_markers = {
        "05_fact_validation.md": ["todo", "placeholder"],
        "06_ats_validation.md": ["todo", "placeholder"],
        "07_position_match.md": ["do not send", "todo", "placeholder"],
        "pdf_text_check.md": ["fail:", "returned empty text"],
    }
    warnings = []
    for name, markers in risky_markers.items():
        text = (base / name).read_text(encoding="utf-8").lower()
        matched = [marker for marker in markers if marker in text]
        if matched:
            warnings.append(f"- {base / name}: {', '.join(matched)}")

    if warnings:
        formatted = "\n".join(warnings)
        raise SystemExit(
            "Local validation artifacts contain blocking/risky markers. "
            "Resolve them before sending the PDF to Enhancv, or pass "
            f"--skip-local-validation-gate intentionally.\n{formatted}"
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


async def capture_outputs(page, out, html_path, screenshot_path, pdf, status=None):
    html_path.write_text(await page.content(), encoding="utf-8")
    await page.screenshot(path=str(screenshot_path), full_page=True)
    visible_text = await page.locator("body").inner_text(timeout=10000)
    out.write_text(
        markdown_report(page.url, pdf, html_path, screenshot_path, visible_text, status),
        encoding="utf-8",
    )


def markdown_report(url, pdf, html_path, screenshot_path, visible_text, status=None):
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
- Browser automation: Playwright
- Captured at: {timestamp}
- Saved HTML: `{html_path}`
- Saved screenshot: `{screenshot_path}`
{status_section}

## Raw Visible Text

```text
{visible_text.strip()}
```
"""


async def safe_capture_outputs(page, out, html_path, screenshot_path, pdf, status):
    try:
        await capture_outputs(page, out, html_path, screenshot_path, pdf, status=status)
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
            status=f"Capture failed: {type(exc).__name__}: {exc}",
        )
        out.write_text(fallback, encoding="utf-8")
        print(f"Wrote fallback diagnostic report to {out}")


async def run(args):
    pdf, out, html_path, screenshot_path, base = resolve_paths(args)
    visible_browser = not args.headless
    manual_wait_seconds = resolve_manual_wait_seconds(args, visible_browser)
    if not args.skip_local_validation_gate:
        require_local_validations(base)
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
        browser = await playwright.chromium.launch(headless=args.headless)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        page.set_default_timeout(args.timeout_ms)

        if visible_browser:
            print(
                "Opening a visible Chromium window. Complete any captcha or "
                "security checks in the browser when prompted."
            )
        else:
            print(
                "Running with --headless. Captcha and other manual steps cannot "
                "be completed interactively."
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
            await safe_capture_outputs(page, out, html_path, screenshot_path, pdf, status)
            raise
        else:
            await capture_outputs(
                page,
                out,
                html_path,
                screenshot_path,
                pdf,
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
