# Contract: run-manifest

Version: 1.0

## Purpose

The run manifest is the **single place that says what happened in a run**: which flow ran, on what
inputs, with what user context, which steps ran and how they ended, which gates are green, and where
every artifact is. Because artifact filenames carry no numeric prefixes, ordering and state live here
and nowhere else.

Anyone — a later step, a resuming agent, the user, a reviewer of the run — should be able to read
this file alone and know the state of the run.

Conventional filename: `run.md`.

## Status values

- `in-progress` — the flow is running;
- `complete` — every step reached a terminal state and the flow's definition of done is met;
- `blocked` — the flow stopped and needs a decision from the user;
- `fail` — the flow ended without meeting its definition of done.

The manifest's status is the run's status. A `complete` manifest with a red gate is a defect.

## Envelope

The common envelope applies, with `producer: flow:<flow-name>` (or `tool:<tool-name>` for a
standalone tool run) and `run_id` set to this run's identifier. The manifest is updated in place
throughout the run; `revision:` increments on each write, `updated:` tracks the latest write.

## Sections

### `## Run`

Run identifier, the flow name and **flow version**, start time, and end time when finished. The flow
version matters: a run executed under an older version of a flow is read differently from one
executed under the current version.

### `## Inputs`

What the run was given: the job dossier (or the equivalent input set for a non-CV flow), the
knowledge bank location, and any input supplied directly by the user for this run. References, not
copies.

### `## User context`

Two things, both required:

1. **Resolution used** — which mechanism supplied the user context: the harness-native local rules
   file, other harness-provided context or memory, or values the user was asked for during preflight.
   When several contributed, each is named with what it supplied.
2. **Resolved snapshot** — the values the run actually used: the resolved package root and the
   resolved output root, the canonical experience sources, the active validation set with each
   entry's kind, the per-skill settings in force, and any additional rules the flow was told to
   honour. Recorded because free-form context can change between runs; the snapshot is what makes a
   run reproducible and reviewable. The two roots belong here for the same reason and one more:
   neither is derivable from the run afterwards, so without them a reader cannot tell which copy of
   the definitions the run obeyed, nor that its results went where the user meant them to.

Values the flow validated and questions it had to ask the user are recorded here too, with the
answers received.

### `## Bank freshness`

The freshness verdict at preflight: per canonical source, whether it changed since the bank was last
built (or could not be read), and the resulting verdict — fresh, stale, or unreadable-in-part — plus
what the flow did about it (proceeded, refreshed first, asked the user).

### `## Steps`

The step checklist. One row per step, in execution order:

| Column | Meaning |
|---|---|
| step | The step's name in the flow. |
| executor | `role.capability`, `tool:<name>`, or `flow` for orchestration steps. |
| contract | The contract of the artifact the step produces, or `—`. |
| artifact | The path written, relative to the run directory. |
| group | The parallel group the step belongs to, when the flow declares one. |
| status | `pending` · `in-progress` · `complete` · `skipped` · `fail` · `blocked`. |
| revision | The revision of the produced artifact, so re-runs after edits are visible. |
| notes | Why a step was skipped, what failed, what was re-run. |

A **skipped** step always carries the reason and, when it was skipped because a capability was not
bound, the instructions for doing it manually. Skipped is a recorded outcome, not a failure.

### `## Gates`

One row per gate the flow declares: gate name, what it requires, current state (`green` · `red` ·
`not reached` · `waived by the user, with the reason`), and the artifact that evidences it. Gates are
listed even before they are reached, so a reader can see what still has to happen.

### `## Artifact index`

Every artifact the run produced: path, contract, status, revision. This is the mapping from contract
names to the filenames this particular flow chose — including instances the flow named itself (two
`cv-document` instances, one `validation-report` per registered validator). Intermediate build
directories and raw captures are listed too, marked as byproducts.

### `## Open questions`

Anything awaiting the user: escalations raised by a step, unresolved manual-review items, ambiguous
context. Empty when the run is complete — an unresolved question and a `complete` status cannot
coexist.

## Rules

- **Written as the run proceeds**, not reconstructed at the end. A manifest that only exists after
  the fact cannot support resuming or blocking.
- **No result lives only in the manifest.** The manifest points at artifacts; it does not replace
  them.
- **No procedure here.** The manifest records what a flow did. What a flow *should* do lives in the
  flow's own definition.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | the flow executor (orchestration), not a role capability |
| Consumers | every role participating in the run — `knowledge-bank-curator`, `vacancy-analyst`, `experience-writer`, `reviewer`, `renderer` — and the user |

Roles **read** the manifest (to find inputs, to check gate state before a gated step). They do not
write it; the flow records their outcomes.
