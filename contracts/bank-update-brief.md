# Contract: bank-update-brief

Version: 1.0

## Purpose

The bank-update brief closes the loop between a run and the candidate's evidence. It reads everything
the run learned and turns it into concrete, answerable questions: which experience is genuinely
absent, which may exist but was never written down, and which is written down but too vaguely to
produce strong material.

Where the gap report is application-specific — this vacancy, this document, this interview — this
brief is forward-looking: it improves the evidence itself, for every future run.

## The hard rule of this contract

**This is a report and nothing else.** It never writes the knowledge bank and never writes the
constraints ledger.

- Bank changes happen only through the curator's build capability, after the user has supplied or
  corrected a canonical source.
- Ledger changes happen only through the curator's constraints capability, which ingests the
  `## Constraint proposals` sections at flow close.

A brief that "already applied" its own suggestions has broken the sole-writer rule.

## Status values

- `complete` — the run's findings have been classified and turned into questions.

## Envelope

The common envelope applies. `inputs:` names the run's analytical artifacts — the evidence map, the
validation reports, the fit report, the gap report, the external gate decision when one exists — plus
the bank files and the constraints ledger as they stand.

## Classification — do this before writing any question

Every gap or weak-evidence finding from the run falls into exactly one category:

| Category | Meaning | What to do |
|---|---|---|
| **Genuine gap** | The experience is clearly absent from the candidate's history. | No question. Say what evidence would address it in future, and treat it as a learning target. |
| **Potentially underdocumented** | The experience may exist but is not captured in the canonical sources. | Ask one specific yes/no question, with an action for each answer. |
| **Depth gap** | The experience exists and is documented, but too vaguely to produce strong material. | Name exactly which specifics are missing and ask for them. |

Getting this wrong has a cost: asking about a genuine gap wastes the user's time and creates pressure
to fabricate.

## Sections

### `## Run summary`

The position and company, the overall fit score, and the gap themes that recurred across the run —
evidence map, fit report, validation reports, external reports. A theme that appeared in several
places is flagged as a recurring signal and prioritised.

### `## Genuine gaps`

For each: the gap, a statement that closing it requires real new experience, and what evidence would
address it in a future application. No questions here.

### `## Potentially underdocumented experience`

One entry per item:

```markdown
#### <descriptive label>

**Category:** Potentially underdocumented
**Seen in:** <the run steps where it surfaced>
**Question:** <one specific, answerable question — yes/no first, then detail if yes>
**If yes — what to document:** <exactly what facts to capture, in which source, with what
constraints on how they may be used>
**If no — action:** <the constraint to record, or a note that no change is needed>
```

### `## Depth and specificity gaps`

One entry per item:

```markdown
#### <descriptive label>

**Category:** Depth gap
**Existing entry:** <the current vague statement, quoted or paraphrased, with its location>
**Missing detail:** <precisely what would strengthen it: numbers, scope, ownership level,
technology, outcome>
**Question:** <ask directly for those specifics>
**Where to add:** <which bank file and section it would strengthen>
```

### `## Suggested updates (conditional)`

What would follow from each answer, as conditional actions the user can approve at a glance:

- *If <the user confirms X>* — add to the experience bank under <section>, suggested wording: <draft
  entry>.
- *If <the user provides detail Y>* — update the <project> entry, adding <what>.
- *If <the user confirms Z is absent>* — record the constraint: <suggested wording>.

Suggestions, not actions. Each names the file and section it would affect, so the user can judge it
without reconstructing the context.

### `## Constraint proposals`

Guardrails that follow directly from this run and need no further input — typically an absence the
run confirmed. See `contracts/README.md`. `None.` when there is nothing to propose. Anything that
needs a decision belongs in the question sections above, not here.

## Rules

- **Never suggest inventing** experience or metrics.
- **Never suggest presenting side-project or learning work as professional experience.**
- **Never suggest upgrading a language level, a seniority claim, or an ownership claim** without new
  canonical evidence.
- **Check the constraints ledger first.** A question already settled there is not asked again.
- **Questions are specific and answerable.** "Do you have cloud experience?" is not a question; "When
  working on <system> at <employer>, did you personally write or edit deployment manifests, resource
  limits, or replica counts — and if so, for which services and how often?" is.
- **Do not duplicate the gap report.** That artifact is about this application; this one is about the
  evidence.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | `knowledge-bank-curator.ingest-run-feedback` |
| Consumers | the user; `knowledge-bank-curator` (a later build, once the user has answered) |
