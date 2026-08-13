---
name: validate-cv-enhancv
description: External, advisory CV check performed by the Enhancv Resume Checker web service. Submits the final PDF deliverable through a real browser session and saves the service's report verbatim as a raw capture for the reviewer to normalize. Gated behind the internal and render gates; never edits the CV.
---

# Tool: validate-cv-enhancv — external resume check via the Enhancv Resume Checker

## Purpose

Obtains a third party's opinion of the finished CV: the Enhancv Resume Checker parses the submitted
PDF, reports how well a machine reads it, and offers suggestions. This tool holds the rules of that
one operation — what may be submitted, how the service is driven, what is captured, and what the
capture may and may not be used for.

The result of this tool is **raw material, not a verdict**. The capture is handed back; the reviewer
turns it into a `validation-report` and judges it in separate, later steps.

## What this tool is, and is not

- **A tool, and an internal one.** It is reached by name and in one way only:
  `reviewer.run-external-checks` is handed this file as the spec to execute. It is registered with no
  harness, discovered by none and never offered in a selection surface — a submission to a third
  party is the last step of a run whose gates are already green, and a request landing here directly
  would arrive with none of that established.
- **A procedure plus its assets, never an actor.** It defines no agent and carries no authority of
  its own. It is executed by the role `reviewer`, and the reviewer's invariants always apply — in
  particular: the document under review is never edited here, external scores are never truth, and
  nothing this service says can justify a claim the evidence does not carry.
- **Optional and registered.** It runs only when the user's local rules file lists it in the active
  validation set as an `external` entry (contract `user-context`). Membership is never decided by
  the executing role or by this file.
- **Gated.** External checks run only after the run's internal checks and render gates are green. A
  submission before that wastes the run and invites advice about problems that were already fixed.
- **Advisory in both directions.** A high score is not evidence of quality, and a low score is not a
  defect finding. Both are the service's claims about the file it parsed.

## Invocation

| Context | Who runs it | Where the outputs go |
|---|---|---|
| Inside a CV workflow | the reviewer, through `reviewer.run-external-checks` | the raw-capture paths the workflow passes |
| Standalone | the user, invoking the reviewer or the script directly | the directory the user names, with a minimal `run.md` under it |

Paths are always supplied by the caller — the user is the caller too, at a standalone invocation.
This tool derives no path from repository layout and keeps no location of its own to fall back on:
asked to run with none named, it asks for one and captures nothing until the answer arrives. The
export filename it receives is likewise the caller's, produced by the calling workflow's naming rule.

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

After the reviewer runs `reviewer.normalize-external-report` over the raw capture, a
`validation-report` instance exists for it — advisory, never carrying a blocking verdict. The
recommendations are then judged by `reviewer.gate-external-recommendations`.

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
2. Resolve this tool's settings from the user's local rules file (`## Skill settings` →
   `### validate-cv-enhancv`) and pass them to the script as explicit arguments. The script never
   reads the rules file itself.
3. Confirm the deliverable exists at the export path the flow produced, is a PDF, is at most 2 MB,
   and was rendered from the *final* document — a deliverable older than the last content change
   blocks the step.
4. Create nothing else and change nothing else. The step is read-only apart from its own captures.

**What "bound" means here — stated as goals, because a recipe would be wrong somewhere.** Two things
have to be true of the machine, and this file says only what must become *possible*, never which
release makes it so:

- **an interpreter that can drive a browser** — the one named by this tool's `python_interpreter`
  setting, or the one on the executable search path when no setting names one, with the automation
  package of the `playwright` dependency row importable *in that same interpreter*;
- **a browser build that driver accepts** — the engine `browser_engine` names, either as a build the
  driver manages itself or as the locally installed browser a `browser_channel` or
  `browser_executable` setting points at.

**Who may make them true: `setup-master.prepare-environment`, with the user's assent, item by
item.** It takes the two goals above verbatim, works out the means from what this machine actually
offers, and records what it did. It prescribes **no command sequence and no version** on purpose — a
fixed sequence presumes a network, a package manager, a shell allowed to reach out, and a machine
like the author's, and each of those presumptions fails somewhere. Neither this tool nor the
reviewer executing it installs anything or improvises a procedure of its own; an unbound dependency
is reported, not worked around.

**And preparation is never enough on its own: the requirement holds on every run.** The service
builds both the upload and the report with the page's own client-side code, so every execution of
this entry opens a live browser window and reaches the service host over the network. There is
nothing cached to replay and no warm state that carries from one run to the next. A session that
cannot reach the network, or that has nowhere to put a visible window — a sandboxed or unattended
shell is usually both — therefore cannot satisfy this entry however completely the machine was
prepared beforehand.

