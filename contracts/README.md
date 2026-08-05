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
| `source-audit` | `source-audit.md` | `vacancy-analyst.audit-sources` (bank stanza filled from the curator's freshness verdict) | reviewer, writer |
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
`external-gate-decision`, `fit-report`, `gap-report`, `render-manifest`, `bank-update-brief`, and
`cv-document` — the last one inside its writer annex. The document is a deliverable rather than a
report, but it is the writing role's only artifact, and the sole-writer rule gives every role exactly
one route to the constraints ledger.

## Predecessor coverage matrix

The engine this repository replaces was one policy file (`AGENTS.md`) plus sixteen prompt files
(`prompts/`). Every normative rule in those files has a **designated home** in the new structure. This
matrix is that designation: rule or section → the file that owns it → who lands it.

Three things it is not: it is not a summary of the rules (the homes hold those), it is not a record of
work done (a designated home may not exist yet), and it is not authority (the designated file is
authoritative once written; this table only says where to look).

**Status column:** `T2` — landed by this task, in `contracts/`. `→ T3x` / `→ T5x` / `→ T6` / `→ T8` —
designated, landed by the task that owns that file. Actual landing is verified by those tasks and by
the final sweep.

A rule may legitimately appear in two homes when both a contract and a role need it — the contract is
then the normative home and the role's copy is operational guidance. A rule may never have **no** home.

### `AGENTS.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| Agent purpose; truthful, ATS-friendly, job-specific CVs from structured inputs | new `AGENTS.md` purpose paragraph | → T8 |
| Source priority: canonical candidate inputs are the source of truth for candidate facts | `contracts/knowledge-bank.md` (source of truth), `contracts/source-audit.md` (evidence classes, canonical vs self-report) | T2 |
| Job inputs define targeting; recruiter and people/team inputs define emphasis only and cannot create candidate claims | `contracts/job-dossier.md`, `contracts/recruiter-signals.md` (the hard rule), `contracts/source-audit.md` (evidence classes) | T2 |
| Derived indexes must not override more original canonical inputs unless a constraint or the user documents a correction | `contracts/knowledge-bank.md` (shared rules), `contracts/source-audit.md` | T2 |
| Index content rules live in one place; `master_cv.md` is not kept | `contracts/knowledge-bank.md` (file set) | T2 |
| Refresh an index when a canonical source changed or new inputs appeared; check all three together; detect staleness before evidence mapping | `roles/knowledge-bank-curator/capabilities/check-freshness.md`; `skills/workflows/refresh-knowledge-bank/SKILL.md`; recorded per run in `run-manifest` → `## Bank freshness` | → T3a / → T4 (record: T2) |
| Constraints may be updated without asking when the update is a conservative safety rule or factual limitation | `contracts/constraints-ledger.md` (ingestion policy), `roles/knowledge-bank-curator/capabilities/maintain-constraints.md` | T2 / → T3a |
| Run isolation: no cross-run contamination; a pattern is promoted into an authoritative file before use | `contracts/README.md` → "Run isolation in artifacts"; `contracts/source-audit.md` → `## Run isolation statement`; new `AGENTS.md` invariants | T1 / T2 / → T8 |
| Audit trail: save a source inventory; identify each input and its role; no unsaved summaries; store metadata and snippets when content cannot be stored; mark conflicts explicitly | `contracts/source-audit.md` | T2 |
| Required outputs list for each job folder | `skills/workflows/generate-targeted-cv/SKILL.md` (fixed artifacts and path patterns); `contracts/run-manifest.md` → `## Artifact index` | → T6 (index: T2) |
| Export filename pattern `FirstNameSurname.<ext>` | `skills/workflows/generate-targeted-cv/SKILL.md` (the naming rule); identity from `contracts/knowledge-bank.md` → `## Candidate`; naming check in `contracts/render-manifest.md` → `## Exports` | → T6 (identity + check: T2) |
| Do not invent experience, metrics, tools, employers, dates, titles, degrees, certifications, achievements | `contracts/README.md` → "Truthfulness in artifacts"; `contracts/cv-document.md` → truthfulness rules | T1 / T2 |
| If evidence is weak, say so; unsupported requirements are gaps; ATS never outranks truth | `contracts/README.md`; `contracts/evidence-map.md` (strength labels); `contracts/cv-document.md`; `contracts/gap-report.md` | T1 / T2 |
| No tables in CV content; markdown stays plain, linear, machine-readable | `contracts/cv-document.md` → format rules | T2 |
| Rendered output may use icons and columns when extraction passes; never as the sole carrier of critical information | `contracts/cv-document.md` (never in the document), `contracts/render-manifest.md` (visible-text and extraction gates), template `policy.md` | T2 / → T5a |
| Standard CV section names | `contracts/cv-document.md` → section order | T2 |
| Skills must not be limited to languages and tools when evidence supports more | `contracts/cv-document.md` → Skills; `contracts/knowledge-bank.md` → skills matrix groups | T2 |
| Header tags: never the only carrier of a skill; off by default; enabled only on explicit validated recommendation | `contracts/cv-document.md` → header tags; `contracts/validation-report.md` → `## Supported tag signals`; `contracts/fit-report.md` → `## Tag-signal verification` | T2 |
| Prefer clear, measurable, recruiter-readable bullets | `contracts/cv-document.md` → Experience | T2 |
| Every important claim traceable to an audited source | `contracts/cv-document.md`; `contracts/validation-report.md` → fact-check profile; `contracts/source-audit.md` | T2 |
| No `TODO`, `PLACEHOLDER`, or unsupported claims in the final CV | `contracts/cv-document.md` → truthfulness rules | T2 |
| Mandatory gates before the final CV, and after rendering | `skills/workflows/generate-targeted-cv/SKILL.md` (step table and gates); `contracts/run-manifest.md` → `## Gates`; `contracts/render-manifest.md` → `## Mechanical gates` | → T6 (record: T2) |
| Writer drafts markdown; the renderer converts validated content; the agent edits only agent content zones | `roles/experience-writer/capabilities/write-document.md`; `roles/renderer/capabilities/render-document.md` | → T3c / → T3e |
| Never change template style to make content fit; revise validated content instead; compress Experience gradually; reuse freed space | `contracts/cv-document.md` → length and compression; `contracts/render-manifest.md` → `## Fit outcome`; `skills/tools/render-cv-pdf/SKILL.md` (page target and fit policy) | T2 / → T5a |
| Escape special characters in generated content | template `policy.md` (escaping table); `roles/renderer/capabilities/render-document.md` | → T5a / → T3e |
| Profile links: fill aliases or handles only, never full addresses | `contracts/cv-document.md` → header block; template `policy.md` | T2 / → T5a |
| Empty optional sections must be removed | `contracts/cv-document.md` → section order | T2 |
| Re-validate after template rendering | `skills/workflows/generate-targeted-cv/SKILL.md`; `contracts/render-manifest.md` → rules (a content change invalidates earlier checks) | → T6 (record: T2) |
| External validators are advisory; run all enabled ones unless disabled; run last, after internal and render gates | `roles/reviewer/capabilities/run-external-checks.md`; the active set comes from `contracts/user-context.md`; ordering from the workflow | → T3d / T1 / → T6 |
| External validators never modify the CV; scores are not truth | `contracts/validation-report.md` (`advisory` status, producer/status matrix); `contracts/external-gate-decision.md` → rules | T2 |
| Keyword suggestions require fact validation; formatting suggestions may be applied; unsupported recommendations go to the gap report | `contracts/external-gate-decision.md` (verdicts and destinations); `contracts/gap-report.md` → `## External GAP_ONLY findings` | T2 |
| Re-run fact validation after applying any external recommendation | `contracts/external-gate-decision.md` → rules; `skills/workflows/generate-targeted-cv/SKILL.md` | T2 / → T6 |
| Registered external validator configs (`validators/external/registry.yaml`) | Superseded: the active validation set is recorded in the user's context — `contracts/user-context.md` | T1 |
| Execution pattern: the agent runs all automation; how to invoke helper scripts | skill `## Dependencies` sections and runbooks; new `AGENTS.md` | → T5* / → T8 |
| The twelve-step full-pipeline procedure | `skills/workflows/generate-targeted-cv/SKILL.md` | → T6 |
| Do not silently skip missing data; mark gaps explicitly | `contracts/README.md` → "Truthfulness in artifacts"; `contracts/run-manifest.md` (a skipped step carries its reason); `contracts/gap-report.md` | T1 / T2 |

### `prompts/00_full_pipeline.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| Step ordering and the rule that the final CV waits for its gates | `skills/workflows/generate-targeted-cv/SKILL.md`; state recorded in `contracts/run-manifest.md` → `## Steps`, `## Gates` | → T6 (record: T2) |
| External validator ordering and how recommendations are applied | `skills/workflows/generate-targeted-cv/SKILL.md`; `roles/reviewer/capabilities/{run-external-checks,gate-external-recommendations}.md` | → T6 / → T3d |
| Tag-signal handoff: analysis proposes, evidence verifies, tags stay out of the linear document, header tags off by default | Proposal: `contracts/requirements-profile.md`, `contracts/recruiter-signals.md` → `## Tag candidates`. Verification: `contracts/fit-report.md` → `## Tag-signal verification`, `contracts/validation-report.md` → `## Supported tag signals`. Placement and default: `contracts/cv-document.md` → header tags and annex | T2 |
| Header-title handoff: the writer chooses it, validation checks it, the renderer uses the validated title | `contracts/cv-document.md` → the header title; `contracts/validation-report.md` → `## Header title check`; `roles/renderer/capabilities/render-document.md` | T2 / → T3e |
| Master CV review runs last and does not modify master data | `contracts/bank-update-brief.md` (the hard rule of that contract); ordering in `skills/workflows/generate-targeted-cv/SKILL.md` | T2 / → T6 |

### `prompts/job_parser.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| The thirteen extraction items (role, seniority, company context, must-have, nice-to-have, responsibilities, technical/soft/domain keywords, hidden priorities, screening filters, red flags, scan signals) | `contracts/requirements-profile.md` → sections | T2 |
| Separate explicit requirements from inferred signals; do not infer unsupported requirements | `contracts/requirements-profile.md` → the explicit/inferred rule | T2 |
| Tag-candidate guidance: not only hard skills; short and job-relevant; mark explicit vs inferred; candidate truth is decided later | `contracts/requirements-profile.md` → `## Tag candidates` | T2 |
| How to read a vacancy to produce the above | `roles/vacancy-analyst/capabilities/analyze-job.md` | → T3b |

### `prompts/recruiter_signal_extractor.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| The nine extraction items (emphasis, hiring-manager priorities, pain points, business context, concerns, phrases to mirror, positioning influence, what not to include, scan signals) | `contracts/recruiter-signals.md` → sections | T2 |
| Do not invent context | `contracts/recruiter-signals.md` → the hard rule | T2 |
| Tag guidance: preserve short supported signals; not limited to hard skills; keep vague soft-skill labels out | `contracts/recruiter-signals.md` → `## Tag candidates` | T2 |
| How to read recruiter notes or a transcript | `roles/vacancy-analyst/capabilities/extract-recruiter-signals.md` | → T3b |
| The transcript such notes are drawn from | `contracts/transcript.md` | T2 |

### `prompts/evidence_mapper.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| Per-requirement mapping: source, supporting fact, strength Strong/Medium/Weak/None, GAP marker | `contracts/evidence-map.md` → entry structure | T2 |
| Use only canonical or audited evidence; do not invent metrics; do not convert weak into strong; suggest safer wording | `contracts/evidence-map.md` → entry structure and strength rules | T2 |
| Retrieval procedure over the bank | `roles/knowledge-bank-curator/capabilities/query-bank.md` | → T3a |
| **"Suggested CV usage" — placement half**: include in summary / skills / experience bullet; the Skills category taxonomy (technical · systems or domain · reliability or delivery · collaboration or working mode · language · do not include); do not map vague soft skills without concrete supporting wording | `contracts/cv-document.md` → `## Evidence placement` | T2 |
| **"Suggested CV usage" — tag half**: tags preserve secondary signals; every tag short, relevant and evidence-backed; a key skill is never preserved only as a tag; tags are not a loophole for unsupported keywords, domain claims, soft-skill labels or inflated ownership | `contracts/fit-report.md` → `## Tag-signal verification`; `contracts/cv-document.md` → header tags | T2 |
| A neutral "suggested placement" column in the map itself | Deliberate non-feature, recorded in `contracts/evidence-map.md`; revisit only if the writer proves to under-use evidence | T2 |

### `prompts/cv_writer.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| **Every CV-format rule** — section names and order, Skills composition and concrete labels, header title `Role \| Domain`, position header shapes, plain/linear markdown, no tables or icon-only facts, internal names replaced with public-facing descriptions, header tags off by default | `contracts/cv-document.md` | T2 |
| Experience job titles stay source-backed even when the header title is broader | `contracts/cv-document.md` → the header title | T2 |
| The writer's output annex: emphasis, omissions, header-title rationale, tag candidates with evidence notes and a render recommendation | `contracts/cv-document.md` → `## Annex: writer notes` | T2 |
| The truthful-writing procedure: use only supported facts, prioritise target-matching evidence, mirror keywords naturally, prefer achievements | `roles/experience-writer/capabilities/write-document.md` (procedure); `contracts/cv-document.md` (the form those rules take in a CV) | → T3c / T2 |

### `prompts/fact_validator.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| Claim classification: Supported / Partially supported / Unsupported / Exaggerated / Too vague / Needs evidence | `contracts/validation-report.md` → fact-check profile | T2 |
| What to check especially (titles, dates, companies, tools, languages, skills coverage, seniority, leadership, metrics, impact, domain, certifications, education, management scope, tags) | `contracts/validation-report.md` → fact-check profile | T2 |
| Report shape: critical issues, partial support, supported claims, header title check, supported tag signals, required edits | `contracts/validation-report.md` → common sections plus fact-check profile | T2 |
| Be strict; a metric absent from the sources is unsupported; familiarity never implies production experience; a market-facing title must not create a false claim | `contracts/validation-report.md` → fact-check profile rules; `roles/reviewer/capabilities/fact-check.md` | T2 / → T3d |
| The checking procedure itself, applicable to any document | `roles/reviewer/capabilities/fact-check.md` | → T3d |

### `prompts/ats_validator.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| The thirteen structural checks and the report shape (score, critical issues, keyword coverage, formatting risks, recommended edits, verdict) | `contracts/validation-report.md` → common sections plus the internal-check profile; the check specification itself in `skills/tools/validate-cv-ats/SKILL.md` | T2 / → T5b |
| ATS formatting rules (no tables, no images, no skill bars, no critical facts in header or footer, standard section names, simple bullets, text-based output) | `contracts/cv-document.md` → format rules; template `policy.md` for the rendered form | T2 / → T5a |
| Columns allowed only when extraction stays readable; inspect both extraction modes | `contracts/render-manifest.md` → `## Mechanical gates`; `skills/tools/render-cv-pdf/SKILL.md` | T2 / → T5a |
| Skills breadth validation; a key skill appearing only in a tag is a defect | `contracts/validation-report.md` (findings); `contracts/cv-document.md` (the rule being checked) | T2 |
| Verdict vocabulary Pass / Pass after edits / Fail | `contracts/validation-report.md` → status values | T2 |

### `prompts/position_matcher.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| The six weighted dimensions (40 / 20 / 15 / 10 / 10 / 5) | `contracts/fit-report.md` → `## Scores` | T2 |
| Report shape: overall score, strong / partial / gaps, risks, suggested positioning, should-apply verdict | `contracts/fit-report.md` → sections | T2 |
| Render-tag fit assessment | `contracts/fit-report.md` → `## Tag-signal verification` | T2 |
| Be critical; no credit for unsupported claims; distinguish experience from keyword presence; a tag never improves the score | `contracts/fit-report.md` → scoring rules | T2 |
| The scoring procedure, kept input-format-agnostic | `roles/vacancy-analyst/capabilities/score-fit.md`; the format declaration in `contracts/fit-report.md` → `## Basis` | → T3b / T2 |
| Position match as a **gate** before the final CV | **Deliberate delta:** the fit report is informational and gates nothing. The workflow declares an escalation rule that reads it instead | T2 / → T6 |

### `prompts/gap_report.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| The five sections: truth-based gaps, how the CV handles them, interview follow-ups, external GAP_ONLY findings, rejected recommendations | `contracts/gap-report.md` → sections | T2 |
| Only genuine gaps backed by earlier findings; never suggest unsupported claims or dishonest interview answers | `contracts/gap-report.md` → rules | T2 |
| The analysis procedure and its inputs | `roles/vacancy-analyst/capabilities/gap-analysis.md` | → T3b |

### `prompts/final_editor.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| Revise only to fix validated issues; remove unsupported claims; rewrite exaggerations; improve readability without adding facts | `roles/experience-writer/capabilities/edit-document.md` | → T3c |
| One-page fit: optimize Experience content first, compress gradually, reuse freed space, never change render style | `contracts/cv-document.md` → length and compression (the length target itself is declared by the caller: `skills/tools/render-cv-pdf/SKILL.md`) | T2 / → T5a |
| Preserve validated tag candidates separately; remove or soften any tag rejected by validation | `contracts/cv-document.md` → header tags, "On revision" | T2 |
| Do not add new material unsupported by canonical inputs or a refreshed bank | `contracts/cv-document.md` → truthfulness rules | T2 |

### `prompts/master_cv_review.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| The three gap categories: genuine gap · potentially underdocumented · depth gap | `contracts/bank-update-brief.md` → classification | T2 |
| The five output sections and the two per-item question formats | `contracts/bank-update-brief.md` → sections | T2 |
| Does not write master data; produces questions and conditional suggestions | `contracts/bank-update-brief.md` → the hard rule of that contract | T2 |
| Never suggest inventing experience, claiming side projects as professional work, or upgrading a level without new evidence; check the ledger before re-asking; prioritise recurring signals; keep questions answerable; do not duplicate the gap report | `contracts/bank-update-brief.md` → rules | T2 |
| The synthesis procedure over a run's artifacts | `roles/knowledge-bank-curator/capabilities/ingest-run-feedback.md` | → T3a |

### `prompts/build_master_cv_banks.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| Source of truth; indexes never override canonical inputs | `contracts/knowledge-bank.md` → shared rules | T2 |
| Completeness mandate; the bank preserves, the run selects | `contracts/knowledge-bank.md` → shared rules | T2 |
| Education, certifications and credentials as dedicated first-class sections; an absence is recorded, not silent | `contracts/knowledge-bank.md` → `## Education`, `## Certifications`, Conservative Gap Notes | T2 |
| `## Positions (employment history)` with title, company, city and country, month-level dates; every role including freelance and self-education | `contracts/knowledge-bank.md` → `## Positions (employment history)`, granularity rules | T2 |
| Self-check against canonical passages: correct, tag as inferred, or remove | `contracts/knowledge-bank.md` → citation rule; procedure in `roles/knowledge-bank-curator/capabilities/build-banks.md` | T2 / → T3a |
| `## Source Metadata` block written on every refresh | `contracts/knowledge-bank.md` → `## Source Metadata` | T2 |
| Experience bank: themed organisation, explicit and implicit evidence, bullet quality rules, conservative verbs, one claim per bullet, `(inferred from …)`, Conservative Gap Notes | `contracts/knowledge-bank.md` → shared rules and experience-bank sections | T2 |
| Skills matrix: capability groups beyond tools, entry format, conservative level labels, no numeric ratings, implicit capability rule | `contracts/knowledge-bank.md` → skills matrix sections | T2 |
| Skills matrix: the second pass over sources for patterns and practices | `roles/knowledge-bank-curator/capabilities/build-banks.md` | → T3a |
| Skills matrix: external validation of inferred capability names, and internal-to-public mappings | Procedure in `roles/knowledge-bank-curator/capabilities/build-banks.md`; the resulting entry form in `contracts/knowledge-bank.md` | → T3a / T2 |
| Projects: what counts as a project, entry structure, entry rules | `contracts/knowledge-bank.md` → projects sections | T2 |
| Coverage pass after building | `roles/knowledge-bank-curator/capabilities/build-banks.md`; `skills/workflows/refresh-knowledge-bank/SKILL.md` | → T3a / → T4 |
| Candidate identity (new — no predecessor rule) | `contracts/knowledge-bank.md` → `## Candidate` | T2 |

### `prompts/template_renderer.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| Use the selected template exactly; edit only agent content zones; do not invent missing fields; do not leave placeholders | `roles/renderer/capabilities/render-document.md` | → T3e |
| Never change style, geometry, spacing, typography, colors or columns to make content fit; send content back instead | `contracts/render-manifest.md` → `## Fit outcome`; `contracts/cv-document.md` → length and compression; `skills/tools/render-cv-pdf/SKILL.md` | T2 / → T5a |
| Fill the role field from the validated CV header title, never from the vacancy title | `contracts/cv-document.md` → the header title; `roles/renderer/capabilities/render-document.md` | T2 / → T3e |
| Profile links: alias or handle only; the template constructs the address | `contracts/cv-document.md` → header block; template `policy.md` | T2 / → T5a |
| Header tags disabled by default at render time | `contracts/cv-document.md` → header tags; template `policy.md` | T2 / → T5a |
| Escaping table; template macro names; two-column placement of sections; alternate-text labels for decorative glyphs; chip helpers | template `policy.md` and `skills/tools/render-cv-pdf/` | → T5a |
| Do not include empty optional sections | `contracts/cv-document.md` → section order | T2 |
| Post-render extraction inspection in both modes; simplify the layout if facts are lost or interleaved | `contracts/render-manifest.md` → `## Mechanical gates`; `skills/tools/render-cv-pdf/SKILL.md` (the gate sequence) | T2 / → T5a |
| If content conflicts with validation reports, follow the validation reports | `roles/renderer/capabilities/render-document.md`; `contracts/render-manifest.md` → rules | → T3e / T2 |

### `prompts/external_validator_runner.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| Run or prepare each enabled validator; check inputs exist; confirm local gates ran first | `roles/reviewer/capabilities/run-external-checks.md`; the active set from `contracts/user-context.md`; gate state read from `contracts/run-manifest.md` | → T3d / T1 / T2 |
| Per-validator command, browser policy, captcha policy, troubleshooting | `skills/tools/validate-cv-enhancv/SKILL.md`, `skills/tools/validate-cv-resumly/SKILL.md` — runbook and `## Dependencies` sections | → T5c / → T5d |
| Manual-use fallback with a prepared checklist | The same validator `SKILL.md` files; a skipped or manual step is recorded in `contracts/run-manifest.md` with instructions | → T5c / → T5d (record: T2) |
| Prefer the correctly named export as input | `skills/workflows/generate-targeted-cv/SKILL.md` (naming rule); `contracts/render-manifest.md` → `## Exports` | → T6 / T2 |
| Do not modify the CV; do not accept recommendations as true; only produce or normalize reports | `contracts/validation-report.md` (`advisory` status); `roles/reviewer/` invariants | T2 / → T3d |

### `prompts/external_report_normalizer.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| The normalized report structure: validator, input files, scores, critical issues, keyword gaps, formatting issues, content suggestions, potentially unsafe suggestions, recommended next actions | `contracts/validation-report.md` → normalized-external profile | T2 |
| Action labels: safe formatting edit · needs fact validation · gap only · reject | `contracts/validation-report.md` → normalized-external profile | T2 |
| The normalization procedure | `roles/reviewer/capabilities/normalize-external-report.md` | → T3d |

### `prompts/external_validation_gate.md`

| Predecessor rule or section | Designated home | Status |
|---|---|---|
| The five decision labels APPLY / APPLY_WITH_REWRITE / GAP_ONLY / REJECT / MANUAL_REVIEW | `contracts/external-gate-decision.md` → verdicts | T2 |
| Report shape: accepted, rewrite-required, gaps to document, rejected, manual review, final recommendation Proceed / Revise / Do not send | `contracts/external-gate-decision.md` → sections | T2 |
| Fact validation overrides external advice; no unsupported skills, tools, metrics, domain experience or ownership; keyword suggestions only where the experience is supported; formatting suggestions usually safe | `contracts/external-gate-decision.md` → rules | T2 |
| Never accept a suggestion that would restyle the template to fit content; apply the content-first fit rule | `contracts/external-gate-decision.md` → rules; `contracts/cv-document.md` → length and compression | T2 |
| Persistent conservative constraints may be recorded without user approval | **Deliberate delta:** the gate no longer writes the ledger. It emits `## Constraint proposals`, ingested by `curator.maintain-constraints` at flow close | T2 |
| The gating procedure | `roles/reviewer/capabilities/gate-external-recommendations.md` | → T3d |

### Other predecessor assets

Not rule files, but they carry normative content; the port map assigns each a home.

| Predecessor asset | Designated home | Status |
|---|---|---|
| `templates/cv-ats-agent-template.tex` | `skills/tools/render-cv-pdf/templates/ats-onepage-latex/template.tex` (copied verbatim) | → T5a |
| `templates/template_policy.md` + `template_selection.md` | the shipped template's `policy.md` (merged; layout placement, fit policy, extraction contract, column gate, escaping table, section order) | → T5a |
| `templates/latex_rendering_notes.md` + `runbooks/04_render_latex.md` | the template's `runbook.md` + the render tool's runbook section | → T5a |
| `validators/external/registry.yaml` | Superseded by the recorded validation set — `contracts/user-context.md` | T1 |
| `validators/external/{enhancv,resumly}.yaml` + `README.md` | `skills/tools/validate-cv-{enhancv,resumly}/SKILL.md` | → T5c / → T5d |
| `scripts/*` (validator runner, ATS checks, extraction check, freshness check, run scaffolding) | The owning skill or role folder, per the port map | → T3a / → T5a–T5c / → T6 |
| `runbooks/01_setup.md` | `roles/setup-master/` + the section template in `contracts/user-context.md` | → T3f / T1 |
| `runbooks/02_run_pipeline.md` | the CV workflow's usage section; the repository README quickstart | → T6 / → T8 |
| `data/master/*` | `outputs/knowledge-bank/`, read as `contracts/knowledge-bank.md` instances | → T4 |
| `data/jobs/<job>/` | a run's job dossier, per `contracts/job-dossier.md` | T2 (contract) / → T7 |
| Completed runs under `outputs/` | Kept as format references only; never content or style authority (run isolation) | T1 |

### Deliberate deltas from the predecessor

Rules that were **not** ported, each by an explicit design decision rather than an omission:

| Predecessor rule | Decision |
|---|---|
| Optional secondary document export alongside the PDF | Dropped. The PDF is the only final deliverable; no contract carries a second export format. |
| Position match validation as a mandatory gate | The fit report is informational and gates nothing; the workflow declares an escalation rule that reads it. |
| The external gate writing the constraints file directly | Replaced by the sole-writer rule: the gate proposes, `curator.maintain-constraints` ingests. |
| A "suggested CV usage" block inside the evidence map | Split by design: placement → `cv-document`, tag verification → `fit-report`. The evidence map stays neutral. |
| Numeric artifact prefixes (`00_`–`10_`) fixing the pipeline order | Replaced by contract-named artifacts plus the run manifest's step checklist and artifact index. |
