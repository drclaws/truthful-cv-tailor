# Capability: reviewer.normalize-external-report

## Purpose

Converts the raw output of one external check into a `validation-report` instance, so that advice
from a third-party service can be read, compared and judged in the same envelope as every internal
check.

Normalization changes **form, not meaning**. The result says what the service said — reorganized,
attributed, and pre-triaged for the later gating step — with nothing added, nothing removed, and
nothing quietly reinterpreted.

A normalized external report is **advisory**. It never carries a blocking verdict about the document
and never opens or closes a gate: external scores are not truth, and the binding decision is made in
the separate gating step the flow invokes afterwards.

## Inputs

| Parameter | Contract / description | Required |
|---|---|---|
| `raw_capture` | the verbatim raw output of one external check, in whatever form it was captured (page capture, exported text, transcribed screenshot, text the user pasted from a manual run) | required |
| `entry_name` | the registered name of the external entry that produced it | required |
| `submitted_deliverable` | path and name of the file that was submitted | required |
| `document` | the document the deliverable was rendered from — read to locate what a suggestion refers to | required |
| `job_inputs` | the job description / `requirements-profile` submitted or referenced, when the service used one | optional |
| `report_path` | where to write the normalized report | required |

## Outputs

| Parameter | Contract | Status values |
|---|---|---|
| `report_path` | `validation-report` | the advisory (informational) status of the contract; never `pass` / `fail` |

One normalized report per raw capture. The raw capture is preserved unchanged alongside it, and the
normalized report cites it by path.

## Procedure

1. **Read the raw capture in full** and the document it refers to. Note anything the capture shows as
   incomplete (a truncated page, a missing section, a screenshot that cut off).
2. **Fill the report body** with these sections, in this order:
   - **Validator** — the registered entry name, plus the service's own naming of the check if the
     capture states it.
   - **Input files** — the deliverable submitted, and the job-side input, if any.
   - **Scores** — every measurement the service reported, each with the service's own label and its
     scale as the service stated it (for example machine-parse rate, match score, readability score,
     and any further scores it emits). Numbers are copied, never rescaled, normalized or averaged.
   - **Critical issues** — what the service claims would block machine parsing or human readability.
   - **Keyword gaps** — the keywords or skills the service claims are missing.
   - **Formatting issues** — what it says about layout, sections, file type, bullets, dates, tables,
     columns, icons or parsing.
   - **Content suggestions** — its suggestions for the summary, bullets, skills or positioning.
   - **Potentially unsafe suggestions** — every suggestion that would require adding a fact, tool,
     metric, certification, domain experience or seniority claim the document does not currently
     carry. This section exists even when the service framed such a suggestion as trivial.
   - **Recommended next actions** — one line per action, each pre-classified as exactly one of:
     `Safe formatting edit`, `Needs fact validation`, `Gap only`, `Reject`.
3. **Attribute everything.** Each entry is written as a claim of the service, with a short verbatim
   quote or a pointer into the raw capture, so a reader can check the normalization against the
   original.
4. **Mark the untranslatable.** Where the raw output is ambiguous, contradictory, or clearly
   truncated, quote it verbatim and write that its meaning is unclear. Never resolve it by guessing
   what the service probably meant.
5. **Write the report** with the common envelope, `inputs:` naming the raw capture and the submitted
   deliverable.
6. **Propose constraints.** A recurring trap this service sets (a claim it keeps pushing that the
   evidence does not support) is a useful `## Constraint proposals` entry. Nothing to propose ⇒
   `None.`
7. **Hand back.** The flow passes the normalized reports to the gating step; this capability judges
   nothing and applies nothing.

## Rules

- **Never add and never drop.** An issue the service did not report must not appear; an issue it did
  report must not disappear because it looks wrong. Where the reviewer disagrees, that belongs in the
  gating step, not in the normalization.
- **Scores are the service's claims.** Record them with the service's labels; never present them as a
  judgement of the candidate, never derive a verdict from them, never compare them across services as
  if they measured the same thing.
- **Triage is a hint, not a decision.** The four next-action labels speed up the gating step. They
  bind nobody: the gate assigns the real verdicts.
- **Flag the unsafe generously.** Any suggestion that could only be satisfied by a new claim goes to
  *Potentially unsafe suggestions*, even when it is phrased as a small wording tweak.
- **Preserve the raw capture.** It is never edited, replaced or deleted after normalization; the
  normalized report is derived from it and cites it.
- **Never edit the document** and never write any artifact other than this report.
- **One entry, one report.** Do not merge two services into one normalized report, and do not split
  one service's report unless it genuinely produced separate captures — consolidation happens in the
  gating step.
- **Partial input stays partial.** A fragment is normalized as a fragment, with its incompleteness
  stated in the report, never presented as a complete result.

## Failure and skip conditions

- **Blocked** — the raw capture is missing, empty, or unreadable. Report `blocked` naming the missing
  capture; do not reconstruct what the service "would have" said.
- **Unusable capture** — the capture exists but contains no report content (an error page, a login
  wall, an unfinished submission). Record it as such, with the verbatim evidence, and hand it back;
  the flow decides whether to re-run the external step.
- **Nothing to normalize** — the service returned a clean result with no issues. That is a valid
  normalized report: the sections exist and say so, and the run record shows the check completed.
- This capability is never a gate. It cannot produce a document failure and its status never blocks a
  flow on its own.
