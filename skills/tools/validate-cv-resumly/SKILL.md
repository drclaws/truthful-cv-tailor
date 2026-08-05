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
  authority of its own. It is executed by the **reviewer** role
  (`roles/reviewer/capabilities/run-external-checks.md`), and the reviewer's invariants
  (`roles/reviewer/ROLE.md`) apply in full, always, and win over anything written here.
- **External scores are never truth.** Everything the service reports is recorded as *that service's
  claim* — advisory input to a later decision, never a verdict about the CV and never a gate.
- **It runs last.** An external check may start only after the run's internal checks and render gates
  are green. Asserting that gate is the reviewer's job, not this skill's; this skill assumes it has
  already been asserted and must not be used to peek at a service "just to see what it says".
- **It never edits anything.** No edit to the CV, the rendered file, the export, the knowledge bank or
  the constraints ledger originates here. It produces one thing: a verbatim raw capture.
- **It does not judge.** Normalization is `roles/reviewer/capabilities/normalize-external-report.md`;
  the binding decision is `roles/reviewer/capabilities/gate-external-recommendations.md`. This skill
  hands back raw material and stops. It never chains those steps itself.
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
report, and only `curator.maintain-constraints` writes the ledger.

## User-context settings

Recognized keys for the `### validate-cv-resumly` subsection under `## Skill settings` in the user's
local rules file (shape and resolution: `contracts/user-context.md`). Unrecognized keys are reported
at preflight, never silently ignored.

| Key | Required | Default | Meaning |
|---|---|---|---|
| `service_url` | required | none — the repository pins no entry point | The service page where a CV is submitted for checking. Absent ⇒ ask the user at preflight; unanswered ⇒ the entry runs SKIPPED with instructions. |
| `account` | optional | none | Which account the user signs in with, or `none` when the service can be used without signing in. **Record which account, never a sign-in secret** — this file is plaintext even though it is gitignored. Secrets stay in the browser's own credential store. |
| `manual_wait_seconds` | optional | `120` | How long to let the service process a submission before treating a stalled page as *not completed*. Raise it on a slow connection. |
| `capture_format` | optional | `markdown` | The form of the raw capture: a faithful text transcription of the report (`markdown`), or a saved page (`html`). |
| `extra_captures` | optional | none | Additional verbatim captures to save alongside the text, e.g. `screenshot`. Useful when the report is partly graphical. |
| `notes` | optional | none | Free-text local notes about this service on this machine (interface quirks, where the report opens). Honoured as guidance; never as an override of the trust policy. |

Example of the subsection, with placeholders only:

```markdown
### validate-cv-resumly
- service_url: <the service page where a CV is submitted>
- account: <the account used to sign in, or "none">
- manual_wait_seconds: 120
- capture_format: markdown
- extra_captures: screenshot
```

## Dependencies

| Field | Entry 1 | Entry 2 | Entry 3 | Entry 4 |
|---|---|---|---|---|
| **name** | Human operator (an interactive session with the user present) | Web browsing with file upload | File writing at the paths passed | Screen or page capture |
| **kind** | `capability` | `capability` | `capability` | `capability` |
| **needed for** | Performing the whole procedure: opening the service, signing in if it asks, submitting the PDF and the job description, completing any human challenge, reading the report and transcribing it | Reaching the service's public web interface and uploading a local PDF from the export path | Saving the raw capture at `raw_capture_path` (and the minimal `run.md` on a standalone run) | Saving an additional verbatim capture when `extra_captures` asks for one, or when the report is partly graphical |
| **required / optional** | required | required | required | optional |
| **when unbound** | No interactive user (an unattended or batch run) ⇒ the entry is recorded **SKIPPED-manual** with the checklist from *Manual procedure* below, so the user can complete it later. The flow continues; this is never a failure and never a red gate. | No browser reaching the service ⇒ **SKIPPED** with instructions: what is missing, what it is needed for, and the manual procedure to run once it is available. | The operator saves the capture themselves and reports its path; the entry counts as executed only once the capture exists at the assigned path, otherwise it is **SKIPPED-manual**. | The text transcription alone is sufficient; record in the capture that a graphical element could not be captured verbatim. |

**No script, and therefore no script dependencies.** This skill bundles no automation, so it requires
no language runtime, no browser-automation driver and no browser engine of its own — unlike an
automated external validator. The only "runtime" is a person with a browser.

**Not a dependency, but a precondition:** `service_url` recorded in user context (see above). A
missing setting is resolved by asking the user at preflight; it is not an environment binding and does
not appear in the setup-time dependency matrix.
