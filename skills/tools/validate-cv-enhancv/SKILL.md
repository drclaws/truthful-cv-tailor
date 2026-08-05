---
name: validate-cv-enhancv
description: External, advisory CV check performed by the Enhancv Resume Checker web service. Submits the final PDF deliverable through a real browser session and saves the service's report verbatim as a raw capture for the reviewer to normalize. Gated behind the internal and render gates; never edits the CV.
---

# Tool skill: validate-cv-enhancv — external resume check via the Enhancv Resume Checker

## Purpose

Obtains a third party's opinion of the finished CV: the Enhancv Resume Checker parses the submitted
PDF, reports how well a machine reads it, and offers suggestions. This skill holds the rules of that
one operation — what may be submitted, how the service is driven, what is captured, and what the
capture may and may not be used for.

The result of this skill is **raw material, not a verdict**. The capture is handed back; the reviewer
turns it into a `validation-report` and judges it in separate, later steps.

## What this skill is, and is not

- **A procedure plus its assets, never an actor.** It defines no agent and carries no authority of
  its own. It is executed by the reviewer (`roles/reviewer/ROLE.md`), and the reviewer's invariants
  always apply — in particular: the document under review is never edited here, external scores are
  never truth, and nothing this service says can justify a claim the evidence does not carry.
- **Optional and registered.** It runs only when the user's local rules file lists it in the active
  validation set as an `external` entry (`contracts/user-context.md`). Membership is never decided by
  the executing role or by this file.
- **Gated.** External checks run only after the run's internal checks and render gates are green. A
  submission before that wastes the run and invites advice about problems that were already fixed.
- **Advisory in both directions.** A high score is not evidence of quality, and a low score is not a
  defect finding. Both are the service's claims about the file it parsed.

## Invocation

| Context | Who runs it | Where the outputs go |
|---|---|---|
| Inside a CV workflow | the reviewer, through `roles/reviewer/capabilities/run-external-checks.md` | the raw-capture paths the workflow passes |
| Standalone | the user, invoking the reviewer or the script directly | `outputs/validate-cv-enhancv/<run-id>/`, with a minimal `run.md` |

Paths are always supplied by the caller. This skill derives no path from repository layout, and the
export filename it receives is the caller's, produced by the calling workflow's naming rule.

## Inputs

| Input | Contract / form | Required |
|---|---|---|
| `deliverable` | the final rendered PDF, at the export path and name the calling flow produced | required |
| `run_manifest` | `run-manifest` (`run.md`) — read for the gate statuses that open this step | required |
| `gate_names` | the names of the gates that must be green, exactly as `run.md` records them | required |
| `required_artifacts` | the run artifacts that must exist before submitting — at minimum the final document the deliverable was rendered from, and the mandatory truthfulness check's report | required |
| `raw_capture_path` | where the verbatim capture is written | required |
| `job_description` | the vacancy text | not used — the service's checker takes the resume only |

The service accepts **PDF only** here. The predecessor's DOCX path is deliberately gone: PDF is the
only deliverable this repository produces.

## Outputs

| Output | Form | Notes |
|---|---|---|
| raw capture (markdown) | verbatim page text plus a provenance header | not a contract instance; never edited, trimmed or summarized |
| raw capture (HTML) | the page source at capture time | written beside the markdown capture |
| raw capture (screenshot) | full-page PNG | evidence of what was on screen, including a partial or failed run |
| outcome | `completed` / `not-completed` / `blocked` / `skipped` | printed, and written as JSON on request |

After the reviewer runs `roles/reviewer/capabilities/normalize-external-report.md` over the raw
capture, a `validation-report` instance exists for it — advisory, never carrying a blocking verdict.
The recommendations are then judged by
`roles/reviewer/capabilities/gate-external-recommendations.md`.

## Service parameters

