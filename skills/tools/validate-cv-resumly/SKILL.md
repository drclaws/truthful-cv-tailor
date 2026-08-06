---
name: validate-cv-resumly
description: External, manual-mode CV check on the Resumly service. A person submits the final rendered PDF together with the job description, saves the service's report verbatim as a raw capture, and hands it back; the reviewer normalizes and gates it. Advisory only — this skill never edits the CV and its scores are never truth.
---

# Tool skill: validate-cv-resumly

An **external** validation spec: the check is performed by a third-party web service, not by rules in
this repository. The service is driven **by hand** — this skill ships no automation script, so its
whole procedure is a checklist a person follows, written to be executable from this file alone.

## What this skill is, and what it is not

- **It is a procedure plus its parameters, never an actor.** It defines no agent and carries no
  authority of its own. It is executed by `reviewer.run-external-checks`, and the invariants of the
  role `reviewer` apply in full, always, and win over anything written here.
- **External scores are never truth.** Everything the service reports is recorded as *that service's
  claim* — advisory input to a later decision, never a verdict about the CV and never a gate.
- **It runs last.** An external check may start only after the run's internal checks and render gates
  are green. Asserting that gate is the reviewer's job, not this skill's; this skill assumes it has
  already been asserted and must not be used to peek at a service "just to see what it says".
- **It never edits anything.** No edit to the CV, the rendered file, the export, the knowledge bank or
  the constraints ledger originates here. It produces one thing: a verbatim raw capture.
- **It does not judge.** Normalization is `reviewer.normalize-external-report`; the binding decision
  is `reviewer.gate-external-recommendations`. This skill hands back raw material and stops. It
  never chains those steps itself.
- Repository-wide invariants (truthfulness, run isolation, tool abstraction, path/OS neutrality) apply
  as stated in `AGENTS.md`.

## Inputs

Every path is **passed in by the caller** — a workflow step, or the user invoking the skill directly.
This skill derives no path from repository layout and computes no filenames.

| Parameter | Contract / description | Required |
|---|---|---|
| `deliverable` | the final rendered CV as **PDF**, at the export path and under the export name the caller produced. This skill neither renames it nor derives its name: the naming rule belongs to the calling workflow. | required |
| `document` | the final CV markdown (`cv-document`, `status: final`) the deliverable was rendered from — read only to confirm the two match and to locate what a suggestion refers to. | required |
| `job_description` | the vacancy text from the run's job dossier (`job-dossier`), or the `requirements-profile` when the dossier text is unavailable. **This service requires a job description**: several of its checks are match-based and are meaningless without one. | required |
| `raw_capture_path` | where to save the verbatim capture of the service's report. Assigned by the caller. | required |
| `settings` | the recognized keys recorded for this skill in the user's context (below). | required (`service_url`); the rest optional |

## Outputs

| Output | Contract | Notes |
|---|---|---|
| raw capture at `raw_capture_path` | **not a contract instance** — verbatim service output | The only artifact this skill produces. Saved exactly as the service presented it; never edited, trimmed, summarized or corrected afterwards. |
| *(later, not by this skill)* normalized report | `validation-report`, advisory status | Written by `reviewer.normalize-external-report` from the raw capture. It never carries a blocking verdict. |
| *(later, not by this skill)* gate decision | `external-gate-decision` | Written by `reviewer.gate-external-recommendations` once every external report of the run is normalized. |

**Placement.** Invoked from a workflow, the capture goes to the path pattern the workflow assigned
(the CV workflow's pattern for external raw captures is `<run>/external/<validator>_raw.<ext>`, and
the normalized report that follows it `<run>/external/<validator>_report.md`). Invoked standalone, the
default is `outputs/validate-cv-resumly/<run-id>/` with a minimal `run.md`. Either way the caller
passes the path; the values above are defaults, not assumptions.

## Service parameters

