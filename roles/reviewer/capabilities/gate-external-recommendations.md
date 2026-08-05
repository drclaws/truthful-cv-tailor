# Capability: reviewer.gate-external-recommendations

## Purpose

Decides what, if anything, external advice is allowed to change. Every recommendation collected from
the normalized external reports of a run receives exactly one verdict — **APPLY**,
**APPLY_WITH_REWRITE**, **GAP_ONLY**, **REJECT** or **MANUAL_REVIEW** — and the run receives one final
recommendation: **Proceed**, **Revise**, or **Do not send**.

This is the point where advisory input meets the truthfulness invariant, and the invariant wins:
**fact validation overrides external advice, always.** The gate decides; it never edits. Applying an
accepted item is the writer's work, and every applied item sends the document back through the
mandatory truthfulness check before it can be final again.

## Inputs

| Parameter | Contract / description | Required |
|---|---|---|
| `normalized_reports` | every normalized external `validation-report` of this run | required |
| `fact_check_report` | the `validation-report` of the mandatory truthfulness check on the final document | required |
| `internal_reports` | the `validation-report` of each registered internal validator that ran | required when any ran |
| `render_manifest` | `render-manifest` — the mechanical gate results | required |
| `document` | the final document under review | required |
| `knowledge_bank` | `knowledge-bank` — the evidence base | required |
| `constraints_ledger` | `constraints-ledger` | required when it exists |
| `evidence_map` | `evidence-map` | optional |
| `requirements_profile` | `requirements-profile` — to judge relevance of a suggestion to the target | optional |
| `report_path` | where to write the decision | required |

## Outputs

| Parameter | Contract | Status values |
|---|---|---|
| `report_path` | `external-gate-decision` | `complete`, `blocked` |

The decision records every recommendation with its verdict and its reason, and closes with the final
recommendation (`Proceed` / `Revise` / `Do not send`).

## Procedure

1. **Collect** every recommendation from every normalized external report, keeping its source entry
   and the service's own wording.
2. **Deduplicate across services.** The same recommendation raised by two services is one item that
   lists both sources. **Agreement between services is not evidence** — two services can be wrong in
   the same way, and neither of them has seen the candidate's sources.
3. **Judge each item** against, in this order: the truthfulness check findings, the constraints
   ledger (and any in-run constraint proposals), the evidence in the knowledge bank / evidence map,
   the target's requirements, and the mechanical readability of the deliverable. Assign exactly one
   verdict:
   - **APPLY** — safe and already supported. It introduces no new claim: a wording, ordering or
     structural change, or a keyword whose underlying experience the evidence carries. Every APPLY
     names the evidence that supports it; an APPLY without a citation is not an APPLY.
   - **APPLY_WITH_REWRITE** — the underlying point is useful, but the suggested wording would
     overstate what the evidence carries. Record the *boundary* the rewrite must respect (what must
     remain true, what must not be implied). The reviewer states the constraint; the writer writes
     the text.
   - **GAP_ONLY** — important to the target but unsupported by evidence. It goes to the gap report and
     never into the document. This is the default home of every suggestion that would require a new
     fact.
   - **REJECT** — irrelevant, unsafe, misleading, harmful, forbidden by a constraint, contradicted by
     the truthfulness check, or damaging to machine or human readability. Record the reason.
   - **MANUAL_REVIEW** — the decision belongs to the user: a fact only the user can confirm, a
     genuine positioning trade-off, or evidence too ambiguous to settle here.
4. **Record the consequences** of the accepted set: which artifacts must be revised, that the writer
   applies the edits, that the mandatory truthfulness check must run again on the result, that the
   internal checks the edits could have affected must be re-run, and that the deliverable must be
   re-rendered and re-gated.
5. **Issue the final recommendation:**
   - **Proceed** — no APPLY or APPLY_WITH_REWRITE item is pending, no MANUAL_REVIEW item is
     unresolved, the truthfulness check passed on the current revision, and the internal and render
     gates are green.
   - **Revise** — at least one APPLY or APPLY_WITH_REWRITE item is to be applied. The run continues
     through the edit → re-check → re-render loop.
   - **Do not send** — a blocking truthfulness problem stands, an unresolved MANUAL_REVIEW item
     affects a claim in the document, or a mechanical gate on the deliverable is broken.
6. **Write the decision** with the common envelope, listing items grouped by verdict, each with its
   source entry, the evidence or rule that decided it, and its consequence.
7. **Propose constraints.** A rejected recommendation that will recur — a service that keeps pushing
   an unsupported metric, a keyword the evidence will never carry — becomes a `## Constraint
   proposals` entry so the ledger can pre-empt it next time. Nothing to propose ⇒ `None.`

## Rules

**Truth first**

- **Fact validation overrides external advice.** Where a service contradicts the truthfulness check,
  the truthfulness check wins and the item is REJECT or GAP_ONLY.
- Never accept an item that would add an unsupported skill, tool, technology, metric, certification,
  domain experience, seniority level, leadership or ownership claim.
- A keyword suggestion may be accepted **only** when the underlying experience is supported by
  evidence; otherwise it is GAP_ONLY, never a wording workaround.
- Advisory scores never drive a verdict. A low score is a prompt to look, not a reason to change
  anything, and a high score never licenses an unsupported claim.
- Every accepted item is traceable: source entry → evidence citation → required change.

**Formatting and fit**

- Formatting suggestions are usually safe, and are accepted only while they preserve both machine
  extraction and human readability. A suggestion that trades extraction quality for appearance is
  REJECT.
- **Never accept a suggestion that changes template style, geometry, margins, font sizes, spacing,
  colors, column widths, section styling or visual components merely to make content fit.** The
  template is not a fitting tool.
- Page-fit recommendations follow the content-first fit policy owned by the render operation: revise
  validated content moderately first — merge overlapping bullets, drop lower-value detail, shorten
  wording, keep target-relevant supported evidence — and reuse any freed space for the strongest
  target-relevant experience detail. The gate records this direction; it does not perform the
  revision.

**Independence**

- The gate never edits the document, the deliverable, the bank or the ledger. It writes one decision
  artifact.
- Every item gets exactly one verdict and a reason. "No comment" is not an outcome; an item nobody can
  decide is MANUAL_REVIEW.
- An unresolved MANUAL_REVIEW item makes `Proceed` impossible.
- Nothing accepted here is final until the mandatory truthfulness check has re-run on the edited
  document.
- Only this run's artifacts, the knowledge bank and the repository definitions are consulted. Another
  run's decisions are never precedent.

## Failure and skip conditions

- **Blocked** — the truthfulness report or the render manifest is missing, or the normalized reports
  cannot be read. Without the truthfulness check there is nothing to override external advice with,
  so no gating happens: report `blocked` and stop.
- **No external reports** — every external entry was SKIPPED or none is registered. The gate is not
  run at all; if the flow invokes it anyway, it records that there was nothing to judge and issues no
  recommendation of its own. The absence of external checks never blocks a run.
- **A service disagrees with an internal check** — that is not a failure condition. Record both, and
  decide by evidence; the internal truthfulness finding prevails.
- **Unresolved MANUAL_REVIEW items** are escalated to the user through the flow; the decision remains
  `Do not send` or `Revise` until they are settled.
