# Contract: recruiter-signals

Version: 1.0

## Purpose

Recruiter signals are what the **conversation** revealed that the vacancy text does not say: what was
emphasized, what the hiring manager appears to care about, which pain points the team has, and what
must stay out of the document.

The profile says what is required. The signals say what will actually land.

## Status values

- `complete` — the available recruiter and people inputs have been read;
- `skipped` — no recruiter or people inputs exist for this run. The artifact still exists, saying so,
  because "there was no conversation" is information the fit report and the writer both need.

## Envelope

The common envelope applies. `inputs:` names the recruiter, people and company sources by their
`source-audit` identifiers.

## The hard rule of this contract

**Signals shape emphasis and positioning. They never create candidate facts.**

Nothing recorded here licenses a claim in a document. Where a signal points at experience the
candidate may have, it points — the claim itself must come from candidate evidence. Where the
candidate made a statement about themselves in the conversation, it is recorded as a **self-report**
and marked as such; a self-report is a lead for the bank-update brief, never a source for a CV
bullet.

Nothing is invented. A signal that cannot be traced to a passage in a source is not a signal.

## Sections

### `## What was emphasized`

What the recruiter actually stressed — repeated, returned to, or spent time on. Each item cites the
passage it comes from.

### `## What the hiring manager likely cares about`

The priorities behind the conversation, marked `(inferred from …)`. Distinct from the section above:
that one records what was said, this one interprets it.

### `## Team pain points`

The problems the team is trying to solve by hiring: what is currently missing, breaking, slow, or
unowned. These are the strongest positioning material a run gets, because they say what "useful"
means to this employer.

### `## Business context`

Stage, pressures, deadlines, funding, market position, growth or contraction — anything that explains
why this role exists now.

### `## Candidate concerns and objections`

Doubts raised in the conversation, explicitly or by implication: about seniority, domain, tooling,
location, availability. Recorded so the document and the interview preparation can address them
directly instead of hoping they were imagined.

### `## Phrases worth mirroring`

Concrete wording from the conversation that is worth echoing when the candidate's evidence genuinely
supports it. Concrete phrasings only — vague soft-skill labels are excluded unless the notes give a
specific, job-relevant formulation that evidence can later support.

### `## Positioning guidance`

What the document should foreground, and in what order, given everything above.

### `## Do NOT include`

Everything that must stay out of the document: information given in confidence, topics the recruiter
warned against, framings that would misrepresent the situation, details that are not the employer's
business. This section is binding on the writer — it is a prohibition, not advice.

### `## Tag candidates`

Short scan signals worth preserving from the conversation: signals that would help a recruiter or
hiring manager scan the fit but do not deserve a summary sentence or an experience bullet. Not
limited to hard skills — system types, delivery context and concrete working modes qualify when they
are concrete and relevant. Vague soft-skill labels are excluded unless the notes supply concrete,
job-relevant phrasing.

Each candidate names the passage supporting it. As in the requirements profile, candidate-side
support is verified later; nothing here reaches a rendered document unverified.

### `## Constraint proposals`

Guardrails discovered in the conversation — a self-report that must not be mistaken for canonical
evidence, a topic the notes say to avoid. See `artifact-conventions.md`. `None.` when there is
nothing to propose.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | `vacancy-analyst.extract-recruiter-signals` |
| Consumers | `experience-writer`, `vacancy-analyst` (fit scoring, gap analysis), `reviewer`, `knowledge-bank-curator` (leads for the bank-update brief) |
