# Contracts

A **contract** defines the FORMAT and SEMANTICS of one artifact: what it contains, what each part
means, who may produce it, and who consumes it. Contracts are the only interface between roles —
data flows through file artifacts, never through direct role-to-role calls.

A contract never defines PLACEMENT. Where an artifact is written is decided by the flow (workflow
skill) that runs the step, or by the user when a role is invoked directly; the path is always passed
to the role as an explicit parameter.

## Scope rules

- **Contracts describe artifacts, not procedures.** How an artifact is produced belongs to a role
  capability (`roles/<role>/capabilities/<name>.md`) or to a tool skill (`skills/tools/<name>/SKILL.md`).
- **Contracts are tool-agnostic and path-agnostic.** No concrete tool names, no external absolute
  paths, no OS specifics. Examples use placeholders such as `<run>/`, `<source-path>`, `<Name>`.
- **Contracts carry no user context.** What the engine needs from the user is described by the
  `user-context` contract; where the user keeps it is never prescribed.

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
| `contract` | The contract name exactly as filed under `contracts/`. |
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
the ledger by `curator.maintain-constraints`, invoked by the flow as its closing step.

Within a single run, steps must honour constraint proposals raised by earlier steps of that same
run, before ingestion has happened.

A report with nothing to propose still carries the section, with the single line `None.`

## Contract versioning

Each contract file declares `Version: <major>.<minor>` under its title.

- **minor** — additive, backward compatible: a new optional section or field.
- **major** — a change that invalidates existing instances: a removed/renamed section, changed
  semantics, a narrowed status vocabulary.

Artifacts record the version they were written against; a consumer that meets an older major
version reports it as a finding rather than silently reinterpreting the artifact.

## Contract index

Persistent contracts — artifacts that outlive a single run:

| Contract | File | Producer | Main consumers |
|---|---|---|---|
| `user-context` | `user-context.md` | the user (via `setup-master`) | every flow at preflight |
| `knowledge-bank` | `knowledge-bank.md` | `knowledge-bank-curator.build-banks` | curator, writer, analyst, reviewer |
| `constraints-ledger` | `constraints-ledger.md` | `knowledge-bank-curator.maintain-constraints` | writer, reviewer, curator |
| `transcript` | `transcript.md` | transcriber (external, not yet built) | analyst (via the job dossier) |
| `job-dossier` | `job-dossier.md` | the user / flow scaffolding | analyst, reviewer |

Per-run contracts:

| Contract | File | Producer | Main consumers |
|---|---|---|---|
| `run-manifest` | `run-manifest.md` | flow executor | every role in the run, the user |
| `source-audit` | `source-audit.md` | `vacancy-analyst.audit-sources` (+ curator bank stanza) | reviewer, writer |
| `requirements-profile` | `requirements-profile.md` | `vacancy-analyst.analyze-job` | curator, writer, analyst, reviewer |
| `recruiter-signals` | `recruiter-signals.md` | `vacancy-analyst.extract-recruiter-signals` | writer, analyst, reviewer |
| `evidence-map` | `evidence-map.md` | `knowledge-bank-curator.query-bank` | writer, analyst, reviewer |
| `cv-document` | `cv-document.md` | `experience-writer.write-document` / `.edit-document` | reviewer, renderer, analyst |
| `validation-report` | `validation-report.md` | `reviewer.fact-check` / `.run-check` / `.normalize-external-report` | writer, renderer, analyst, curator |
| `external-gate-decision` | `external-gate-decision.md` | `reviewer.gate-external-recommendations` | writer, analyst, the user |
| `fit-report` | `fit-report.md` | `vacancy-analyst.score-fit` | the user, analyst, curator |
| `gap-report` | `gap-report.md` | `vacancy-analyst.gap-analysis` | the user, curator |
| `render-manifest` | `render-manifest.md` | `renderer.render-document` | reviewer, the user |
| `bank-update-brief` | `bank-update-brief.md` | `knowledge-bank-curator.ingest-run-feedback` | the user |

Report-type contracts — those that carry `## Constraint proposals`: `source-audit`,
`requirements-profile`, `recruiter-signals`, `evidence-map`, `validation-report`,
`external-gate-decision`, `fit-report`, `gap-report`, `render-manifest`, `bank-update-brief`.