| Parameter | Value |
|---|---|
| Service | Resumly — an external CV / ATS checker, reached through its public web interface. |
| Entry point | **Not pinned by this repository.** The user records it as `service_url` (below), because service entry points move and a stale URL committed here would be a silent trap. |
| Mode | **Manual only.** No automation script ships with this skill; a person performs every step. |
| Accepted input | **PDF only.** See *Limitations* — this system produces no other final format. |
| Job description | Required (pasted or uploaded as the service's interface asks). |
| Size limit | None declared by this skill. If the service rejects the file for size, that is a *not completed* outcome to record and report, never a reason to re-render differently on this skill's initiative. |
| Session | The user's own browser session. No credentials of any kind are stored in this repository or in this skill. |

### Checks expected from this service

The capture is expected to contain some or all of the following. A missing item is not a failure — it
is recorded as absent so that normalization does not present a fragment as a whole report.

- `ats_score`
- `formatting_issues`
- `keyword_gaps`
- `content_strength`
- `readability`
- `tailoring_suggestions`
- `missing_sections`
- `job_match_feedback`

## Trust policy

What this service is allowed to influence, and what it can never do. These are properties of the
**spec**; enforcing them is the reviewer's gating step.

| Rule | Value |
|---|---|
| May suggest keywords | yes — and a keyword may be adopted **only** if the underlying experience is already supported by evidence |
| May suggest rewrites | yes — as suggestions to be re-written truthfully, never as text to paste |
| May suggest formatting changes | yes — unless the change would reduce readability, or would restyle the template merely to make content fit |
| May add facts | **no** |
| May add tools | **no** |
| May add metrics | **no** |
| May add certifications | **no** |
| May add domain experience | **no** |

| Trust property | Value |
|---|---|
| `score_is_advisory` | true — the score is the service's measurement, recorded as its claim; no verdict is ever derived from it |
| `recommendations_require_fact_validation` | true — nothing from this service reaches the CV without passing the truthfulness check |
| `run_last_after_local_gates` | true — internal checks and render gates must be green before submission |
| `unsupported_recommendations_go_to_gap_report` | true — an important but unsupported recommendation becomes a gap entry, never CV text |
| `final_cv_changes_require_internal_validation` | true — any applied recommendation triggers a fact re-check and a re-run of the internal checks it could have affected, then a re-render |

A recommendation this service keeps pushing that the evidence does not support is a good candidate for
a durable guardrail: it is proposed through the `## Constraint proposals` section of the reviewer's
report, and only `knowledge-bank-curator.maintain-constraints` writes the ledger.

## User-context settings

Recognized keys for the `### validate-cv-resumly` subsection under `## Skill settings` in the user's
local rules file (shape and resolution: contract `user-context`). Unrecognized keys are reported at
preflight, never silently ignored.

| Key | Required | Values | Default | Meaning |
|---|---|---|---|---|
| `service_url` | required | URL | none — the repository pins no entry point | The service page where a CV is submitted for checking. Absent ⇒ ask the user at preflight; unanswered ⇒ the entry runs SKIPPED with instructions. |
| `account` | optional | an account name, or `none` | none | Which account the user signs in with, or `none` when the service can be used without signing in. **Record which account, never a sign-in secret** — this file is plaintext even though it is gitignored. Secrets stay in the browser's own credential store. |
| `manual_wait_seconds` | optional | integer seconds | `120` | How long to let the service process a submission before treating a stalled page as *not completed*. Raise it on a slow connection. |
| `capture_format` | optional | `markdown`, `html` | `markdown` | The form of the raw capture: a faithful text transcription of the report (`markdown`), or a saved page (`html`). |
| `extra_captures` | optional | capture kinds, e.g. `screenshot` | none | Additional verbatim captures to save alongside the text, e.g. `screenshot`. Useful when the report is partly graphical. |
| `notes` | optional | free text | none | Free-text local notes about this service on this machine (interface quirks, where the report opens). Honoured as guidance; never as an override of the trust policy. |

Example of the subsection, with placeholders only:

```markdown
### validate-cv-resumly
- service_url: <the service page where a CV is submitted>
- account: <the account used to sign in, or "none">
- manual_wait_seconds: 120
- capture_format: markdown
- extra_captures: screenshot
```

## Manual procedure

Performed by a person, start to finish. Follow the steps in order; each one names what it produces.

1. **Confirm the check may run at all.** The run's internal checks and render gates must already be
   green, and the PDF must be the one rendered from the final document — not an earlier build.
   Invoked from a workflow, the reviewer has asserted this before handing the step over; invoked
   standalone, ask the user to confirm it explicitly. Not green, or unknown ⇒ **stop and report**;
   nothing is submitted. *Produces: a go / no-go decision.*
2. **Collect the inputs.** The `deliverable` PDF at the export path, the final `document`, the
   `job_description` text, the `raw_capture_path` to save into, and the recorded settings. Anything
   missing ⇒ stop and ask; do not substitute a similar file and never take an input from another run.
   *Produces: the working set for this submission.*
3. **Prepare the environment.** Open a normal, **visible** browser window and go to the recorded
   `service_url`. Sign in with the recorded `account` only if the service asks for it. No `service_url`
   recorded ⇒ ask the user; unanswered ⇒ record **SKIPPED** with these instructions and stop.
   *Produces: the service's submission page, ready.*
4. **Submit.** Upload the PDF exactly as it is — same file, same name, no re-export, no editing, no
   renaming. Then provide the job description the way the interface asks (paste or upload). Submit
   **nothing else**: no run notes, no knowledge-bank extracts, no additional personal data. The
   service is a third party. *Produces: an accepted submission.*
5. **Wait for the result.** Give the service up to `manual_wait_seconds` (default 120) to finish
   processing, watching for its completion signal rather than assuming a fixed delay.
   *Produces: a finished report, or a stall to troubleshoot.*
6. **Complete any human challenge yourself**, in the open window — a captcha, a consent dialog, an
   email confirmation. The check is manual precisely so a person is present for this.
   *Produces: an unblocked session.*
7. **Read the whole report.** Expand every collapsed panel, open every tab and scroll to the end
   before capturing anything: partial reports normalize into partial conclusions.
   *Produces: the complete report on screen.*
8. **Save the capture verbatim** at `raw_capture_path`, in the recorded `capture_format`. Copy every
   score with the service's own label and its own scale, every reported issue and every suggestion, in
   the service's own words. Do not correct, re-order, translate, summarize or improve anything — a
   capture is evidence of what the service said. Note explicitly which of the *checks expected* are
   absent, and mark anything truncated or purely graphical. Save any `extra_captures` alongside it.
   *Produces: the raw capture — the only artifact of this skill.*
9. **Record the outcome** for the reviewer's run record: `executed` with the capture paths;
   **SKIPPED-manual** with the reason and this checklist; or **not completed** with what was attempted
   and what was observed to fail. A service that failed is never a defect of the CV.
   *Produces: the per-entry outcome line.*
10. **Stop.** Hand back the capture paths and nothing else. Do not act on any advice, do not edit the
    CV or the export, do not add suggested keywords, do not normalize and do not judge — the reviewer's
    normalization and gating steps do that next, in that order. *Produces: the handover.*

### Capture skeleton

A short provenance header, then the service's text untouched. The header is written by the operator
and is provenance only — it never becomes an edit to what the service said.

```markdown
Service: Resumly (<service_url>)
Captured: <ISO-8601 date/time>
Submitted deliverable: <path/name of the PDF exactly as submitted>
Job description submitted: <path or reference of the text provided>
Expected checks not present in this report: <list, or "none">
Capture completeness: complete | partial — <what is missing and why>

--- verbatim service output below ---
<everything the service reported, unaltered>
```

## Runbook

### Environment preparation

- A normal, visible browser session driven by a person. Nothing headless, nothing unattended: this
  skill has no automation to run unattended.
- The recorded `service_url`, and the recorded `account` if the service requires signing in. Sign-in
  secrets live in the browser's own credential store — never in this repository, never in the user's
  rules file, never in the capture.
- The export directory reachable from the browser's file picker, so the PDF can be uploaded from where
  the render step actually wrote it.
- The job description text at hand, from the run's job dossier.

### Service interaction

- One submission per check. Re-submitting the same PDF to compare scores tells nothing: the numbers
  are a third party's measurement, not a measurement of truth.
- Submit the deliverable unchanged. If it looks wrong (stale, misnamed, not the final render), stop and
  report it — repairing it is the caller's business, not this skill's.
- Keep the job description as the vacancy states it. Do not trim it to improve a match score.
- Anything the interface offers beyond checking — auto-rewrite, "fix my CV", template conversion,
  applying suggestions in place — is **out of scope and must not be used**. This skill collects a
  report; it never lets a service touch the document.

### Waiting and human challenges

- Default wait before treating a page as stalled: `manual_wait_seconds`, 120 by default. On a slow
  connection, 180 is a reasonable single retry value; record the change under `manual_wait_seconds`
  rather than improvising it every run.
- Human challenges (captcha, consent, confirmation link) are completed by the person in the open
  window. There is no policy for solving them automatically, and none may be invented.
- A challenge that repeats after two honest attempts is a **not completed** outcome, not a reason to
  work around the service.

### Manual fallback

This skill is already the manual path — its fallback is **asynchronous completion**, used when the
person cannot finish during the current session (no interactive user, the service is unreachable, a
sign-in wall the user has to resolve on their own time):

1. Record the entry as **SKIPPED-manual** with the reason.
2. Hand the user a checklist derived from *Manual procedure*: which file to submit, where (the
   recorded `service_url`), what else to provide (the job description), what to save, and to exactly
   which path (`raw_capture_path`).
3. The flow continues. A SKIPPED external check never fails a run, never produces a `Fail` verdict and
   never turns a gate red.
4. When the user later completes the submission and saves the capture at that path, the normalization
   step can run over it exactly as if it had been captured during the session; the gating step follows.

### Troubleshooting

| Symptom | What to do |
|---|---|
| The page stalls past `manual_wait_seconds` | Retry once with a longer wait (e.g. 180) and record the new value in settings. Still stalled ⇒ **not completed** + the asynchronous fallback. |
| The service refuses the file (size, parse error, upload error) | Record the refusal message verbatim as the outcome. It is a submission problem, not a CV defect, and it never produces a verdict about the document. Report it back to the caller. |
| The service demands a format this system does not produce | Record **not completed**, quote the demand, and report it to the user. Do **not** invent a conversion step — see *Limitations*. |
| A sign-in wall or paywall appears and no `account` is recorded | Ask the user. Unresolved ⇒ **SKIPPED** with instructions; never create an account, never pay, never enter someone else's session on the user's behalf. |
| A human challenge loops | Complete it in the visible window; after two honest attempts, **not completed**. |
| The report is partly graphical (gauges, charts) | Transcribe the numbers and labels as text, save a `screenshot` under `extra_captures`, and mark the capture `partial` with what could not be captured verbatim. |
| The report contradicts an internal check | Capture it exactly as it is. Contradictions are resolved by the gating step against evidence — never by editing the capture and never by re-submitting until the service agrees. |
| The entry point 404s or the interface was redesigned | Update `service_url` through `setup-master.update-settings`. If the service is gone, report that: never substitute a different service under this skill's name. |
| The service is down | **Not completed**, with the observation. External checks are advisory; a run is finished without them. |

## Limitations

- **PDF only — DOCX is not produced by this system.** The predecessor configuration of this validator
  preferred a DOCX upload. That format was dropped deliberately: PDF is the only final deliverable
  this repository produces, so a DOCX input simply does not exist here, and no conversion step is
  offered or permitted. Submit the PDF. If the service ever refuses PDF and requires a format this
  system does not produce, record the check as **not completed**, report the demand to the user, and
  let the user decide — do not convert, and do not improvise an export.
- **No automation, no unattended runs.** Without a person, this entry is SKIPPED-manual. That is a
  designed outcome, not a gap to be filled by scripting the service on the fly.
- **Scores are not comparable** — not between services, not between runs, not against internal checks.
  They are one third party's measurement, recorded as its claim.
- **Third-party exposure is real.** Only the deliverable and the job description are ever submitted.
  The knowledge bank, run notes, evidence maps and any other run artifact stay in the run.
- **Run isolation applies.** The inputs come from this run only; another run's export or capture is
  never submitted, cited or reused as a precedent.
- **The service may change without notice.** This file describes the intended interaction, not a
  contract with the vendor: a mismatch is reported to the user, never worked around by guessing.

## Dependencies

| Name | Kind | Needed for | Required / optional | When unbound |
|---|---|---|---|---|
| Human operator (an interactive session with the user present) | capability | Performing the whole procedure: opening the service, signing in if it asks, submitting the PDF and the job description, completing any human challenge, reading the report and transcribing it. | required | No interactive user (an unattended or batch run) ⇒ the entry is recorded **SKIPPED-manual** with the checklist from *Manual procedure* above, so the user can complete it later. The flow continues; this is never a failure and never a red gate. |
| Web browsing with file upload | capability | Reaching the service's public web interface and uploading a local PDF from the export path. | required | No browser reaching the service ⇒ **SKIPPED** with instructions: what is missing, what it is needed for, and the manual procedure to run once it is available. |
| File writing at the paths passed | capability | Saving the raw capture at `raw_capture_path` (and the minimal `run.md` on a standalone run). | required | The operator saves the capture themselves and reports its path; the entry counts as executed only once the capture exists at the assigned path, otherwise it is **SKIPPED-manual**. |
| Screen or page capture | capability | Saving an additional verbatim capture when `extra_captures` asks for one, or when the report is partly graphical. | optional | The text transcription alone is sufficient; record in the capture that a graphical element could not be captured verbatim. |

**No script, and therefore no script dependencies.** This skill bundles no automation, so it requires
no language runtime, no browser-automation driver and no browser engine of its own — unlike an
automated external validator. The only "runtime" is a person with a browser.

**Not a dependency, but a precondition:** `service_url` recorded in user context (see above). A
missing setting is resolved by asking the user at preflight; it is not an environment binding and does
not appear in the setup-time dependency matrix.
