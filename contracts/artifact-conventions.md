# Artifact conventions

The rules **every** contract in this directory inherits: what a contract may and may not describe,
how an artifact instance is named, the common envelope every instance opens with, and the
artifact-wide rules on truthfulness, run isolation, constraint proposals and versioning.

This is an ordinary document of the contracts directory, listed in the index like any contract. Refer
to it by the name `artifact-conventions` from outside the directory, and as the bare sibling filename
`artifact-conventions.md` from a contract file.

**Why this document exists.** Until it did, every contract file pointed at this directory's
`README.md` for the common envelope — an agent rule deferring to a human document for a rule it has
to follow. A README is orientation for a person and is never something an agent follows to do its
work, so the envelope, the field rules and the artifact-wide rules moved here, and the contract files
now point at this sibling instead. The rules themselves did not change in that move; only their home
did.

## Scope rules

- **Contracts describe artifacts, not procedures.** How an artifact is produced belongs to a role
  capability (`<role>.<capability>`) or to a tool skill.
- **Contracts are tool-agnostic and path-agnostic.** No concrete tool names, no external absolute
  paths, no OS specifics. Examples use placeholders such as `<run>/`, `<source-path>`, `<Name>`.
- **Contracts carry no user context.** What the engine needs from the user is described by the
  `user-context` contract; where the user keeps it is never prescribed.
- **A contract never defines placement.** Where an artifact is written is decided by the flow
  (workflow skill) that runs the step, or by the user when a role is invoked directly; the path is
  always passed to the role as an explicit parameter.

## Artifact naming

- Artifact filenames are derived from the contract name: contract `requirements-profile` →
  `requirements_profile.md`. **No numeric prefixes.** Ordering, gate status and the artifact index
  live in the run manifest (`run.md`, contract `run-manifest`).
- When a flow produces several instances of one contract, the flow names them and records the
  mapping in `run.md` — for example two `cv-document` instances as `draft_cv.md` and `final_cv.md`,
  or one `validation-report` per registered validator under a declared path pattern.

## The common envelope

Every artifact instance opens with a YAML frontmatter block. It is the machine-readable header that
makes an artifact self-describing: which contract it obeys, who produced it, from what, and in what
state.

```markdown
---
contract: <contract-name>
contract_version: <major>.<minor>
producer: <role>.<capability> | flow:<flow-name> | tool:<tool-name>
run_id: <run identifier> | n/a
status: <one of the values this contract declares>
revision: <integer, starts at 1>
created: <ISO-8601 date or date+time>
updated: <ISO-8601 date or date+time>
inputs:
  - <path> — <contract-name>
  - <path> — <contract-name>
---
```

Field rules:

| Field | Rule |
|---|---|
| `contract` | The contract name exactly as the contracts index files it. |
| `contract_version` | The version of the contract the instance was written against, copied from the contract file's `Version:` line. |
| `producer` | The role capability that wrote the artifact, or the flow/tool when the artifact is written by orchestration itself (e.g. `run.md`). |
| `run_id` | The run this artifact belongs to. Persistent artifacts (knowledge bank, constraints ledger) use `n/a`. |
| `status` | Present always; the allowed set is declared by each contract (baseline vocabulary below). |
| `revision` | Starts at `1`. Incremented whenever the artifact is overwritten in place — re-validation after edits, re-render, re-check. Never reset. |
| `created` / `updated` | ISO-8601 (`YYYY-MM-DD` or `YYYY-MM-DDThh:mm±hh:mm`). Taken from the environment, never guessed. On `revision: 1` both are equal. |
| `inputs` | Every artifact actually consumed, as `path — contract-name`. Sources outside the contract set are listed with a short description instead of a contract name. Use `inputs: []` only when the artifact genuinely consumed nothing. |

Baseline `status` vocabulary (each contract declares which subset it uses, and may add values it
defines): `draft`, `final`, `pass`, `pass-after-edits`, `fail`, `informational`, `in-progress`,
`complete`, `blocked`, `skipped`.

## Truthfulness in artifacts

These apply to every contract instance without exception:

- **Never invent.** Experience, metrics, tools, employers, dates, titles, degrees, certifications
  and achievements are only ever reported as found in a canonical source, with a citation.
