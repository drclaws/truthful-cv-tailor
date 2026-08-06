# Contract: source-audit

Version: 1.0

## Purpose

The source audit is the run's **audit trail of inputs**, written before any drafting happens. It
inventories every source the run will use, classifies what each source is allowed to influence, and
records conflicts between sources explicitly instead of resolving them silently.

It exists because an unsaved summary is not source truth. Later steps — fact-checking above all —
need to know exactly what the run read, in what state, and with what standing.

## Status values

- `complete` — the inventory covers every input the run will use;
- `blocked` — an input could not be read or classified and the run needs a decision.

## Envelope

The common envelope applies. `inputs:` lists the sources being audited; where a source has no path,
it is described instead.

## Sections

### `## Run isolation statement`

An explicit statement of what this run drew on: its own run directory (including the job dossier),
the shared knowledge bank, the shared repository definitions, and the sources listed below —
and that no other run's outputs were read, cited, imitated or used as precedent.

This is stated, not assumed. It is the artifact that makes the isolation invariant checkable.

### `## Source inventory`

One entry per source, each with a short stable identifier that later artifacts can cite. Each entry
carries:

| Field | Meaning |
|---|---|
| identifier | A short label (`S1`, `S2`, …) other artifacts cite. |
| kind | What it physically is: a file, a fetched page, an API response, a pasted text, a conversation transcript, a bank file. |
| locator | Path, URL, or description when neither exists. |
| captured | When it was read or fetched, and the read status — read, partially read, unreadable (with the reason). |
| stored as | Where the run keeps the content, or an explicit note that only metadata and extracted snippets could be retained. |
| evidence class | See below. |
| canonical? | `canonical` or `self-report / secondary`. See below. |

### `## Evidence classes`

Every source is classified. The class decides what the source may influence:

| Class | May influence | May never |
|---|---|---|
| candidate evidence | Candidate facts on the CV. | — |
| job targeting | What the CV emphasizes and which requirements are analysed. | Create a candidate fact. |
| recruiter signal | Emphasis, positioning, wording to mirror. | Create a candidate fact. |
| company context | Positioning, tone, what to foreground. | Create a candidate fact. |
| people / team context | Emphasis only. | Create a candidate fact. |

**Canonical versus self-report.** Canonical candidate inputs are the source of truth for candidate
facts. A candidate statement made in a conversation, a screening call, or a form is a **self-report**:
it is recorded, it may reveal under-documented experience, and it does **not** license a CV claim on
its own. Derived indexes (the knowledge bank) are structured evidence, but never override a more
original canonical input unless the constraints ledger or the user documents the correction.

### `## Bank stanza`

The version statement for the candidate-evidence side: which knowledge-bank files the run uses, when
each was last built, the freshness verdict against the canonical sources, and whether a refresh was
performed before the run proceeded. Bank files also appear as entries in the inventory; this stanza
says what state they were in.

**One file, one writer.** The analyst writes the whole artifact, this stanza included. The freshness
verdict is *produced* by the curator's freshness capability and returned to its caller; the flow
records it, and the analyst transcribes it here, attributed to that check. The curator does not write
into this file — two roles editing one artifact is exactly the ambiguity contracts exist to remove.

If the bank state changes after the audit was written — a refresh triggered mid-run — the audit is
rewritten with `revision:` incremented rather than appended to. The audit always describes the state
the run actually used.

### `## Conflicts`

Every disagreement between sources, stated explicitly: which sources disagree, on what, and how the
run handled it (which source it followed and why, or that it recorded the conflict and left the claim
out). A conflict resolved silently is a defect. An unresolved conflict that affects a claim makes
that claim ineligible for the document until it is settled.

### `## Gaps in the inventory`

Sources that were expected but absent or unreadable, and what the run does about them: what will be
missing from the analysis, what was asked of the user. Recorded so that a thin result is legible as
"the inputs were thin" rather than "the analysis was weak".

### `## Constraint proposals`

Guardrails discovered while auditing sources — a conflict that should constrain future claims, a
source whose standing must not be over-read, a mapping that must not be treated as equivalence. See
`artifact-conventions.md`. `None.` when there is nothing to propose.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | `vacancy-analyst.audit-sources` — sole writer; the bank stanza is filled from the freshness verdict returned by `knowledge-bank-curator.check-freshness` |
| Consumers | `reviewer` (fact-check traceability), `experience-writer`, `vacancy-analyst`, `knowledge-bank-curator` |
