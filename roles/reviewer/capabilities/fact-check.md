# Capability: reviewer.fact-check

## Purpose

The universal truthfulness check. Given any candidate document and the sources that may serve as
evidence, it classifies every meaningful claim in that document by how well the evidence supports it,
and produces a `validation-report` with findings, required edits and a verdict.

This capability is **not part of the registered validation set**. It is the reviewer's own capability
and every CV workflow invokes it directly and unconditionally, because the truthfulness invariant
forbids finalizing a document nobody has checked. It cannot be disabled, deselected or SKIPPED; if it
cannot run, the flow is blocked rather than continued.

It is also the common truthfulness layer for every other operation in this role: whenever a document
changes — after an edit, after a render that altered content, after any accepted external
recommendation — this check runs again before the document may be treated as final.

## Inputs

| Parameter | Contract / description | Required |
|---|---|---|
| `document` | the document under review — a `cv-document` instance, or any other candidate-document contract | required |
| `knowledge_bank` | `knowledge-bank` — the curated evidence base (experience, projects, skills, and the candidate identity section) | required |
| `constraints_ledger` | `constraints-ledger` — negative-evidence guardrails | required when it exists; its absence is recorded in the report |
| `evidence_map` | `evidence-map` — per-requirement evidence with citations and strength | optional (present in a CV run; absent when the document was written without one) |
| `source_audit` | `source-audit` — the inventory and classification of this run's inputs | optional |
| `canonical_sources` | the canonical source documents listed in the source audit, when the flow passes them for direct verification | optional |
| `requirements_profile` | `requirements-profile` — context for positioning claims and for judging gaps | optional |
| `recruiter_signals` / `job_dossier` | `recruiter-signals`, `job-dossier` — emphasis signals only | optional |
| `report_path` | where to write the report | required |
| `in_run_constraint_proposals` | constraint proposals raised by earlier steps of this same run, not yet ingested into the ledger | optional |

## Outputs

| Parameter | Contract | Status values |
|---|---|---|
| `report_path` | `validation-report` | `pass`, `pass-after-edits`, `fail`, `blocked` |

The report's verdict follows the role's verdict vocabulary. Re-checking overwrites the same report in
place with `revision:` incremented.

## Procedure

1. **Confirm the inputs.** Read the document and each evidence source passed. If the document or the
   knowledge bank is missing or unreadable, write a `blocked` report saying exactly what is missing
   and stop — never check a document against whatever happened to be readable.
2. **Build a claim inventory.** Walk the document top to bottom and list every meaningful claim: not
   only body bullets, but headline and positioning lines, section headings that assert a capability,
   employment titles, employers, dates, and any compact scan label. A claim is anything a reader
   could quote back as a fact about the candidate.
3. **Attach evidence to each claim.** For each one, find the supporting passage in the evidence
   sources and record a citation (source file and section/bullet). Prefer the most canonical source
   available; the evidence map is a shortcut to it, not a substitute for it.
4. **Classify each claim** as exactly one of:
   - **Supported** — the evidence states it, at the strength the document states it;
   - **Partially supported** — the underlying fact exists but the document says more (broader scope,
     stronger seniority, larger impact) than the evidence carries;
   - **Unsupported** — no evidence states it;
   - **Exaggerated** — evidence exists but the wording inflates it;
   - **Too vague** — the wording cannot be verified because it says nothing checkable;
   - **Needs evidence** — plausible and probably true, but no source in scope confirms it.
5. **Apply the constraints.** Check every claim against the constraints ledger and against any
   in-run constraint proposals. A claim that a constraint forbids is a blocking finding even when
   another source seems to support it — the ledger records why that support was judged insufficient.
6. **Run the surface checks** listed under Rules (positioning line, employment titles, dates,
   employers, tooling and languages, skills coverage and wording, seniority, leadership and
   management scope, metrics, business impact, domain experience, education, certifications, compact
   scan labels, internal names).