**In such a session the honest default is SKIPPED-manual**, and it is a designed outcome rather than
a gap for preparation to close: record the entry with the reason, hand over the *Manual fallback*
checklist below so the user can complete it from a session that has a display and a network, and let
the flow continue. Never a `Fail` verdict about the CV, never a red gate, and never an attempt to
substitute an HTTP request for the browser session.

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
| The runner reports the automation stack is not bound | the browser stack is missing for the interpreter running the script | close the gap through `setup-master.prepare-environment`, whose goal is the one *Environment preparation* states, or run the manual fallback; the entry is SKIPPED either way |
| The browser build cannot be launched | the engine's build is not installed, or a recorded browser binary does not resolve | install the engine build, or correct the `browser_executable` / `browser_channel` setting recorded for this machine |
| The upload UI never becomes ready | the page is slow, or a challenge is standing in front of it | raise the timeout, and run with a visible window so the challenge can be completed |
| A challenge appears and the run ends | the run was headless, or nobody completed the challenge in time | re-run with a visible window and a longer manual grace period (for example 180 seconds) |
| Processing never finishes | the service is slow or the report never rendered | raise the timeout; if it recurs, use the manual fallback and record the service as flaky in the run record |
| The capture contains a cookie wall, an error page or a login prompt | the submission never reached the report | record it as an unusable capture with the evidence; do not reconstruct what the report "would have" said |
| The capture is missing most of the expected checks | partial capture | mark it partial, say what is missing, and let the normalization treat it as a fragment |
| The input is rejected as too large | the file exceeds the 2 MB service limit | do not shrink the CV's content to fit — report it to the flow; the deliverable is the renderer's output, not this step's |
| A local policy forbids Chromium-based browsers | the default engine is not acceptable here | record `browser_engine: firefox` (or `webkit`) in this tool's settings |

## Bundled script

`scripts/run_enhancv.py`, beside this file — drives the service and writes the captures. It takes
explicit command-line arguments only, reads no rules or context file, and derives no path from
repository layout.

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

## User-context settings

Recorded under `## Skill settings` → `### validate-cv-enhancv` in the user's local rules file (see
contract `user-context`). All are optional; the machine-specific bindings of this tool's
dependencies belong here and nowhere else. Keys this file does not define are reported to the user,
never silently ignored.

| Key | Required | Values | Default | Meaning |
|---|---|---|---|---|
| `mode` | optional | `browser`, `manual` | `browser` | `manual` forces the manual fallback without attempting automation |
| `python_interpreter` | optional | path or name | the caller's `python3` | the interpreter that has the automation stack installed |
| `browser_engine` | optional | `chromium`, `firefox`, `webkit` | `chromium` | which engine the run drives |
| `browser_channel` | optional | channel name | none | launch a locally installed browser channel instead of the bundled build |
| `browser_executable` | optional | path or name | none | launch a specific browser binary; a bare name is resolved on `PATH` |
| `headless` | optional | `true`, `false` | `false` | `true` only for unattended automation the user asked for |
| `manual_wait_seconds` | optional | integer | `120` visible / `0` headless | grace period for completing a challenge |
| `timeout_ms` | optional | integer | `180000` | maximum wait for the upload UI and for processing |
| `service_url` | optional | URL | the service URL above | override when the service moves |
| `max_input_mb` | optional | number | `2` | override when the service's limit changes |

## Dependencies

| Name | Kind | Needed for | Required / optional | When unbound |
|---|---|---|---|---|
| `python3` | tool | Running the bundled runner script. Probed **at the interpreter recorded as `python_interpreter`** in this tool's settings subsection when one is recorded, and on the executable search path otherwise; the evidence names which one answered. Answers to `--version`. Recording it is the reliable form, and more so once this package is installed rather than cloned: the `playwright` row below has to be importable in the *same* interpreter that runs the script, and whichever interpreter happens to come first on a search path is frequently not the one the user prepared. | required | The check runs manual — the reviewer follows the manual fallback and records the entry as SKIPPED-manual with those instructions. |
| Browser automation | capability | Driving a real browser session through the service's client-side upload and report. | required | The entry runs SKIPPED with instructions; the manual fallback in the runbook is the documented substitute, and the flow continues. |
| `playwright` (Python package, `playwright.async_api`) | tool | The concrete binding of browser automation used by the bundled script. It is a module, not an executable, so it is probed **inside the same interpreter as the `python3` row** — the check is `<that interpreter> -c "import playwright.async_api"`, which exits 0 when the package is importable there. | required | The script reports outcome `skipped` with the binding instructions and the manual fallback; nothing is submitted and nothing crashes. |
| A Playwright browser build — `chromium` (default), or `firefox` / `webkit` | tool | Rendering the service page and letting the user complete challenges. Not an executable on the search path either: it is probed **at the `browser_executable` recorded** in this tool's settings when one is recorded, and otherwise through the driver in the same interpreter as the two rows above; the evidence names which build answered. | required | The script reports outcome `skipped` naming the engine that could not be launched; install the engine build or record a `browser_channel` / `browser_executable` binding. |
| Network access to the service host | capability | Reaching the checker at all. | required | The run ends `not-completed` with the diagnostic capture; the manual fallback applies from a machine that can reach the service. |
| An interactive desktop session (a visible browser window) | capability | Completing the service's human-verification challenges, which is the default mode. | required | The run may be attempted headless (`headless: true`), but a challenge then cannot be completed and the run ends `not-completed`; the manual fallback on a machine with a display is the documented path. |
