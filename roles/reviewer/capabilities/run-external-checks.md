# Capability: reviewer.run-external-checks

## Purpose

Runs the **EXTERNAL entries of the registered validation set** — checks performed by third-party
services rather than by rules in this repository — and captures their raw output for later
normalization.

This capability is **gated**: it may run only after the internal checks and the render gates of the
run are green. External services see the finished deliverable; sending them anything earlier wastes
the submission and invites advice about problems that were already fixed.

It produces raw material only. It never normalizes, never judges, never applies anything, and never
touches the document.

## Inputs

| Parameter | Contract / description | Required |
|---|---|---|
| `external_entries` | the EXTERNAL entries of the user's registered validation set, each with its name, the path to its spec (`SKILL.md`), and any per-skill settings recorded for it | required |
| `deliverable` | the final rendered deliverable to submit, at the export path and name the calling flow's naming rule produced | required |
| `document` | the final document the deliverable was rendered from — read only to confirm the two match | required |
| `job_inputs` | the job-side inputs an entry's spec may require (job description from the job dossier, requirements profile) | as declared by each entry |
| `run_manifest` | `run-manifest` — read for the gate statuses that open this gate | required |
| `raw_capture_paths` | the path pattern the flow assigned for each entry's raw capture(s) | required |
| `report_path` | where to write the run record of this capability | required |

## Outputs

| Parameter | Contract | Status values |
|---|---|---|
| `raw_capture_paths` | raw service output, stored verbatim — not a contract instance | — |
| `report_path` | `validation-report` describing the run of this step: per-entry outcome, not per-finding judgement | `complete`, `skipped`, `blocked` |

The run record lists, per entry: `executed` (with the raw capture paths), `SKIPPED` (with the reason
and the instructions to unblock it), or `not completed` (with what was attempted and what failed). It
carries no verdict about the document — judging is a later, separate step.

## Procedure

1. **Assert the gate.** Read the run manifest and confirm that every internal check of this run and
   every render gate is green:
   - the mandatory truthfulness check passed on the final document;
   - every registered internal validator that ran reports `Pass` or `Pass-after-edits` with its edits
     already applied, or is a recorded SKIPPED;
   - the render gates recorded in the render manifest are green.
   Any red or unknown status ⇒ write a `blocked` run record naming the gate that is not green and
   **stop without submitting anything**. Missing statuses count as unknown, not as green.
2. **Confirm the submission material.** The deliverable exists at the export path the flow passed, is
   the file type the entry's spec requires, is within any size limit the spec states, and was
   produced from the final document (a deliverable older than the last content change is a blocked
   condition, not a warning).
3. **For each external entry** — in parallel where the harness supports it, sequentially otherwise;
   the outcome must not differ:
   1. **Read the entry's spec.** It owns everything service-specific: required inputs, environment
      preparation, the interaction procedure, session and challenge policy, waiting behaviour, the
      manual fallback, troubleshooting, and where the raw output is expected.
   2. **Check its dependency bindings.** Every dependency the spec marks as required must be bound.
      Unbound ⇒ **SKIPPED** with instructions (below) — do not improvise a substitute path to the
      service.
   3. **Execute the spec's procedure** as written: prepare the environment, submit exactly the inputs
      the spec declares, follow its interaction policy (visible session, human-in-the-loop
      challenges, waiting) exactly. The reviewer executes the documented procedure; it never invents
      how to drive a service.
   4. **Capture the raw output verbatim** at the path the flow assigned — the report text, and any
      additional capture the spec declares. Raw captures are evidence of what the service said and
      are never edited, trimmed, summarized or corrected.
   5. **Record the outcome** for this entry.
4. **Write the run record** with the common envelope, listing every entry of the external set and its
   outcome, including the entries that were SKIPPED and why.
5. **Propose constraints** if the run surfaced a durable guardrail (for example a service that
   repeatedly demands an unsupported claim). Nothing to propose ⇒ `None.`
6. **Hand back** the list of raw captures. The flow decides what happens next; this capability does
   not normalize them and does not act on them.

## Rules

- **Gated, hard.** External checks are the last advisory step of a run. No submission before internal
  checks and render gates are green — no exceptions, no "just to see what it says".
- **Advisory only.** Nothing a service returns is truth, and nothing returned here is applied.
  Recommendations are judged in a separate, later step; keyword suggestions are never added to the
  document, here or anywhere, by this role.
- **Never modify the document, the deliverable, the bank or the ledger.** This capability writes only
  raw captures and its own run record.
- **The set is given, not chosen.** Unless the user says otherwise, every EXTERNAL entry of the
  registered set is attempted. The reviewer never adds an unregistered service and never silently
  drops a registered one.
- **The spec owns service specifics.** Environment preparation, interaction policy, waiting, and
  fallbacks are read from the entry's spec, never hardcoded in this capability and never carried over
  from another entry.
- **Submit only what the spec declares.** No extra artifacts, no additional personal data, no
  internal run notes. External services are third parties.
- **SKIPPED is a first-class outcome.** An entry whose dependencies are unbound is recorded as
  SKIPPED with instructions and never contributes a failure, a `Fail` verdict, or a red gate.
- **Manual-mode entries** (a spec whose procedure is performed by a person) produce a precise
  checklist derived from the spec: which file to submit, where, which options to choose, what to save
  and to which path so that a later step can normalize it. Record the entry as SKIPPED-manual, or as
  executed if the user completed it during the session and the raw output was saved.
- **No automatic re-runs.** After the document changes, this capability runs again only when the flow
  re-asserts the gate on the new revision.
- **No concrete tool or service names in this file.** The capability is generic over external
  entries; names live in the registered set and in each entry's spec.

## Failure and skip conditions

- **Blocked** — a gate is red or unknown; the deliverable is missing, stale, or of a form no entry
  accepts; the run manifest cannot be read. Nothing is submitted; the run record says which condition
  blocked it.
- **SKIPPED (unbound dependency)** — the run record states, for that entry: which dependency is
  missing, what it is needed for, how to bind it, and the manual procedure from its spec. The flow
  continues.
- **Not completed** — the service was reachable but the procedure did not finish (interface changed,
  submission rejected, an unattended human challenge, a timeout). Record what was attempted, the
  failure as observed, and the manual fallback from the spec. This is not a document defect and never
  produces a `Fail` verdict about the document.
- **Partial capture** — some output was obtained but the spec's expected captures are incomplete.
  Save what exists, mark it partial, and say what is missing so the normalization step does not treat
  a fragment as the whole report.