7. **Write the report** against the `validation-report` contract: findings with severity and the
   concrete edit each one requires, the claim classification, and the verdict. Findings are ordered
   blocking first. State required edits as *what must become true* ("drop the ownership wording; the
   source records participation, not ownership"), never as a rewritten document.
8. **Propose constraints.** Any claim that had to be removed or softened, and any wording risk likely
   to reappear, becomes an entry under `## Constraint proposals`. Nothing to propose ⇒ `None.`
9. **On a re-check** (after edits, re-render, or an accepted external recommendation): re-check the
   **whole** document, not only the changed lines — an edit elsewhere can change what a neighbouring
   claim implies. Overwrite the report, increment `revision:`, and note in the report which change
   triggered the re-check.

## Rules

**Strictness**

- Be strict. When evidence and wording disagree, the wording is wrong.
- If a metric is not in a source, it is unsupported. A rounded, restated or recomputed metric is a
  new metric and needs its own evidence.
- A technology recorded only as familiar, studied, or used in a personal context must not be worded
  so as to imply professional or production experience.
- Weak evidence is reported as weak. Strength markers are never rounded up.
- Never rewrite an unsupported claim into a supported-sounding one — that is inventing with extra
  steps. Say what is unsupported and what the truthful boundary is; the writer rewrites.
- Unknown is a value: when a claim cannot be verified from the sources in scope, that is
  `Needs evidence` and the verdict cannot be `Pass`.

**Positioning lines (the document's headline / title line)**

- A positioning line may be market-facing and tailored to the target, but it must not create a false
  claim — in particular by copying a domain-specific vacancy title the candidate's evidence does not
  support.
- Verify separately that the employment titles inside the document remain exactly source-backed. A
  tailored headline never licenses a tailored job title.
- Report explicitly, in its own finding or section: whether the positioning line is truthful and
  supported, whether it accidentally implies unsupported domain experience, and whether employment
  titles stayed source-backed.

**Compact scan labels (optional short tags a render may place in a header)**

- They are off by default. Treat a proposed label as an exception that must earn its place.
- A label does not need to repeat body text verbatim, but it must be relevant, source-backed, and
  incapable of misleading about domain experience, ownership, seniority, or production use.
- If a label names an important skill or capability, verify that the capability also appears in the
  document body (summary, skills, experience). Flag any label that is the **only** carrier of an
  important fact.
- A label that is safe but merely duplicates the body is marked **safe-but-omit**, not approved.
- List the labels that are safe to use, each with its evidence basis; omit the section entirely when
  none are proposed.

**Skills claims**

- Skills may legitimately be broader than tool names: technical skills, systems and problem domains,
  reliability and delivery practices, collaboration or working-mode skills, and languages all count.
- Each of them still needs evidence. Breadth is not a licence for unsupported abstraction.

**Sources and confidentiality**

- Recruiter notes, calls and other people-derived inputs are emphasis and positioning signals only.
  They may never create or corroborate a candidate fact.
- Internal product, project or team names must appear as public-facing descriptions. Flag any leak of
  a confidential internal name as a finding.
- Never cite another run's outputs as evidence, style authority or precedent. Evidence comes from the
  knowledge bank, the canonical sources of this run, and this run's own artifacts.

**Document-type neutrality**

- The document's own contract declares its sections; check the claims the document actually contains
  rather than assuming a CV layout. Rules written above in CV vocabulary apply to the equivalent
  surface of any candidate document — a profile headline is a positioning line, a profile summary is
  a summary.
- If the document declares a contract this capability does not recognize, still check every claim in
  it, and record the unrecognized contract as a finding rather than skipping the check.

**Independence**

- Never edit the document, never write the knowledge bank, the ledger, or any artifact other than
  this report.
- The verdict comes from findings. No score, internal or external, overrides it.

## Failure and skip conditions

- **Never skipped.** This capability has no SKIPPED outcome: it is mandatory in every flow that
  produces a candidate document.
- **Blocked** — the document or the knowledge bank is missing/unreadable, or the document declares an
  incompatible major version of its contract. Write a `blocked` report naming what is missing and
  what the flow must supply, and stop.
- **Degraded evidence** — an optional evidence source is missing (no evidence map, no source audit).
  The check still runs against what exists; the report records which sources were unavailable, and
  claims that only those sources could have confirmed are classified `Needs evidence`.
- **Ambiguous evidence** that decides between `Supported` and `Unsupported` is escalated to the user
  through the flow, and recorded as a finding meanwhile — never resolved by assumption.
- A `Fail` verdict is a normal, expected outcome: it hands the document back to the writer's edit
  step and does not end the flow.