- **Unknown is a value.** When something cannot be determined, write `unknown` (or `not stated in
  sources`) and say why. A plausible guess presented as fact is a defect, not a convenience.
- **Weak evidence is labelled weak.** Strength markers are never rounded up.
- **Gaps are recorded, never smoothed over.** An unsupported requirement becomes a gap entry.
- **Inference is marked.** Anything derived rather than read is tagged `(inferred from <source>)`.

## Run isolation in artifacts

An artifact may cite: its own run directory, the shared knowledge bank, and the shared repository
definitions (contracts, roles, skills). It must never read, imitate or cite another run's outputs as
evidence, style authority or precedent. A pattern worth keeping is first promoted into an
authoritative file (a contract, a role capability, a skill) and only then used.

## Constraint proposals

The knowledge bank and the constraints ledger have a single writer: the knowledge-bank-curator.
Other roles never write them. Instead, **every report-type contract carries a `## Constraint
proposals` section**, in which the producing role proposes negative-evidence guardrails discovered
during its work ("do not claim X unless a canonical source adds it"). Proposals are ingested into
the ledger by `knowledge-bank-curator.maintain-constraints`, invoked by the flow as its closing step.

Within a single run, steps must honour constraint proposals raised by earlier steps of that same
run, before ingestion has happened.

A report with nothing to propose still carries the section, with the single line `None.`

**Report-type contracts** — those that carry `## Constraint proposals`: `source-audit`,
`requirements-profile`, `recruiter-signals`, `evidence-map`, `validation-report`,
`external-gate-decision`, `fit-report`, `gap-report`, `render-manifest`, `bank-update-brief`, and
`cv-document` — the last one inside its writer annex. The document is a deliverable rather than a
report, but it is the writing role's only artifact, and the sole-writer rule gives every role exactly
one route to the constraints ledger.

## Contract versioning

Each contract file declares `Version: <major>.<minor>` under its title.

- **minor** — additive, backward compatible: a new optional section or field.
- **major** — a change that invalidates existing instances: a removed/renamed section, changed
  semantics, a narrowed status vocabulary.

Artifacts record the version they were written against; a consumer that meets an older major
version reports it as a finding rather than silently reinterpreting the artifact.

## Who writes what

Which role capability produces each contract, and who reads it. This is a rule about authority, not a
resolver — the contracts index is where a name is turned into a file.

Persistent contracts — artifacts that outlive a single run:

| Contract | Producer | Main consumers |
|---|---|---|
| `user-context` | the user (via `setup-master`) | every flow at preflight |
| `knowledge-bank` | `knowledge-bank-curator.build-banks` | curator, writer, analyst, reviewer |
| `constraints-ledger` | `knowledge-bank-curator.maintain-constraints` | writer, reviewer, curator |
| `transcript` | transcriber (external, not yet built) | analyst (via the job dossier) |
| `job-dossier` | the user / flow scaffolding | analyst, reviewer |

Per-run contracts:

| Contract | Producer | Main consumers |
|---|---|---|
| `run-manifest` | flow executor | every role in the run, the user |
| `source-audit` | `vacancy-analyst.audit-sources` (bank stanza filled from the curator's freshness verdict) | reviewer, writer |
| `requirements-profile` | `vacancy-analyst.analyze-job` | curator, writer, analyst, reviewer |
| `recruiter-signals` | `vacancy-analyst.extract-recruiter-signals` | writer, analyst, reviewer |
| `evidence-map` | `knowledge-bank-curator.query-bank` | writer, analyst, reviewer |
| `cv-document` | `experience-writer.write-document` / `.edit-document` | reviewer, renderer, analyst |
| `validation-report` | `reviewer.fact-check` / `.run-check` / `.normalize-external-report` | writer, renderer, analyst, curator |
| `external-gate-decision` | `reviewer.gate-external-recommendations` | writer, analyst, the user |
| `fit-report` | `vacancy-analyst.score-fit` | the user, analyst, curator |
| `gap-report` | `vacancy-analyst.gap-analysis` | the user, curator |
| `render-manifest` | `renderer.render-document` | reviewer, the user |
| `bank-update-brief` | `knowledge-bank-curator.ingest-run-feedback` | the user |
