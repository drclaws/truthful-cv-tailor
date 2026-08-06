# Contract: external-gate-decision

Version: 1.0

## Purpose

External validation services are advisory. This artifact is where their advice is **judged**: each
recommendation gets an explicit verdict and a destination, and the document only ever changes through
a decision recorded here.

Without this gate, an external score becomes a target and a keyword suggestion becomes a claim. That
is the failure mode the contract exists to prevent.

## Status values

- `complete` — every recommendation has a verdict and the final recommendation is stated;
- `blocked` — one or more items need a user decision (`MANUAL_REVIEW`) before the flow can proceed.

## Envelope

The common envelope applies. `inputs:` names every normalized external report gated here (with
revisions), the document under review, the truthfulness check report, the evidence sources and the
constraints ledger.

## Verdicts

Every recommendation from every gated report receives exactly one:

| Verdict | Meaning | Destination |
|---|---|---|
| `APPLY` | Safe and supported as stated. | The writer's edit pass. |
| `APPLY_WITH_REWRITE` | The underlying point is useful, but the wording must be made truthful. The rewritten wording is given here. | The writer's edit pass, using the rewrite. |
| `GAP_ONLY` | A real requirement, but the candidate's evidence does not support it. | The gap report. Never the document. |
| `REJECT` | Irrelevant, unsafe, misleading, or harmful. | Nowhere, with the reason recorded. |
| `MANUAL_REVIEW` | The decision needs the user. | The user; the run is blocked on it. |

## Sections

### `## Scope`

Which reports were gated, from which services, against which revision of the document, and which
prerequisite gates were green before external checks ran.

### `## Decisions`

The per-recommendation table — the substance of this artifact:

| Column | Rule |
|---|---|
| id | Identifier the edit pass and the gap report can cite. |
| source | The service and the finding it came from. |
| recommendation | What was suggested, as stated. |
| verdict | One of the five above. |
| rationale | Why. For anything other than `APPLY`, this names the rule or the missing evidence. |
| rewrite | For `APPLY_WITH_REWRITE`: the exact truthful wording to use. |

### Grouped views

The same decisions, grouped for the consumers who act on them:

- `## Accepted changes` — the `APPLY` items;
- `## Changes requiring truthful rewrite` — `APPLY_WITH_REWRITE`, with the rewritten wording;
- `## Gaps to document but not add` — `GAP_ONLY`, each with the reason it cannot be claimed;
- `## Rejected suggestions` — `REJECT`, each with its rejection reason;
- `## Manual review items` — `MANUAL_REVIEW`, each stating precisely what the user must decide.

### `## Final recommendation`

One of:

- **Proceed** — send as is;
- **Revise** — apply the accepted and rewritten changes, re-check, then send;
- **Do not send** — the document is not ready; the reasons are listed.

### `## Constraint proposals`

Guardrails discovered while gating — in particular recurring advice from external services that
would push toward unsupported claims and should be pre-empted in future runs. See
`artifact-conventions.md`. `None.` when there is nothing to propose.

## Rules

- **Truthfulness overrides external advice, always.** A suggestion that conflicts with the
  truthfulness check loses, regardless of the score attached to it.
- **No unsupported additions**, of any kind: skills, tools, metrics, domain experience, leadership or
  ownership claims. A keyword suggestion is acceptable only when the underlying experience is
  supported by evidence.
- **Formatting suggestions are usually safe** — unless they reduce readability or extraction quality.
- **Never accept a suggestion that would restyle the rendered template merely to make content fit.**
  A fit problem is solved by revising validated content, moderately, preserving the strongest
  supported evidence, and reusing any space freed for the strongest target-relevant material.
- **Scores are not truth and are not a verdict.** They may inform a rationale; they never justify one
  on their own.
- **Applying anything means re-checking.** Any applied recommendation triggers a fresh truthfulness
  check of the edited document.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | `reviewer.gate-external-recommendations` |
| Consumers | `experience-writer` (edit pass), `vacancy-analyst` (gap analysis), the user, `knowledge-bank-curator` (via constraint proposals) |
