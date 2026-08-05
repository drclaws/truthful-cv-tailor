# Contract: constraints-ledger

Version: 1.0

## Purpose

The ledger records **negative evidence**: the guardrails that keep later runs from re-making a
mistake someone already caught. Its entries have the shape "do not claim X unless a canonical source
adds it" — a claim the evidence does not support, a wording risk, a recurring external-validator
trap, a conflict between sources, or a mapping that must not be over-read.

Positive evidence lives in the knowledge bank. The ledger says what the evidence does **not** carry.

## Sole writer

The ledger is written **only** by `knowledge-bank-curator.maintain-constraints`. No other role edits
it, ever. Other roles propose entries through the `## Constraint proposals` section that every
report-type contract carries; the flow invokes the curator's ingest capability as its closing step.

Ingestion policy (semantics the ledger records, not the procedure that applies it):

- a proposal that only records a conservative safety rule or a factual limitation is ingested as
  written;
- anything broader — a proposal that would suppress supported evidence, contradict an existing
  entry, or decide something the sources leave open — becomes a question to the user and is recorded
  as `pending` until answered.

Within a single run, steps honour proposals raised by earlier steps of that run **before** the
proposals reach the ledger.

## Status values

- `current` — the live ledger (contract-defined value).

Each ingestion increments `revision:`.

## Envelope

The common envelope applies, with `run_id: n/a` and
`producer: knowledge-bank-curator.maintain-constraints`. `inputs:` lists the reports whose proposals
were ingested in the latest revision.

## Sections

### `## Hard constraints`

The active guardrails. One entry per constraint. Each entry carries:

| Field | Meaning |
|---|---|
| statement | The guardrail itself, phrased as a prohibition with its unlock condition — "do not claim X unless a canonical source adds it". |
| scope | What it applies to: a technology, a domain, an ownership level, a seniority claim, a wording pattern, a source conflict. |
| origin | Where it came from: the run and the report that proposed it, or the user. |
| recorded | The date it entered the ledger. |
| state | `active` · `partially unlocked` · `superseded`. |

A constraint is never silently deleted. When new canonical evidence arrives, the entry moves to
`partially unlocked` or `superseded`, keeps its history, and states **exactly** what the new source
does and does not license. Deleting the entry loses the reason the guardrail existed.

### `## Pending questions`

Proposals that could not be ingested as conservative safety rules and are waiting on the user. Each
carries the proposed statement, its origin, and the specific question the user must answer. A pending
item is not a constraint: it does not restrict anything until it is answered and moved into
`## Hard constraints`.

### `## Superseded`

Constraints no longer in force, with the evidence that released them. Kept so that a later reader can
see the question was settled rather than forgotten. May also be kept inline via the `state` field
when the file is small; a repository of either shape satisfies this contract as long as the history
is not lost.

## Rules

- **Conservative by default.** An ambiguous proposal becomes the stricter constraint, or a pending
  question — never a permissive reading.
- **Specific, not sweeping.** "Do not claim professional experience with <technology>" is usable.
  "Be careful with technology claims" is not.
- **Every constraint names its unlock condition**, so a future refresh can tell when it no longer
  applies.
- **Consumers must honour the ledger.** A claim that a constraint forbids does not enter a document,
  an evidence map, or a fit score, regardless of how attractive it is for the target.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | `knowledge-bank-curator.maintain-constraints` |
| Consumers | `experience-writer`, `reviewer`, `vacancy-analyst`, `knowledge-bank-curator` |
