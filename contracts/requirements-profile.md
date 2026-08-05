# Contract: requirements-profile

Version: 1.0

## Purpose

The requirements profile is the structured reading of the vacancy: what the employer asks for, what
they appear to care about beyond the text, and which of those is written down versus inferred. It is
the target definition every later step aims at — evidence mapping queries it, the writer prioritises
against it, fit scoring measures against it, gap analysis subtracts from it.

## Status values

- `complete` — the vacancy has been read in full and every requirement captured;
- `blocked` — the job-side inputs are insufficient to produce a usable profile.

## Envelope

The common envelope applies. `inputs:` names the job-side sources read, by their `source-audit`
identifiers.

## The explicit / inferred rule

**Every item in this profile is marked `explicit` or `inferred`.**

- `explicit` — stated in a job-side source. The statement is quoted or closely paraphrased and its
  source identifier is given.
- `inferred` — read between the lines. Marked `(inferred from <source and passage>)`, with the
  reasoning stated in one clause.

Requirements are never invented. A responsibility that is neither stated nor supportable by a named
passage does not belong in the profile at all — not even as an inference.

## Sections

### `## Role`

Role title as advertised, seniority level as advertised, and — separately — the seniority the text
actually implies when the two differ (marked inferred). Employment type, location and working model
when stated.

### `## Company context`

What the employer does, stage and scale, the team the role sits in, and anything in the sources that
shapes what "a good candidate" means here. Drawn from job-side sources only.

### `## Must-have requirements`

Requirements the vacancy presents as necessary. One entry per requirement, each with a short stable
identifier (`R1`, `R2`, …) that the evidence map, the fit report and the gap report all cite. Each
entry carries the requirement as stated, its explicit/inferred marking, and — where the vacancy
bundles several things into one line — the components separated out, because evidence is found per
component, not per sentence.

### `## Nice-to-have requirements`

The same shape, for requirements presented as preferred rather than necessary. Kept distinct: they
score differently and they are not gaps in the same sense.

### `## Responsibilities`

What the person will actually do. Separate from requirements: a responsibility describes the work,
a requirement describes the bar for being considered. Same identifier and marking discipline.

### `## Keyword sets`

Three grouped lists, each entry traceable to where it appears in the sources:

- **technical** — languages, systems, tools, platforms;
- **domain** — the business or problem space;
- **working-mode and soft** — collaboration, ownership, delivery expectations, only where the
  vacancy gives concrete wording.

Keywords are recorded as the vacancy phrases them; synonyms actually used in the sources are grouped
with the term they belong to. This is a record of the vacancy's vocabulary, not a target to be met —
whether the candidate can truthfully carry a keyword is decided later, against evidence.

### `## Hidden priorities`

What the vacancy appears to care about most, based on repetition, ordering, emphasis and phrasing
rather than on an explicit statement. Always `inferred`, always with the passage that suggests it.
This section is what lets a document be targeted rather than merely compliant.

### `## Screening filters`

Conditions likely to be applied before a human reads the application: hard requirements, location or
authorization conditions, years-of-experience thresholds, mandatory technologies. Marked explicit or
inferred. Recorded because failing a filter is a different problem from scoring low.

### `## Red flags and unclear requirements`

Contradictions inside the vacancy, requirements too vague to test evidence against, warning signs
worth raising with the user, and anything a later step should not guess at. An unclear requirement
recorded here is not silently interpreted downstream.

### `## Tag candidates`

Short hiring scan signals worth testing as compact render tags. Tag candidates are not limited to
hard skills: technical themes, system or problem types, working context and delivery context all
qualify when concrete and job-relevant. Each candidate is short, job-relevant, and marked as coming
from an explicit requirement or an inferred priority.

**Candidate truth is not decided here.** This section proposes; support against candidate evidence
is verified later, and no tag reaches a rendered document unverified.

### `## Constraint proposals`

Guardrails discovered while reading the vacancy — for instance a domain claim the vacancy invites
that the candidate evidence must not be stretched to meet. See `contracts/README.md`. `None.` when
there is nothing to propose.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | `vacancy-analyst.analyze-job` |
| Consumers | `knowledge-bank-curator` (evidence mapping), `experience-writer`, `vacancy-analyst` (fit scoring, gap analysis), `reviewer` |
