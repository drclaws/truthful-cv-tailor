# Contract: evidence-map

Version: 1.0

## Purpose

The evidence map answers one question per requirement: **what does the candidate's evidence actually
say about this, and how strongly?** It is the bridge between the target (the requirements profile)
and the evidence (the knowledge bank), and it is the artifact that makes truthfulness checkable
later — a claim in a document should be traceable through this map to a cited bank entry.

It is a **retrieval** artifact. It reports what exists and how strong it is. It does not decide what
the document says.

## Status values

- `complete` — every requirement in the profile has an entry;
- `blocked` — the bank could not be read or is too stale to query.

## Envelope

The common envelope applies. `inputs:` names the requirements profile, the recruiter signals, the
bank files queried, and the constraints ledger.

## Coverage rule

**Every** requirement and responsibility identifier from the requirements profile appears here,
including the ones with no evidence. A requirement absent from the map is indistinguishable from a
requirement that was never checked; a `None` entry is a result.

Entries cite the profile's identifiers (`R1`, `R2`, …) so the fit report and the gap report can join
on them.

## Entry structure

One entry per requirement:

### `### <identifier> — <requirement as stated>`

The requirement quoted from the profile, with its explicit/inferred marking carried over.

**Evidence found** — zero or more items, each with:

| Field | Rule |
|---|---|
| citation | The bank file and section (or the canonical source, where the run reads one directly) the evidence comes from. A bare assertion with no citation is not evidence. |
| supporting fact | What the source actually says, close to its own wording. Not a strengthened paraphrase. |
| strength | `Strong` · `Medium` · `Weak` · `None`. |

**Strength** is assigned against the evidence, never against the requirement's importance or the
desire to score well:

- `Strong` — production experience, directly stated, with scope or outcome.
- `Medium` — real experience, but narrower, older, or less directly stated than the requirement asks.
- `Weak` — adjacent, incidental, inferred, or non-professional exposure.
- `None` — nothing in the evidence addresses it.

Strength is never rounded up, and never upgraded because several weak items point the same way —
several weak items are several weak items, and that is stated.

**Constraint flags** — the constraints-ledger entries that bear on this requirement, quoted. A
constraint flag is binding downstream: it names what must not be claimed here even where evidence
looks suggestive.

**Safer wording** — when the honest evidence is narrower than the requirement, a formulation that
states what is genuinely supported. This is a truthfulness aid, not a placement instruction.

**GAP** — present when strength is `None`, or when constraints forbid using what evidence exists.
A GAP marker states what kind of experience is missing (a technology, a domain, an ownership level,
a seniority level), so the gap report can classify it without re-deriving it.

## Optional summary section

### `## Coverage summary` (optional)

Counts by strength across must-have and nice-to-have requirements, and the list of GAP identifiers.
Convenience only — the entries remain the source of truth.

## `## Constraint proposals`

Guardrails discovered while mapping: evidence that consistently invites over-claiming, a term whose
apparent match is misleading, a mapping that must not be read as equivalence. See
`artifact-conventions.md`. `None.` when there is nothing to propose.

## Deliberate non-features

- **No suggested placement.** This contract carries no "include in summary / skills / experience"
  column. Placement is the writer's decision under the `cv-document` contract, and tag verification
  is the analyst's under the `fit-report` contract. Should a document turn out to under-use available
  evidence in practice, the intended remedy is to add an **optional, neutral** placement column here
  — not to move the mapping step back to the writing side.
- **No scoring.** Strength labels are evidence descriptions, not points. Weighted scoring is the fit
  report's job.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | `knowledge-bank-curator.query-bank` (batch mode over the requirements profile) |
| Consumers | `experience-writer`, `vacancy-analyst` (fit scoring, gap analysis), `reviewer` (fact-check) |