| Parameter | Value |
|---|---|
| Service | Enhancv Resume Checker, `https://enhancv.com/resources/resume-checker/` |
| Interaction mode | real browser session; the upload and the report are produced by client-side JavaScript, so an HTTP request cannot replace it |
| Accepted input | PDF |
| Maximum input size | **2 MB** (the service's limit at the time of writing; the runner refuses a larger file before any upload) |
| Input filename | supplied by the caller; the check enforces a naming pattern only when the caller passes one |
| Job description | not submitted |
| Session state | a fresh browser context per run; no account, no login, no cookies carried between runs |
| Order | last advisory step of a run, after internal checks and render gates |

**Checks the service is expected to report** (used to tell a complete capture from a fragment, never
as a checklist the CV must satisfy): resume score, ATS parse rate, spelling and grammar, content
strength, quantifying impact, readability, formatting issues, skill evidence, employment gaps, design
feedback. A capture missing most of these is a partial capture and must be marked as one.

## Trust policy

These are the rules the reviewer applies to anything this service returns. They restate the role's
invariants for this specific entry; where they seem to conflict with the role, the role wins.

- The score is **advisory**. It never becomes a verdict, never appears as a claim about the
  candidate, and is recorded only as this service's measurement under its own label.
- Every recommendation **requires fact validation** before it can be applied. An applied
  recommendation triggers a re-run of the mandatory truthfulness check and of the internal checks it
  could have affected.
- The service **may** suggest keyword additions, rewrites and formatting changes. It **may not**
  cause a fact, tool, metric, certification, seniority level or domain of experience to be added to
  the CV. Any suggestion that would require one is recorded as a gap, never applied.
- Unsupported recommendations go to the run's gap report, honestly, as things the CV does not claim.
- This step runs **after** the local gates, never before, and never "just to see what it says".
- Nothing here edits the CV, the deliverable, the knowledge bank or the constraints ledger.

## Runbook

The rules below are the operation's rules. The bundled script implements them; it does not own them.
A run performed by hand follows the same rules.

### Environment preparation

1. Confirm the dependencies declared below are bound. A required one that is not bound ⇒ the entry is
   **SKIPPED with instructions**; that is a recorded outcome, never a failure of the run.
2. Resolve this skill's settings from the user's local rules file (`## Skill settings` →
   `### validate-cv-enhancv`) and pass them to the script as explicit arguments. The script never
   reads the rules file itself.
3. Confirm the deliverable exists at the export path the flow produced, is a PDF, is at most 2 MB,
   and was rendered from the *final* document — a deliverable older than the last content change
   blocks the step.
4. Create nothing else and change nothing else. The step is read-only apart from its own captures.

### The precheck (gates first, submission second)

Nothing is sent to a third party before all of this holds:

- **The gates the caller named are green in `run.md`.** The statuses are read from the run manifest,
  matched by the gate names the caller passes. A gate is green only when a line naming it says so and
  no line naming it says anything worse. The manifest records gates in a table, so a matching row is
  read cell by cell and only a cell that *opens* with a status word counts — the requirement column
  says what the gate needs and must never outvote the state column. The contract's four states are
  recognized: `green` opens the submission, `red`, `not reached` and `waived by the user` do not. A
  gate the manifest does not mention, or mentions ambiguously, counts as **unknown — and unknown is
  never green**.
- **The declared artifacts exist and are non-empty** — at minimum the final document and the report
  of the mandatory truthfulness check, plus whatever else the flow declares.
- **None of those artifacts carries a blocking marker.** Unless the caller supplies its own list, the
  markers are `todo`, `placeholder`, `do not send` and `returned empty text`: text that says the run
  is unfinished or must not be sent. A marker hit blocks the submission and names the file and the
  marker.
- **The input passes its own checks** — PDF, non-empty, within the size limit, and matching the
  export naming rule when the caller passes one.

Any failure ⇒ outcome `blocked`, nothing submitted, and the reason states which condition failed. The
gate check can be waived only by an explicit, deliberate override, and a waived run says so in its
output.

### Service interaction

1. Open a fresh browser context and navigate to the service URL.
2. **Dismiss the cookie banner** if one appears (its accept control carries one of the usual labels).
   A banner left standing hides the upload control.
3. **Wait for the upload UI to be ready** — a file input, or the page's own upload prompt. The page
   loads its interface asynchronously; acting before it is ready produces a false "no upload control"
   failure.
4. **Submit the PDF** through the file input, clicking the upload prompt first when the input is not
   directly present.
5. **Wait for processing to finish.** The report is ready when the page shows report content (a
   score, a parse rate, an issue list) *and* no longer shows a processing message, and when that
   content has stopped changing across consecutive reads. A page that still says it is analysing is
   not a report.
6. **Capture verbatim**: the visible report text into the markdown capture (with a provenance header
   naming the service, URL, submitted file, browser engine and capture time), the page source into
   the HTML capture, and a full-page screenshot beside them. Captures are never edited afterwards —
   they are the evidence of what the service said.
7. If the procedure fails or is interrupted, capture whatever state exists and mark it as a
   diagnostic, partial capture. A fragment is never handed on as a report.

### Captcha and visible-browser policy

- **The browser window is visible by default.** This is the normal mode and it is deliberate: the
  service puts human-verification challenges in front of the upload and, sometimes, in front of the
  report.
- **Challenges are completed by the user, in the open browser window.** The check never attempts to
  solve, bypass, or automate its way around a captcha or a security check.
- When a challenge is detected, the run **says so and waits**, extending its deadline by the manual
  grace period (default **120 seconds** with a visible browser). The user completes the challenge and
  the run continues on its own.
- **Headless mode is opt-in only**, for unattended automation the user explicitly asked for. In
  headless mode the manual grace period defaults to 0, a detected challenge cannot be completed, and
  the correct outcome is to stop and report — not to retry blindly.
- An unattended challenge is **not-completed**, not a document defect, and never produces a `Fail`
  verdict about the CV.

### Manual fallback

Use it when browser automation is unbound, when the service changes in a way the runner does not
follow, or when the user prefers to drive the service themselves.

1. Open the service URL in a normal browser session.
2. Upload the same deliverable — the exact export the flow produced, unmodified.
3. Complete any challenge in that browser.
4. Wait for the full report, then copy **all** of its text verbatim into the raw-capture path the
   flow assigned; save a screenshot beside it when possible.
5. Add a short provenance note at the top of the capture: service, URL, submitted file, date, and the
   fact that the capture was taken by hand.
6. Hand the capture back. The reviewer normalizes and gates it exactly as it would an automated one;
   the entry is recorded **SKIPPED-manual**, or executed if the user completed it during the session.
7. Never paraphrase, summarize or "clean up" the service's text while copying: normalization happens
   in a later step and needs the original wording.

### Troubleshooting

| Symptom | What it means | What to do |
|---|---|---|
| The runner reports the automation stack is not bound | the browser stack is missing for the interpreter running the script | bind it as the dependency entry describes, or run the manual fallback; the entry is SKIPPED either way |
| The browser build cannot be launched | the engine's build is not installed, or a recorded browser binary does not resolve | install the engine build, or correct the `browser_executable` / `browser_channel` setting recorded for this machine |
| The upload UI never becomes ready | the page is slow, or a challenge is standing in front of it | raise the timeout, and run with a visible window so the challenge can be completed |
| A challenge appears and the run ends | the run was headless, or nobody completed the challenge in time | re-run with a visible window and a longer manual grace period (for example 180 seconds) |
| Processing never finishes | the service is slow or the report never rendered | raise the timeout; if it recurs, use the manual fallback and record the service as flaky in the run record |
| The capture contains a cookie wall, an error page or a login prompt | the submission never reached the report | record it as an unusable capture with the evidence; do not reconstruct what the report "would have" said |
| The capture is missing most of the expected checks | partial capture | mark it partial, say what is missing, and let the normalization treat it as a fragment |
| The input is rejected as too large | the file exceeds the 2 MB service limit | do not shrink the CV's content to fit — report it to the flow; the deliverable is the renderer's output, not this step's |
| A local policy forbids Chromium-based browsers | the default engine is not acceptable here | record `browser_engine: firefox` (or `webkit`) in this skill's settings |

## Bundled script

`skills/tools/validate-cv-enhancv/scripts/run_enhancv.py` — drives the service and writes the
captures. It takes explicit command-line arguments only, reads no rules or context file, and derives
no path from repository layout.

```text
run_enhancv.py --pdf <export.pdf> --raw-out <run>/external/enhancv_raw.md \
    --run-manifest <run>/run.md \
    --require-gate "<gate name as run.md records it>" \
    --require-artifact <run>/final_cv.md --require-artifact <run>/fact_check.md
```

| Argument | Purpose |
|---|---|
| `--pdf` | the deliverable to submit |
| `--raw-out` | the markdown capture path; the HTML and PNG captures default to the same stem |
| `--html-out`, `--screenshot-out` | override those two paths |
| `--status-json` | write the machine-readable outcome of the invocation |
| `--run-manifest` | the `run.md` whose gate statuses are read |
| `--require-gate` | repeatable; a gate that must be green |
| `--require-artifact` | repeatable; an artifact that must exist and be non-empty |
| `--forbid-marker`, `--no-marker-scan` | replace or disable the blocking-marker scan |
| `--skip-gate-check` | deliberate override; the run says it was waived |
| `--export-name-pattern` | the calling workflow's naming rule, enforced when passed |
| `--max-input-mb` | input size limit; defaults to the service's 2 MB |
| `--url` | service URL override |
| `--browser`, `--browser-channel`, `--browser-executable` | engine choice and machine-specific bindings |
| `--headless` | opt into an unattended run |
| `--timeout-ms`, `--manual-wait-seconds` | waiting behaviour, including the challenge grace period |

**Outcome, not exit code.** The script prints one of `completed`, `not-completed`, `blocked`,
`skipped` and exits `0` whenever the command line was valid — an unbound dependency is a reported
status, never a crash. Exit `2` means the command line itself was wrong; exit `130` means the run was
interrupted. The reviewer reads the outcome, and records it in its run record with the reviewer's own
vocabulary (`executed`, `SKIPPED`, `not completed`, `blocked`).

## Settings recognized in the user's context

Recorded under `## Skill settings` → `### validate-cv-enhancv` in the user's local rules file (see
`contracts/user-context.md`). All are optional; the machine-specific bindings of this skill's
dependencies belong here and nowhere else. Keys this file does not define are reported to the user,
never silently ignored.

