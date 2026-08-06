# Contract: gap-report

Version: 1.0

## Purpose

The gap report is the honest account of **what this application does not have**: which requirements
the evidence does not support, how the document handled them without pretending otherwise, what the
candidate should be ready to say in an interview, and which external recommendations were refused and
why.

It is application-specific and backward-looking with respect to this run. Improving the underlying
evidence is a different artifact (`bank-update-brief`).

## Status values

- `complete` — every gap identified in the run is accounted for.

## Envelope

The common envelope applies. `inputs:` names the requirements profile, the evidence map, the
validation reports, the fit report, the external gate decision when one exists, and the final
document with its revision.

## Sections

### `## Truth-based gaps`

Requirements from the vacancy with no supporting evidence in the candidate's canonical sources. Each
entry states the requirement (citing its identifier), what **kind** of experience is missing —
technology, domain, ownership level, seniority — and how central it is to the role.

Only genuine gaps, each grounded in an evidence-map `None` entry, a constraint flag, or a fit-report
finding. This section never proposes adding an unsupported claim.

### `## How the CV handles these gaps`

For each gap: how the document is positioned. Which transferable evidence was used instead, which
target keywords were deliberately omitted, and which wording decisions kept the document honest while
staying as relevant as possible.

This section is what makes the document's omissions legible — to the user reviewing it, and to a
future run asking why something is absent.

### `## Interview follow-up topics`

For each significant gap, an honest answer the candidate can prepare: what **is** owned
professionally, how it transfers, and an explicit acknowledgement of what is not held.

Hard rules: never draft an answer that claims experience the candidate does not have; never suggest
implying production experience from learning or side projects; where the honest answer is "I have not
done this", say so and pair it with the nearest real experience.

### `## External GAP_ONLY findings`

Items the external gate marked `GAP_ONLY`: important requirements external services flagged that
cannot be added to the document because the evidence does not support them. Each states the service
it came from, the suggestion as made, and why it was routed here instead of into the document.

Omitted when no external checks ran; the run manifest already records that they did not.

### `## Rejected recommendations`

Every suggestion refused, from any source — external services, keyword recommendations, scoring
hints — with its rejection reason: it would require claiming unsupported experience, inflating
ownership, rewriting a truthful job title, or otherwise crossing a truthfulness rule.

Recorded so the same suggestion is not silently re-litigated in the next run.

### `## Constraint proposals`

Guardrails the gaps suggest — typically "do not claim <X> unless a canonical source adds it" for a
gap that keeps being pressed by targets in this market. See `artifact-conventions.md`. `None.` when
there is nothing to propose.

## Rules

- Gaps come from findings already recorded elsewhere in the run, not from fresh speculation.
- Never suggest adding an unsupported claim to the document.
- Never suggest preparing a dishonest interview answer.
- A gap is stated as a fact about the evidence, not as a judgement about the candidate.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | `vacancy-analyst.gap-analysis` |
| Consumers | the user, `knowledge-bank-curator` (bank-update brief and constraint ingestion) |
