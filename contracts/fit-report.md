# Contract: fit-report

Version: 1.0

## Purpose

The fit report evaluates **candidate against vacancy**: how well the evidence matches what this
employer asks for, where the strength is, where the risk is, and whether applying is worth it.

It is **informational**. It is not a quality check on a document and it never blocks anything by
itself. A flow may declare an escalation rule that reads this report — "pause and ask the user when
the verdict is negative or the score is below <threshold>" — but the threshold and the pause belong
to the flow, not to this contract.

## Status values

- `informational` — the only status this contract uses.

There is deliberately **no** `pass`, `fail` or `pass-after-edits`. Checking a document against rules
and sources is a different job, done by a different role, under a different contract.

## Input-format agnosticism

This contract does not prescribe where the candidate data came from. The scoring works from:

- the knowledge bank directly, or
- an evidence map for this vacancy, or
- an arbitrary existing CV supplied by the user.

**The header declares which was used**, because it changes how much the scores can be trusted: a
score derived from an arbitrary CV reflects that document, not the candidate's full evidence.

Keeping the report input-agnostic is deliberate — the same scoring serves flows that have no CV and
no evidence map at all, such as evaluating a vacancy before deciding to pursue it.

## Envelope

The common envelope applies. `inputs:` names the requirements profile, the recruiter signals, and the
candidate-data source actually used (with revision, where it has one).

## Sections

### `## Basis`

| Field | Meaning |
|---|---|
| candidate data format | `knowledge bank` · `evidence map` · `supplied CV` · a combination, named. |
| subject | The vacancy, and the document assessed when there is one (with revision). |
| limitations | What this basis cannot see — for example, that a supplied CV omits evidence the bank holds. |

### `## Scores`

Fixed weights, summing to 100:

| Dimension | Max |
|---|---|
| Must-have coverage | 40 |
| Responsibilities alignment | 20 |
| Seniority alignment | 15 |
| Domain alignment | 10 |
| Keyword alignment | 10 |
| Recruiter-signal alignment | 5 |

Each dimension is scored with a one-or-two-sentence justification citing the requirement identifiers
that drove it. The overall score is the sum, stated with the dimension breakdown — never as a bare
number.

Scoring rules:

- **No credit for unsupported claims.** A requirement met by a claim the evidence does not carry
  scores zero for that requirement.
- **Real experience is distinguished from keyword presence.** A term appearing in a document is not
  evidence of the experience behind it.
- **Recruiter-signal alignment is capped low on purpose.** Signals shape positioning; they cannot
  compensate for missing evidence.
- **Be critical.** An inflated score is worse than a low one: it costs the user an application.

### `## Strong matches`

Requirements met with genuinely strong evidence, each citing the evidence behind it.

### `## Partial matches`

Requirements met only partly — narrower, older, adjacent, or lower in ownership than asked. Each
states precisely what is present and what is not, since this is what interview preparation and
positioning both work from.

### `## Gaps`

Requirements with no supporting evidence, or whose evidence a constraint forbids using. Stated
plainly, without cushioning. The gap report develops these; here they are named and counted.

### `## Risks`

What could go wrong in this application beyond simple gaps: a screening filter the candidate fails, a
seniority mismatch in either direction, a domain distance the document cannot close honestly, a
recruiter-noted concern that will resurface, an over-tailoring risk.

### `## Positioning advice`

How to present the candidate for this target given the above: what to lead with, which transferable
evidence carries the most weight, which framing to avoid. Advice only — the writing decisions belong
to the writer under the `cv-document` contract.

### `## Tag-signal verification`

The verification half of the tag-signal handoff. For each tag candidate proposed by the requirements
profile or the recruiter signals: whether candidate evidence genuinely supports it, whether it helps a
hiring manager scan the fit, and whether it should be omitted as weak, misleading, redundant with
Skills/Summary/Experience, or unsupported.

A tag **never improves the score**. A signal only counts when the evidence behind it is real and
already visible in the candidate data this report was scored from.

### `## Should apply?`

One verdict, with a short justification:

- **Strong yes**
- **Yes, with positioning** — naming the positioning it depends on
- **Maybe** — naming what would decide it
- **Low ROI** — naming what makes it low

### `## Constraint proposals`

Guardrails discovered while scoring — most often a requirement the target invites the candidate to
over-claim. See `contracts/README.md`. `None.` when there is nothing to propose.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | `vacancy-analyst.score-fit` |
| Consumers | the user, `vacancy-analyst` (gap analysis), `knowledge-bank-curator` (bank-update brief), `experience-writer` (positioning advice, when the flow routes it there) |