| Key | Values | Default | Effect |
|---|---|---|---|
| `mode` | `browser`, `manual` | `browser` | `manual` forces the manual fallback without attempting automation |
| `python_interpreter` | path or name | the caller's `python3` | the interpreter that has the automation stack installed |
| `browser_engine` | `chromium`, `firefox`, `webkit` | `chromium` | which engine the run drives |
| `browser_channel` | channel name | none | launch a locally installed browser channel instead of the bundled build |
| `browser_executable` | path or name | none | launch a specific browser binary; a bare name is resolved on `PATH` |
| `headless` | `true`, `false` | `false` | `true` only for unattended automation the user asked for |
| `manual_wait_seconds` | integer | `120` visible / `0` headless | grace period for completing a challenge |
| `timeout_ms` | integer | `180000` | maximum wait for the upload UI and for processing |
| `service_url` | URL | the service URL above | override when the service moves |
| `max_input_mb` | number | `2` | override when the service's limit changes |

## Dependencies

- **name:** `python3`
  **kind:** tool
  **needed for:** running the bundled runner script
  **required | optional:** required
  **when unbound:** the check runs manual — the reviewer follows the manual fallback and records the
  entry as SKIPPED-manual with those instructions.

- **name:** browser automation
  **kind:** capability
  **needed for:** driving a real browser session through the service's client-side upload and report
  **required | optional:** required
  **when unbound:** the entry runs SKIPPED with instructions; the manual fallback in the runbook is
  the documented substitute, and the flow continues.

- **name:** `playwright` (Python package, `playwright.async_api`)
  **kind:** tool
  **needed for:** the concrete binding of browser automation used by the bundled script
  **required | optional:** required
  **when unbound:** the script reports outcome `skipped` with the binding instructions and the manual
  fallback; nothing is submitted and nothing crashes.

- **name:** a Playwright browser build — `chromium` (default), or `firefox` / `webkit`
  **kind:** tool
  **needed for:** rendering the service page and letting the user complete challenges
  **required | optional:** required
  **when unbound:** the script reports outcome `skipped` naming the engine that could not be
  launched; install the engine build or record a `browser_channel` / `browser_executable` binding.

- **name:** network access to the service host
  **kind:** capability
  **needed for:** reaching the checker at all
  **required | optional:** required
  **when unbound:** the run ends `not-completed` with the diagnostic capture; the manual fallback
  applies from a machine that can reach the service.

- **name:** an interactive desktop session (a visible browser window)
  **kind:** capability
  **needed for:** completing the service's human-verification challenges, which is the default mode
  **required | optional:** required
  **when unbound:** the run may be attempted headless (`headless: true`), but a challenge then cannot
  be completed and the run ends `not-completed`; the manual fallback on a machine with a display is
  the documented path.
