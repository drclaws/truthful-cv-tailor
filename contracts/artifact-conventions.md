# Artifact conventions

The rules **every** contract in this directory inherits: what a contract may and may not describe,
how an artifact instance is named, the common envelope every instance opens with, and the
artifact-wide rules on truthfulness, run isolation, constraint proposals and versioning — followed
by the rules that bind a **named family** of contracts rather than all of them.

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
  capability (`<role>.<capability>`) or to a tool.
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

## Deliverable-document contracts

**Deliverable-document contracts** — those describing an artifact a person sends or publishes:
`cv-document`, and `profile-document` when it exists. Each declares its own sections, its own
target, its own header shapes and its own surface-specific rules; what every such document shares is
stated here once and inherited — **presentation neutrality** and the **content-first fit policy**.

**Why a named family rather than a rule for every contract.** These rules were first written for the
CV and read like CV rules, but not one of them is about a CV: they are about a document that a
machine reads as a flat stream of text and a stranger skims in seconds. They hold unchanged for a
professional-network profile, which has no renderer at all. Applied to *every* contract they would
be wrong — an `evidence-map` **is** a table — so the subset is named, exactly as the report-type
family above is named. The wording below therefore names no particular surface: **the target the
caller declares**, not the page target; **a downstream surface**, not the renderer.

### Presentation neutrality

The document stays plain, linear and machine-readable, because it is read twice: once by a machine
that sees only the text stream in reading order, and once by a person scanning for a few seconds.
Anything carrying meaning outside that text stream is lost to the first reader and easily missed by
the second.

- **No tables in the document's content.** Extraction interleaves and reorders cells, so a fact that
  only the table's geometry explains reaches the reader scrambled, or not at all.
- **No images, graphics, skill bars or rating marks.** They carry no extractable text, and a bar or
  a star count asserts a level of proficiency that no source states.
- **No fact carried only by an icon, a colour, an alignment or a position.** Every fact has to
  survive being read as plain text in reading order. An icon that is the only thing saying "this is
  a phone number", or a date recognisable only by where it sits, is a fact the reader never receives.
- **No critical information placed only in a running header or footer.** Repeating furniture is
  routinely dropped, duplicated or hoisted out of order by extraction, and human readers skip it.
- **Simple bullets, and the declared section names used exactly as declared** — no invented, clever
  or renamed headings. Headings are the reader's index and the parser's segmentation, and a renamed
  one defeats both. Which sections exist, and in what order, stays each contract's own business.
- **An optional section with no supported content is omitted entirely**, never kept as an empty
  heading. An empty heading reads as something the candidate lacks, rather than as a section that
  did not apply.
- **Escaping belongs to the downstream surface.** Characters that a renderer, a markup dialect or a
  web form has to escape are written naturally here. Escaping is the consuming surface's job, never
  a reason to distort, drop or reword the document's text.

Presentation choices made downstream — columns, decorative icons, typography — belong to the surface
and are governed by the surface's own rules. They are permitted only while the delivered result's
text still extracts readably, and are never introduced into the document itself.

### The content-first fit policy

Every deliverable has a limit: a page count, a field length, a screen of text. **The target is
declared by the caller** — the flow, the render operation, or the platform whose form the text is
pasted into — and never by the document contract, which fixes no page or word count of its own. What
is fixed here is what happens when the content exceeds that target.

1. **The evidence-carrying section is compressed first.** Merge overlapping items, shorten wording
   while preserving concrete scope, impact, tooling and seniority, then drop the lowest-value
   detail, keeping the strongest supported evidence for this target. Each contract names which of
   its own sections that is.
2. **Compress gradually.** The goal is a complete, readable document that fits — not the shortest
   possible document. Nothing is cut harder than the target requires.
3. **Freed space is refilled.** The rule runs both ways: when a later edit opens room, it goes to
   the highest-value supported material that improves fit against the same target.
4. **A presentational change is never the answer.** Restyling the delivered result — geometry,
   margins, type sizes, spacing, colours, column widths, section styling — to make content fit is
   out of bounds, and a deliverable document never proposes one. Reaching instead for a different
   template or a different surface to squeeze the same content in is the same violation by another
   route. **A fit problem is a content problem**, and it is solved by revising validated content
   under the checks that validated it.

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
