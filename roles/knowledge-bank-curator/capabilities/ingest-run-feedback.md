# Capability: knowledge-bank-curator.ingest-run-feedback

## Purpose

Close the loop between one run and the candidate's knowledge bank: read everything the run learned —
gaps, weak evidence, validator findings, fit analysis — and turn it into a short list of concrete,
answerable questions that tell the candidate what real experience is missing from their canonical
sources. The output is the `bank-update-brief`.

This capability is a **report only**. It never writes the bank and never writes the constraints
ledger; the ledger has its own writer, invoked separately at flow close.

## Inputs

| Input | Contract / description | Required |
|---|---|---|
| `run_reports` | The run's analytical artifacts, each with its contract: `evidence-map`, `fit-report`, `gap-report`, `validation-report` instances (internal and normalised external), `external-gate-decision`, `requirements-profile`, `recruiter-signals`. Whatever the flow produced. | required |
| `bank_dir` | The knowledge bank, read-only: what is already documented, and how. | required |
| `constraints_ledger` | The constraints ledger, read-only: what has already been confirmed absent. | required |
| `output_path` | Where the brief is written. | required |
| `run_id` | Run identifier for the envelope. | required |

## Outputs

| Output | Contract | Status values |
|---|---|---|
| The brief at `output_path` | `bank-update-brief` | `complete` |

It is a report-type artifact: common envelope plus a `## Constraint proposals` section (`None.` when
there is nothing to propose).

## Procedure

1. **Read the run's reports and the bank.** Collect every gap, weak-evidence finding, unsupported
   keyword, and recurring criticism, together with which report each came from.
2. **Read the ledger.** Anything already recorded there as confirmed absent is a **closed question**:
   it is not asked again. Re-asking closed questions is how a review turns into pressure to
   fabricate.
3. **Classify every finding** into exactly one of the three categories below, *before* writing any
   question. The classification decides whether a question is even appropriate.
4. **Mark recurring signals.** A finding that appeared in several reports — evidence map, fit report,
   validators — is flagged as recurring and sorted to the top of its category.
5. **Write the brief** with the sections below.
6. **Propose constraints** for anything this run demonstrated to be a durable factual limitation, in
   the `## Constraint proposals` section, for the separate ledger-ingestion step to pick up.

## Rules

### The three categories

| Category | Means | What to write |
|---|---|---|
| **Genuine gap** | The experience is clearly absent from the candidate's history. | No question. State the gap, confirm it needs real new experience, and describe what evidence would close it in a future application. Treat as a learning target, not a documentation task. |
| **Potentially underdocumented** | The experience may well exist, but the canonical sources do not capture it. | A specific yes/no question, plus what to do on each answer. |
| **Depth gap** | The experience exists and is documented, but too vaguely to yield strong evidence. | Name the existing entry, say exactly which specifics are missing, ask for them. |

**Separating genuine gaps from underdocumented ones is the point of the exercise.** Asking about a
genuine gap wastes the candidate's time and invites invention; treating an underdocumented strength
as a gap silently discards real experience.

### Section layout of the brief

1. **Run summary** — the position and company, the fit outcome, and the gap themes that recurred
   across the run's reports.
2. **Genuine gaps** — one entry each: the gap, why it needs real experience, what evidence would
   close it later. No questions in this section.
3. **Potentially underdocumented experience** — one entry per item:

   ```markdown
   #### <descriptive label>

   **Category:** Potentially underdocumented
   **Seen in:** <which reports raised it; mark "recurring" when more than one>
   **Question:** <one specific yes/no question, then the detail to give if yes>
   **If yes — what to document:** <which bank section, which facts to capture,
   which constraints apply, in what wording>
   **If no — action:** <propose the constraint that records the absence, so the
   question is never asked again — the proposal goes in `## Constraint proposals`;
   or state that no bank change is needed>
   ```

4. **Depth and specificity gaps** — one entry per item:

   ```markdown
   #### <descriptive label>

   **Category:** Depth gap
   **Existing entry:** <quote or paraphrase the current vague statement, with its bank citation>
   **Missing detail:** <exactly what would strengthen it: numbers, scope, ownership level,
   technology, outcome>
   **Question:** <ask directly for those specifics>
   **Where to add:** <which bank file and section>
   ```

5. **Suggested bank updates** — the concrete changes that would follow from the answers, as
   conditionals: *if the candidate confirms X → add to the experience bank under <section>, suggested
   wording: …*; *if detail Y arrives → extend the <project> entry with …*; *if Z is confirmed absent
   → propose the constraint "…"*. These are suggestions for a future build, not instructions to
   anybody to edit the bank now.
6. **`## Constraint proposals`** — per the common report rule.

### Question quality

- **Specific and answerable.** "Do you have cloud experience?" is useless. "When working with the
  internal deployment platform, did you personally write or edit deployment manifests, resource
  limits, or replica counts? If yes: for which services, and how often?" is actionable.
- Ask for a yes/no first, then for the detail that a *yes* would need.
- One question per item. A question with three parts gets one answer that fits none of them.
- Never suggest inventing experience or metrics, and never hint at wording that would sound better
  than the truth.
- Never suggest presenting side-project or self-education work as professional experience.
- Never suggest upgrading a language level, an ownership claim, or a seniority signal without new
  canonical evidence.

### Boundaries

- **This is forward-looking, about the bank.** The run's own gap report is application-specific —
  this CV, this interview. Do not duplicate it: where they overlap, the brief asks what would change
  the *bank*, not what to say in *this* application.
- **Nothing is written except the brief.** Not the bank, not the ledger, not the run's other
  artifacts. Every suggested change is conditional on an answer the candidate has not given yet.
- **The bank is the reference for what is already documented** — check before asking, so that a
  question never asks for something the bank already contains.

## Failure and skip conditions

- **Some run reports are absent** (a validator was skipped, no external checks ran) — proceed with
  what exists and list the missing inputs in the run summary. A partial brief is useful; a blocked
  one is not.
- **The run produced no gaps at all** — still write the brief, with the summary, empty categories
  stated explicitly as empty, and `None.` under constraint proposals. Silence is indistinguishable
  from an unrun step.
- **The ledger cannot be read** — stop and report. Without it, closed questions get re-asked, which
  is the one failure mode this capability must not have.
- **The bank cannot be read** — stop and report: without knowing what is documented, every question
  is a guess.
