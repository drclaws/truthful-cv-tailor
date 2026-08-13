---
name: generate-targeted-cv
description: Produces a truthful, target-specific CV for one vacancy — analyses the job side, retrieves cited evidence from the knowledge bank, writes and checks the document, renders the PDF deliverable, runs the registered external checks, and closes with the gap report, the bank update brief and the ledger ingestion.
---

# Workflow: generate-targeted-cv

Flow version: 1.0

## Purpose

One run of this flow answers one question: **what can this candidate truthfully say to this
vacancy?** It turns a job dossier plus the knowledge bank into a rendered PDF whose every claim is
traceable, whose gaps are written down rather than papered over, and whose state is fully legible
from a single manifest.

The flow orchestrates five roles — `vacancy-analyst`, `knowledge-bank-curator`, `experience-writer`,
`reviewer`, `renderer` — and adds what no role may do for itself: resolving the user's context,
computing every path, deciding order and parallelism, holding the gates, and closing the constraints
ledger.

What it deliberately does **not** do: it never writes the knowledge bank (a stale bank is fixed by
`refresh-knowledge-bank`, never here), it never decides whether the candidate should apply (it asks),
and it never lets a machine-readability score outrank the truth.

## When to run

Run this flow when a specific vacancy is worth a tailored application and its job dossier exists —
at minimum a job description. Run it again for the same vacancy when the dossier gained material
(a screening call, company notes) or when the bank was refreshed with evidence the earlier run could
not use; a rerun is a **new run directory**, never an edit of the old one.

Do not run it to evaluate whether a vacancy is worth pursuing at all: `vacancy-analyst.score-fit`
answers that on its own, against the bank, without producing a CV.

Do not run it while the bank is stale. Step 2 checks; a stale verdict routes to the
`refresh-knowledge-bank` workflow first, and this flow resumes afterwards.

## Run identifier and output layout

`run-id` is the **vacancy slug**: `<company>-<role>`, lowercased, non-alphanumeric characters
collapsed to single hyphens, derived from the job dossier's own wording. A rerun appends `-2`, `-3`,
… — a run directory is never reused and never overwritten.

```
outputs/generate-targeted-cv/<run-id>/     # this run; nothing outside it is written by this flow
outputs/knowledge-bank/                    # THE BANK — read-only here, except the ledger at step 24
```

Every path below is **computed by this flow and passed to roles and tools as an explicit
parameter**. Contracts fix no placement; the three declarations that follow are this flow's.

### Fixed artifacts

Steps that always run. Contract → default filename.

| Contract | Default path | Notes |
|---|---|---|
| `run-manifest` | `<run>/run.md` | Written as the run proceeds, never reconstructed at the end. |
| `job-dossier` | `<run>/position/` | The run's job-side inputs. On a rerun, copied from the previous run (see *Rerun and the dossier*). |
| `source-audit` | `<run>/source_audit.md` | |
| `requirements-profile` | `<run>/requirements_profile.md` | |
| `recruiter-signals` | `<run>/recruiter_signals.md` | Written even when the run has no people-side input — then with `status: skipped`. |
| `evidence-map` | `<run>/evidence_map.md` | |
| `cv-document` | `<run>/draft_cv.md` | `status: draft`; overwritten in place by each edit pass, `revision:` incremented. |
| `validation-report` | `<run>/fact_check.md` | The mandatory `reviewer.fact-check`. **Always runs**, never part of the registered set, never skippable. |
| `fit-report` | `<run>/fit_report.md` | Informational; gates nothing. Read by the escalation rule below. |
| `cv-document` | `<run>/final_cv.md` | `status: final`; the instance that is rendered and sent. |
| `render-manifest` | `<run>/render/render_report.md` | Lives inside an intermediate directory; it is still a contract artifact and is indexed as one. |
| `gap-report` | `<run>/gap_report.md` | |
| `bank-update-brief` | `<run>/bank_update_brief.md` | Last artifact of the run. |
| `constraints-ledger` | `<bank-dir>/constraints.md` | **Outside the run.** Written only by `knowledge-bank-curator.maintain-constraints` at flow close, and indexed in `run.md` by path. |

### Flexible stages

Steps whose file **set** depends on the user's registered validation set, not on this layout. Each
row is a path pattern instantiated per registered item at run time; if the set has no entry of a
kind, none of that kind's files exist and nothing else changes.

| Stage | Path pattern | Instantiated per |
|---|---|---|
| internal check report | `<run>/checks/<validator>.md` | each entry of the registered set of kind `internal` |
| external raw capture | `<run>/external/<validator>_raw.<ext>` | each capture the entry's own spec declares, for each entry of kind `external` (`<ext>` is whatever the spec captures: `.md`, `.html`, `.png`, …) |
| normalized external report | `<run>/external/<validator>_report.md` | each external entry that produced a capture |
| external run record | `<run>/external/run_record.md` | once, when the set has at least one `external` entry — see *Where the per-entry external outcomes go* |
| external gate decision | `<run>/external/gate_decision.md` | once, when at least one external entry produced a normalized report |

`<validator>` is the entry's **registered name**, as recorded in the user's validation set,
lowercased with non-alphanumeric characters collapsed to hyphens. The name comes from the registered
set; this file names no validator.

The mandatory truthfulness check is **not** one of these stages. It is `reviewer.fact-check`, it
writes the fixed artifact `<run>/fact_check.md`, and it runs whatever the registered set contains —
including when the set is empty.

### Intermediate directories

Build byproducts and raw material. Declared here, at the workflow-rules level, and in no contract.

| Directory | Holds | Rules |
|---|---|---|
| `<run>/render/` | the typeset source (`final_cv.tex`), the typesetting toolchain's byproducts, and the render report | Passed to the render tool as both `source_out`'s directory and `build_dir` (see below). Byproducts are never part of the deliverable. |
| `<run>/exports/` | the deliverable, named by *The export naming rule* below | Exactly one deliverable per run. Nothing else is written here. |
| `<run>/work/` | inputs a check spec asks the executing role to prepare (for example a keyword list derived from the requirements profile), raw script captures, and any content fetched through a fallback reader | Byproducts, not artifacts: nothing here is a contract instance, nothing here is evidence, and no later run may read it. Listed in the artifact index as byproducts. |

**`build_dir` is passed explicitly.** The render tool treats it as optional and would default it to
the directory of the typeset source — which here is the same `<run>/render/`. The flow passes it
anyway: this flow declares its intermediate directories, it passes every path it computes, and no
step's output location may depend on a tool-side default that a future template bundle could move.

### Example run folder — illustrative, NOT normative

With one internal and two external entries registered. A different registered set produces a
different file set, and only the fixed artifacts above are guaranteed.

```
outputs/generate-targeted-cv/<run-id>/
├── run.md
├── position/
├── source_audit.md
├── requirements_profile.md          # ─┐ group A
├── recruiter_signals.md             # ─┘
├── evidence_map.md
├── draft_cv.md
├── fact_check.md                    # ─┐ group B: reviewer.fact-check (always)
├── checks/validate-cv-ats.md        #  ├   + one report per registered internal entry
├── fit_report.md                    # ─┘   ∥ the informational fit report
├── final_cv.md
├── render/final_cv.tex  render/render_report.md
├── exports/<FirstName><Surname>.pdf
├── external/validate-cv-enhancv_raw.md   external/validate-cv-enhancv_report.md
├── external/validate-cv-resumly_raw.md   external/validate-cv-resumly_report.md
├── external/run_record.md  external/gate_decision.md
├── work/
├── gap_report.md
└── bank_update_brief.md
```

`checks/validate-cv-ats.md` is present in this picture **only because the illustration registers an
ATS entry**. Remove it from the set and the file is simply absent; no step of this flow changes.

## The export naming rule

**This workflow owns the naming of the deliverable.** The rule lives here — not in a contract, not
in user context, not in the render tool, and not in any validator spec. Those apply it and check it;
they never define it.

> The deliverable is named **`<FirstName><Surname>.pdf`**.

How it is built, in order:

1. Read the knowledge bank's `## Candidate` section (contract `knowledge-bank`). It is the only
   admissible source of the candidate's identity — never a file path, never a previous run, never a
   CV, never the agent's own recollection.
2. Take the **first given name** and the **family name** from the full name as that section records
   it. Middle names, patronymics, honorifics and suffixes are dropped.
3. Remove every character that is not a letter or a digit from each part (a hyphenated or
   apostrophised name loses the punctuation, not the letters). Keep each part's letters exactly as
   recorded, diacritics included: the name is never transliterated, translated, anglicised or
   re-capitalised to look tidier.
4. Concatenate the two parts with no separator, then append `.pdf`. PDF is the only deliverable this
   repository produces.

Escalations belonging to this rule — all of them questions, never guesses:

- **`## Candidate` is absent** (a bank imported before the section existed): the rule is never
  reached in that state — G2 settles it at step 2, by running `refresh-knowledge-bank` so the curator
  derives the section. If a run somehow arrives here without one, ask the user for the name rather
  than deriving it from anywhere else, and record the answer in `run.md`.
- **`## Candidate` records two spellings** with the conflict marked: ask which to use. The flow never
  picks one.
- **The rule yields a name the filesystem cannot hold**: report it and ask. Do not silently
  substitute characters.

The resolved name is passed on as a value, three times: to the render tool as `export_name` (its
gate 5 checks the produced filename against it), to any external entry whose spec declares a
naming-pattern parameter (so the entry enforces *this* rule rather than nothing), and into `run.md`
so the user can find the file by name.

## Inputs

What one run of this flow is given. An index, not a second home for rules: each row points at the
section that owns it. Every value here is resolved or computed before step 3 and passed onward
explicitly — this flow derives nothing from repository layout.

| Input | Contract / description | Required |
|---|---|---|
| `output_root` | the directory this engine writes into: this run's directory is `<output-root>/generate-targeted-cv/<run-id>/`, and the knowledge bank is `<output-root>/knowledge-bank/` unless `bank_dir` is passed separately. Supplied with the request, never inside this package, never defaulted — the rule and its reasons are `engine-conventions` → *Where a run writes*. | required |
| `run_id` | the vacancy slug, built as *Run identifier and output layout* above defines it | required |
| job material | the vacancy's own material: at minimum a readable job description, plus any screening transcripts (contract `transcript`), people notes and company notes. It becomes the run's `job-dossier` instance at `<run>/position/`. | required |
| user context | contract `user-context`, resolved at step 1 through the declared order. Supplies the canonical experience sources, the active validation set, the per-skill settings and the additional rules; *User-context settings* below states what this flow does with each. | required |
| `bank_dir`, `<ledger>` | the knowledge bank directory (contract `knowledge-bank`) and its `constraints.md` (contract `constraints-ledger`), resolved at preflight; `bank_dir` defaults to `<output-root>/knowledge-bank/` and `<ledger>` to the `constraints.md` inside it when neither is passed separately — derived from a value the request supplied, never from where these files sit. Read-only to this flow, except the ledger at step 24. | required |
| the previous run's `position/` | on a rerun for the same vacancy: the earlier run's job dossier, **copied** into the new run rather than pointed at — see *Rerun and the dossier* at step 3. | optional |

Nothing is defaulted. An input that did not resolve is a question to the user, recorded in `run.md`
`## Open questions`; the flow never fills one in from a previous run, from a canonical source it is
not allowed to read, or from its own recollection.

## Steps

`executor` is the `role.capability` that runs the step, `tool:<name>` for a tool executed by its
owning role, or `flow` for orchestration the flow does itself. Every path a role receives is
passed explicitly by the flow; `<bank-dir>` and `<ledger>` are the knowledge bank directory and its
`constraints.md`, resolved at preflight.

| # | Step | Executor | Contract | Paths passed | Group | Gate |
|---|---|---|---|---|---|---|
| 0 | Resolve this package's root, then load `engine-conventions` | `flow` | — | — | — | — |
| 1 | Resolve user context | `flow` | `user-context` | — | — | G1 |
| 2 | Check the bank is usable | `knowledge-bank-curator.check-freshness` | — (verdict returned) | `sources`, `bank_dir` | — | G2 |
| 3 | Scaffold the run, seed the manifest | `flow` (`scripts/create_run.py`) | `run-manifest` | `<run>/`, `<run>/run.md`, `<run>/position/` | — | — |
| 4 | Audit the job-side inputs | `vacancy-analyst.audit-sources` | `source-audit` | `run_id`, `job_dossier_path=<run>/position/`, `transcript_paths`, `additional_inputs`, `run_manifest_path=<run>/run.md`, `constraints_ledger_path=<ledger>`, `output_path=<run>/source_audit.md` | — | G3 |
| 5 | Analyse the vacancy | `vacancy-analyst.analyze-job` | `requirements-profile` | `run_id`, `job_dossier_path`, `source_audit_path=<run>/source_audit.md`, `constraints_ledger_path`, `output_path=<run>/requirements_profile.md` | **A** | — |
| 6 | Extract recruiter signals | `vacancy-analyst.extract-recruiter-signals` | `recruiter-signals` | `run_id`, `job_dossier_path`, `transcript_paths`, `people_notes`, `source_audit_path`, `constraints_ledger_path`, `output_path=<run>/recruiter_signals.md` | **A** | — |
| 7 | Retrieve evidence (batch) | `knowledge-bank-curator.query-bank` | `evidence-map` | `bank_dir`, `requirements_profile=<run>/requirements_profile.md`, `constraints_ledger`, `recruiter_signals=<run>/recruiter_signals.md`, `in_run_proposals`, `output_path=<run>/evidence_map.md`, `run_id` | — | G4 |
| 8 | Write the draft | `experience-writer.write-document` | `cv-document` | `document_format_contract=cv-document`, `evidence_source=<run>/evidence_map.md`, `requirements_source`, `signals_source`, `constraints_ledger`, `in_run_proposals`, `source_audit`, `additional_rules`, `output_path=<run>/draft_cv.md`, `run_id`, `status=draft` | — | — |
| 9 | Truthfulness check (mandatory) | `reviewer.fact-check` | `validation-report` | `document=<run>/draft_cv.md`, `knowledge_bank`, `constraints_ledger`, `evidence_map`, `source_audit`, `requirements_profile`, `recruiter_signals`, `in_run_constraint_proposals`, `report_path=<run>/fact_check.md` | **B** | G5 |
| 10 | Registered internal checks | `reviewer.run-check` — one invocation per entry | `validation-report` | `check_spec`, `check_name`, `check_inputs` (exactly what that spec declares), `check_settings`, `run_manifest=<run>/run.md`, `report_path=<run>/checks/<validator>.md` | **B** | G6 |
| 11 | Score the fit | `vacancy-analyst.score-fit` | `fit-report` | `run_id`, `requirements_profile_path`, `candidate_data_path=<run>/draft_cv.md`, `candidate_data_format=cv-document`, `recruiter_signals_path`, `job_dossier_path`, `constraints_ledger_path`, `tag_candidates_source=<run>/draft_cv.md`, `output_path=<run>/fit_report.md` | **B** | — |
| 12 | Edit loop (while any check fails) | `experience-writer.edit-document` | `cv-document` | `document_path=<run>/draft_cv.md`, `document_format_contract`, `findings` (the failing reports), `evidence_source`, `requirements_source`, `signals_source`, `constraints_ledger`, `output_path=<run>/draft_cv.md`, `status=draft` | — | G5, G6 re-run |
| 13 | Fit escalation | `flow` | — (reads `fit-report`) | `<run>/fit_report.md` | — | G7 |
| 14 | Promote the cleared draft | `experience-writer.edit-document` | `cv-document` | `document_path=<run>/draft_cv.md`, `caller_instruction`, `evidence_source`, `constraints_ledger`, `output_path=<run>/final_cv.md`, `status=final` | — | G8 |
| 15 | Re-check the final instance | `reviewer.fact-check`; `reviewer.run-check` per implicated entry | `validation-report` | `document=<run>/final_cv.md`; same report paths, `revision:` incremented | — | G5, G6 |
| 16 | Render the deliverable | `renderer.render-document` via `tool:render-cv-pdf` | `render-manifest` | `document=<run>/final_cv.md`, `template` (resolved from user context), `settings` (`page_target`), `export_name`, `source_out=<run>/render/final_cv.tex`, `export_out=<run>/exports/<export_name>`, `manifest_out=<run>/render/render_report.md`, `build_dir=<run>/render/`, `validation_reports=<run>/fact_check.md` + every `<run>/checks/<validator>.md` | — | G9 |
| 16b | Re-check the rendered form | `reviewer.run-check` — one invocation per implicated entry | `validation-report` | `check_spec`, `check_name`, the inputs of step 10 **plus** `rendered_pdf=<run>/exports/<export_name>` and the two text extractions prepared into `<run>/work/`, `check_settings`, `run_manifest=<run>/run.md`, `report_path=<run>/checks/<validator>.md` (`revision:` incremented) | — | G6 |
| 17 | Resolve an overflow or a red gate | `experience-writer.edit-document` → step 15 → step 16 → step 16b | `cv-document` | as steps 14–16b, on `<run>/final_cv.md` | — | G5, G6, G9 |
| 18 | Run the external checks | `reviewer.run-external-checks` | raw captures + `validation-report` (run record) | `external_entries`, `deliverable=<run>/exports/<export_name>`, `document=<run>/final_cv.md`, `job_inputs`, `run_manifest=<run>/run.md`, `raw_capture_paths=<run>/external/<validator>_raw.<ext>`, `report_path=<run>/external/run_record.md` | **C** | G10 |
| 19 | Normalize each capture | `reviewer.normalize-external-report` — one invocation per capture | `validation-report` (advisory) | `raw_capture`, `entry_name`, `submitted_deliverable`, `document=<run>/final_cv.md`, `job_inputs`, `report_path=<run>/external/<validator>_report.md` | **C** | — |
| 20 | Gate the external recommendations | `reviewer.gate-external-recommendations` | `external-gate-decision` | `normalized_reports`, `fact_check_report=<run>/fact_check.md`, `internal_reports`, `render_manifest=<run>/render/render_report.md`, `document=<run>/final_cv.md`, `knowledge_bank`, `constraints_ledger`, `evidence_map`, `requirements_profile`, `report_path=<run>/external/gate_decision.md` | — | G11 |
| 21 | Apply accepted advice (conditional) | `experience-writer.edit-document` → step 15 → step 16 → step 16b | `cv-document` | `document_path=<run>/final_cv.md`, `gate_decisions=<run>/external/gate_decision.md`, `evidence_source`, `constraints_ledger`, `output_path=<run>/final_cv.md`, `status=final` | — | G5, G6, G9 |
| 22 | Report the gaps | `vacancy-analyst.gap-analysis` | `gap-report` | `run_id`, `requirements_profile_path`, `evidence_map_path`, `cv_document_path=<run>/final_cv.md`, `validation_report_paths`, `fit_report_path`, `external_gate_decision_path`, `recruiter_signals_path`, `constraints_ledger_path`, `output_path=<run>/gap_report.md` | — | — |
| 23 | Brief the bank | `knowledge-bank-curator.ingest-run-feedback` | `bank-update-brief` | `run_reports` (this run's analytical artifacts), `bank_dir`, `constraints_ledger`, `output_path=<run>/bank_update_brief.md`, `run_id` | — | — |
| 24 | Ingest constraint proposals | `knowledge-bank-curator.maintain-constraints` | `constraints-ledger` | `report_paths` (every report of this run), `direct_proposals`, `constraints_ledger=<ledger>`, `bank_dir`, `run_id` | — | G12 |
| 25 | Close the manifest | `flow` | `run-manifest` | `<run>/run.md` | — | — |

### Parallel groups

| Group | Steps | Rule |
|---|---|---|
| **A** | 5 ∥ 6 | Both read the dossier and the source audit; neither reads the other's output. |
| **B** | 9 ∥ (each entry of 10) ∥ 11 | All three read the same draft revision. The fit score is informational and does not wait for the checks; the checks do not wait for it. |
| **C** | the per-entry executions inside 18, then each 19 | External entries are independent services; one entry's outcome never changes another's. |

A harness with subagents runs a group concurrently; a single-context harness runs the same steps in
table order. **The result must not differ.** Nothing inside a group may read another group member's
output — that is what makes the two execution modes equivalent.

### 0. Resolve this package's root, then load the engine's conventions

This file was presented from `<package root>/skills/generate-targeted-cv/`. The package root is two
levels above that directory; resolve it to an absolute path from the location the harness supplied
with this file. Then read `engine-conventions` — the invariants, the reference grammar, the anchor
rule, the loading rule and the rule about where a run writes — from the contracts directory at that
root, before doing anything else. If the location was not supplied, or the file cannot be read, do
not proceed: report which of the two happened, and ask.

Every public skill of this package carries that paragraph, and the duplication is deliberate: an
entry point cannot read the engine's conventions to learn how to find the engine's conventions, so
something has to anchor the scheme. The rule itself — where the base comes from, why the absolute
result is what gets read, what a refusal to read it means, and what to do when no base was supplied —
lives once, in `engine-conventions`, and this step never becomes a second copy of it. Do not tidy the
step away as a duplicate.

### 1. Resolve user context

Resolve, per contract `user-context`, in its order: the harness-native local agent rules file →
any other context or memory the harness provides → **ask the user**. The local rules file wins on
conflict. Nothing is defaulted from the repository layout and nothing is inferred.

What this flow needs resolved, and what it does with each value, is in *User-context settings* below.
Validate the result per the contract's preflight rules, and in particular:

- the validation set is well-formed — every entry has a name and a kind, and resolves to a skill that
  exists. A shipped `validate-cv-*` skill missing from the set is a **warning** to the user (adding a
  validator without recording it leaves it inactive), never a silent addition;
- every per-skill settings subsection names a skill that exists, and its keys are recognized by that
  skill's own `SKILL.md`. Unrecognized keys are reported, never interpreted here.

Nothing about the **bank** is decided here. Whether it exists, whether it is current, and whether it
carries the identity the export naming rule needs are all properties of the bank, and they are
settled together at step 2 — which is also where the remedy for all three lives.

Record in `run.md` `## User context`: which resolution supplied which values, and the resolved
snapshot — the `output_root` this run was given included, as contract `run-manifest` requires of that
snapshot. An empty registered validation set is legitimate and is recorded as such: the mandatory
truthfulness check still runs.

### 2. Check the bank is usable

Invoke `knowledge-bank-curator.check-freshness` with the resolved sources and the bank directory.
Record the verdict, the per-source and per-index statuses in `run.md` `## Bank freshness`.

| Verdict | What the flow does |
|---|---|
| `fresh` | Proceed to the `## Candidate` check below. |
| `stale` | **Stop this flow and run `refresh-knowledge-bank` first**, then resume from step 1 with the rebuilt bank. A bank that does not exist yet returns `stale`, so a first-ever run lands here — at the diagnosis, not at a downstream symptom. A CV built on a stale bank is a CV built on last month's truth, and nothing downstream can detect it. |
| `unknown` (a source could not be read) | Ask the user before proceeding. Proceeding is allowed if the user accepts the risk; the acceptance and its reason go into `run.md`, and the source audit's bank stanza carries it. |

Then confirm the bank carries a `## Candidate` section (contract `knowledge-bank`): *The export
naming rule* above needs the candidate's identity, and that section is its only admissible source.
**Absent ⇒ the same routing `stale` gets** — stop this flow, run `refresh-knowledge-bank` so the
curator derives the section, and resume from step 1. It is decided here because it is a property of
the bank, and the remedy for a bank that cannot serve this flow is stated once, in one place.

Two other cases are *not* a rebuild. A section recording conflicting spellings is a question for the
user (*The export naming rule*, *Escalation*). A section still absent after a refresh means the
curator could not derive an identity at all, which is also a question — never a second refresh.

The verdict is *produced* here and *transcribed* by the analyst into the source audit's
`## Bank stanza` at step 4 — the flow records it in `run.md`, the analyst copies it, and the curator
never writes into that file.

### 3. Scaffold the run, seed the manifest

Run `scripts/create_run.py` with values this flow resolved — the run directory, the run id, the flow
name and version, the resolved context snapshot, the step and gate names of the tables in this file,
the bank directory, the identity and the export name the naming rule produced, and (on a rerun) the
previous run's `position/` to copy. The script takes explicit command-line arguments and reads no
context, rules or contract file; `--help` documents every argument.

The seeded `run.md` is a `run-manifest` instance with `status: in-progress`,
`producer: flow:generate-targeted-cv`, one `## Steps` row per step of the table above at `pending`,
and one `## Gates` row per gate below at `not reached`. **The manifest is written as the run
proceeds** — a manifest reconstructed at the end cannot support resuming, blocking, or the gate reads
that step 18 depends on.

If the script cannot run (no interpreter), create the same layout and seed the same manifest by hand.
A missing script runtime never fails this flow.

**Rerun and the dossier.** A rerun for the same vacancy copies the previous run's `position/` into
the new run rather than pointing at it. The duplication is deliberate and is the price of run
isolation: a run may read only its own directory, the shared bank and the shared repository
definitions, so pointing at another run's dossier would make that other run an input. The script
automates the copy; new material is added to the **new** run's copy.

### 4. Audit the job-side inputs

`vacancy-analyst.audit-sources` inventories and classifies everything the run was given, marks the
conflicts, and writes the bank stanza from the freshness verdict recorded in `run.md`. **G3** is the
audit existing and reaching `status: complete`; a `blocked` audit (no readable job description)
stops the flow with a question.

### 5–6. Group A — the vacancy and the people around it

`analyze-job` produces the requirements profile; `extract-recruiter-signals` produces the signals.
Both may run concurrently. A run with no people-side input still produces `recruiter_signals.md`,
with `status: skipped` — a recorded absence, not a missing file, because later steps read it and
need to see that the recruiter component is absent rather than empty.

Optional enrichment (public company material, public profile context for named interviewers) that
has no bound capability is recorded inside the artifact as `SKIPPED` with instructions. It never
fails a step.

### 7. Retrieve evidence

`knowledge-bank-curator.query-bank` in **batch mode** over the requirements profile produces the
evidence map: one entry per requirement, cited, strength-labelled, constraint-flagged, `GAP` where
the bank has nothing.

**G4** is the map covering every requirement in the profile. A map missing rows is worse than a map
full of gaps: an absent row is indistinguishable from an oversight.

The map is deliberately **neutral** — it says what evidence exists, never where it should go. The
writer derives placement itself; see the writer's capability. Do not wait for usage hints that are
not coming.

### 8. Write the draft

`experience-writer.write-document`, pointed at contract `cv-document` as its format contract.
The evidence map is the **only** admissible source of facts.

**The writer's notes have a home.** `cv-document` declares `## Annex: writer notes`, so the
positioning choices, the intentional omissions, the header-title rationale, the tag candidates and
the writer's open issues are written **into `draft_cv.md`'s annex** and travel with the document.
The capability's fallback — hand the notes to the flow when the format contract declares no annex —
does not apply in this flow and must not be used as a reason to keep notes out of the artifact.

### 9–11. Group B — check the draft, and score it

Three independent readings of the same draft revision:

- **9, the mandatory truthfulness check.** `reviewer.fact-check` **always runs**. It is not part of
  the registered validation set, it cannot be deselected, disabled or skipped, and if it cannot run
  the flow is blocked rather than continued. Its report is the fixed artifact `<run>/fact_check.md`.
- **10, the registered internal checks.** For **each entry of the registered validation set of kind
  `internal`**, one `reviewer.run-check` invocation, executing that entry's own spec, writing to
  `<run>/checks/<validator>.md`. The flow passes the entry's spec path, its registered name, the
  inputs that spec declares, and the per-skill settings recorded for it. The flow neither knows nor
  cares what any entry checks: it resolves the set, computes the paths, and reads back verdicts. An
  entry whose required dependency is unbound is a recorded `skipped` report with instructions —
  never a failure, never a red gate.
- **11, the fit score.** `vacancy-analyst.score-fit` against the draft, with
  `candidate_data_format: cv-document` declared in the report header. **Informational**: it sets no
  status, opens no gate and blocks nothing. The escalation rule at step 13 is what reads it.

### 12. The edit loop

Any `validation-report` of group B with verdict `Fail`, or `Pass-after-edits` with required edits,
goes back to `experience-writer.edit-document` with those reports as `findings`. The writer applies
the smallest sufficient change; the reviewer never edits, and the writer never declares the result
validated.

**What re-runs, and how the flow knows.** `edit-document` returns a **disposition list**: every
finding and verdict with what was done about it, plus an account of what changed materially. This
flow records that list in `run.md` — in the `## Steps` notes of the edit step, alongside the bumped
`revision:` — and uses it to compute the re-check set:

| The edit changed | What re-runs |
|---|---|
| any content at all | `reviewer.fact-check` — in full, over the whole document, not only the changed lines |
| content an internal entry inspects | that entry's `run-check`, re-executing the **whole** spec |
| nothing (every item was `GAP_ONLY`, `REJECT` or not-for-the-writer) | nothing; the items are routed to the gap report at step 22 |

The disposition list is **routing state, not a result**: what changed and why is recorded in the
document's own annex, and the findings stay in the reviewer's reports. The manifest holds only which
checks the flow must re-open. Every re-check overwrites its report in place with `revision:`
incremented.

A finding that survives repeated edit cycles is reported to the user, not looped over silently.

### 13. Fit escalation

The fit report gates nothing — but a run that is not worth sending should not consume a render and
three external submissions before anyone notices. So this flow, and not the report, declares an
escalation rule:

> **Pause and ask the user whether to proceed** when the fit report's `## Should apply?` verdict is
> **`Maybe`** or **`Low ROI`**, or when its overall score is **below 60 % of the denominator the
> report states** (below 60 of 100, or below 57 of 95 when the recruiter component is `n/a`).

Asking means presenting the score, the verdict, the named risks and the strongest gaps, and waiting.
The answer — proceed, stop, or proceed after changing the target — is recorded in `run.md`
`## Open questions` with the reasoning. **G7** is the escalation being settled: either it did not
trigger, or the user answered.

The threshold is a flow convention for spending effort, not a judgement about the candidate and not
a quality bar. It never changes a report, never changes a status, and never becomes a reason to make
the CV claim more.

### 14–15. The final instance, and its checks

`edit-document` writes the cleared draft to `<run>/final_cv.md` with `status: final` and the caller
instruction *promote; apply the outstanding required edits and change nothing else*. The draft stays
where it is: two instances, one contract, both indexed in `run.md`.

Then the checks run **against the instance that will actually be rendered**: `reviewer.fact-check`
in full, plus the internal entries the disposition list implicates. The reports are overwritten with
`revision:` incremented, so that every report names the document that was rendered. **G8** is
`final_cv.md` existing at `status: final` with no unresolved required edit from any report.

### 16. Render the deliverable

`renderer.render-document`, executing the tool `render-cv-pdf` with the template resolved from that
tool's own settings subsection in user context (its default is the shipped bundle). The tool owns the
page target, the gate sequence, the template resolution and how an overflow is reported; what to do
about an overflow is the content-first fit policy of the document contract's family, not the tool's;
this flow owns the paths and the export name.

**The renderer may refuse, and that is correct.** It does not render a document that contradicts an
accompanying validation report, and it does not quietly prefer one over the other — it stops and
reports the conflict. This flow therefore never expects a silent preference, and never passes a
document whose reports it has not cleared:

- steps 14–15 must have closed G5 and G6 on **this** revision before step 16 starts;
- the `validation_reports` the flow passes are exactly the reports that cleared this revision —
  `fact_check.md` plus every `checks/<validator>.md`, at their current revisions;
- a refusal is **not** a render failure to retry. It means an artifact pair disagrees. Route it back:
  the writer resolves the document side, the reviewer re-checks, and only then does step 16 run
  again. Overriding the renderer, or re-passing the same pair, is a defect.

**Overflow is a content problem** (step 17). The tool reports what overflowed and by how much; the
writer compresses validated content gradually per its own capability; the template is never
restyled, and no content is silently cut. After any content change: step 15, then step 16, then step
16b again.

**G9** is every mechanical gate in `render/render_report.md` green — compile twice, page target,
text extraction in both modes, fonts embedded, export filename matching the naming rule. An unbound
toolchain is a **SKIPPED** render with instructions and the gates recorded as *not run*: it does not
fail this flow, but it does not open G10 either, because a gate that did not run was never green.

### 16b. Re-check the rendered form

Some checks can only be made against the file that will actually be sent. A registered internal entry
may declare rendered inputs — the deliverable and its two text extractions — and until a render
exists those items are reported *not applicable at this stage*, never as passes. A run that stopped
at step 16 would therefore ship a deliverable whose rendered form no internal check ever saw.

So: once G9 is green, **re-run every internal entry whose spec declares rendered inputs**, over the
same document plus the render. The flow prepares the two extractions into `<run>/work/` (plain
reading order and layout-preserving — the same two the render gate produced) and passes them with the
export path; each entry's report is overwritten in place at `<run>/checks/<validator>.md` with
`revision:` incremented, so the report names the artefact pair it actually examined.

- An entry whose spec declares **no** rendered inputs is not re-run here: nothing it inspects changed.
- Extraction unbound ⇒ the rendered half is **SKIPPED with instructions** per the entry's own spec,
  the markdown half stands, and the report is partial. It is not a failure and not a red gate.
- A finding here is an ordinary finding: back to step 17 — the writer edits, step 15 re-checks, step
  16 re-renders, and this step runs again. The template is never restyled to satisfy it.
- `reviewer.fact-check` is **not** re-run here. It examines claims, and rendering changes no claim;
  it re-runs when content changes, which is step 15's job.

**G6 stays open until this has happened** for every entry it applies to. G10 reads G6, so no external
submission precedes the rendered-form check.

### 18–20. External validation

Gated, hard: **G10 opens only when G5, G6 and G9 are all green.** No submission happens earlier —
not partially, not "just to see what it says".

`reviewer.run-external-checks` runs **each entry of the registered validation set of kind
`external`**, executing that entry's own spec: its environment preparation, its interaction policy,
its manual fallback. Entries run concurrently where the harness allows. The flow supplies the
deliverable at its export path and name, the final document, the job-side inputs the entry declares,
the run manifest, the raw-capture paths from the pattern above, and the gate names to assert —
**exactly as `run.md` records them** in the `## Gates` table, so an entry that reads gate statuses
from the manifest matches on the same strings this file declares.

An entry whose required dependency is unbound is **SKIPPED with instructions**. It never fails the
flow, never turns a gate red, and never produces a verdict about the document.

**Where the per-entry external outcomes go.** `run-external-checks` produces one run record for the
whole step, and this flow places it at **`<run>/external/run_record.md`** — its own artifact, a
`validation-report` instance, listing every external entry with its outcome (`executed` with the
capture paths, `SKIPPED` with the unblocking instructions and the manual procedure from its spec, or
`not completed` with what was attempted). It is not folded into `run.md`: the manifest points at
artifacts rather than replacing them, and a SKIPPED entry's instructions are a procedure a person
follows later — too much to live in a table cell, and too important to lose when the manifest is
rewritten. `run.md` carries the one-line outcome per entry and the pointer.

Then, per capture, `reviewer.normalize-external-report` writes the advisory report at
`<run>/external/<validator>_report.md` — form changed, meaning untouched, never a blocking verdict.
Finally `reviewer.gate-external-recommendations` judges every recommendation once, across services,
into `<run>/external/gate_decision.md`.

**G11** is the gate decision existing with a final recommendation and **no unresolved
`MANUAL_REVIEW`**. A `MANUAL_REVIEW` item is a question for the user, recorded in `run.md`
`## Open questions`; the run cannot be `complete` while one is open.

### 21. Applying accepted advice

Every `APPLY` / `APPLY_WITH_REWRITE` goes to `edit-document`, within the evidence and never beyond
it. `GAP_ONLY` and `REJECT` change no document and go to the gap report. `MANUAL_REVIEW` waits for
the user.

Any applied item re-opens the same loop as any other content change: `reviewer.fact-check`, the
internal entries the disposition list implicates, and a re-render. External advice never shortens
this path, however safe it looked.

### 22–24. Closing the run

- **22, the gap report.** `vacancy-analyst.gap-analysis` over the requirements, the evidence map, the
  final document and every finding of the run: genuine gaps, how the document handles them, honest
  interview follow-ups, the external `GAP_ONLY` items, and every rejected recommendation with its
  reason.
- **23, the bank update brief.** `knowledge-bank-curator.ingest-run-feedback` — a report only. It
  asks what would change the **bank**, never what to say in this application, and it writes nothing
  but the brief. It runs **last among the analytical steps**, after every validator and render check,
  because it reads their outcomes.
- **24, the ledger.** `knowledge-bank-curator.maintain-constraints` — the only writer of the ledger —
  ingests the `## Constraint proposals` of **every report this run produced**: source audit,
  requirements profile, recruiter signals, evidence map, every validation report (internal,
  the mandatory truthfulness check, and the normalized external ones), the external run record, the
  gate decision, the fit report, the render manifest, the gap report, the bank update brief, and the
  writer's annex in `final_cv.md`. `direct_proposals` carries what lives in no artifact: anything the
  user stated during the run, and proposals returned by a capability whose report was never written
  (a step that ended `blocked`).

  Conservative proposals are applied without asking; everything else becomes a recorded question.
  **G12** is the ingestion having run and its summary recorded — pending questions included. Nothing
  to ingest is a success.

Earlier steps of the same run honour proposals raised by earlier steps **before** this ingestion:
the flow carries them forward as `in_run_proposals` / `in_run_constraint_proposals`, and step 24
makes them durable.

### 25. Close the manifest

Fill `run.md`: final step statuses and revisions, gate states, the artifact index (every artifact
with its contract, status and revision, plus `<run>/render/`, `<run>/exports/` and `<run>/work/`
marked as intermediates and byproducts, and the ledger by its path outside the run), and the open
questions. Set `status: complete` only when the definition of done is met; otherwise `blocked` (a
decision is needed) or `fail`, with the reason.

A `complete` manifest with a red gate or an unresolved question is a defect.

## Gates

| Gate | Requires | Evidenced by |
|---|---|---|
| G1 context resolved | User context resolved through the declared order; the validation set well-formed; every per-skill settings subsection naming a skill that recognizes its keys. | `run.md` `## User context` |
| G2 bank usable | A freshness verdict with per-source and per-index status, **and** the bank's `## Candidate` section present for the naming rule. `stale` — which is what a bank that does not exist yet returns — or `## Candidate` absent ⇒ refresh first, then resume from step 1. `unknown` ⇒ settled with the user. An undecided verdict is a red gate. | `run.md` `## Bank freshness` |
| G3 sources audited | Every run input inventoried and classified; conflicts marked; the bank stanza written. | `<run>/source_audit.md` |
| G4 evidence retrieved | One evidence-map entry per requirement in the profile, cited and strength-labelled, gaps marked `GAP`. | `<run>/evidence_map.md` |
| G5 truthfulness | The mandatory `reviewer.fact-check` on the current revision of the document in play: `pass`, or `pass-after-edits` with every required edit applied and the check re-run. Never skipped, never waived. | `<run>/fact_check.md` |
| G6 registered internal checks | Every entry of the registered set of kind `internal`: `pass`, or `pass-after-edits` with its edits applied and the entry re-run, or a recorded `skipped` with instructions. **And, once a render exists, every entry whose spec declares rendered inputs re-run against it (step 16b)** — an entry still reporting its rendered items as *not applicable at this stage* does not close this gate. An empty set closes it trivially. | `<run>/checks/<validator>.md` |
| G7 fit escalation settled | The rule did not trigger, or the user answered and the answer is recorded. | `<run>/fit_report.md`, `run.md` `## Open questions` |
| G8 final document | `<run>/final_cv.md` exists at `status: final`, with no unresolved required edit from any report. | `<run>/final_cv.md` |
| G9 render gates | Every mechanical gate green in the render manifest: compile ×2, page target, extraction in both modes, fonts embedded, export filename matching the naming rule. Gates recorded *not run* are not green. | `<run>/render/render_report.md` |
| G10 external submission opened | G5, G6 and G9 all green at the time of submission. Missing or ambiguous statuses count as unknown, and unknown is never green. | `run.md` `## Gates`, `<run>/external/run_record.md` |
| G11 external advice judged | A gate decision with a final recommendation and no unresolved `MANUAL_REVIEW`; every applied item re-checked and re-rendered. | `<run>/external/gate_decision.md` |
| G12 ledger closed | `maintain-constraints` ran over every report of the run; its summary and any pending questions recorded. | `run.md`, `<bank-dir>/constraints.md` |

Gate names are recorded in `run.md` `## Gates` **exactly as this table names them**. Steps that read
gate statuses out of the manifest — an external entry's precheck, a resuming agent — match on those
strings.

## Definition of done

- Every gate green in `run.md`, or explicitly waived by the user with the reason recorded. G5 is
  never waivable.
- The deliverable exists at `<run>/exports/`, named per *The export naming rule*, and the render
  manifest's naming check says `match`.
- No unresolved `MANUAL_REVIEW` item and no unanswered escalation.
- The gap report and the bank update brief exist; the ledger ingestion ran and its questions are in
  `## Open questions`.
- `run.md` has `status: complete`, a full artifact index, and no unresolved question.

## Escalation

Stop and ask the user — recording the question in `run.md` `## Open questions` and setting
`status: blocked` — when:

- user context cannot be resolved, the validation set is malformed, or a per-skill setting is
  unrecognized by the skill it names;
- the bank's `## Candidate` section records conflicting spellings, or is still absent after a
  refresh, so the export name cannot be derived — a section that is merely absent is routed to
  `refresh-knowledge-bank` at step 2 rather than escalated;
- the freshness verdict is `unknown` and the affected source matters to this vacancy;
- no readable job description was provided, or the job-side inputs contradict each other on something
  load-bearing and neither source is more canonical;
- the fit escalation rule triggers (step 13);
- the same finding survives repeated edit cycles, or two required edits contradict each other;
- the renderer reports that the document contradicts an accompanying validation report, and the
  contradiction is not resolvable by an edit the findings already require;
- content cannot meet the page target without cutting something a finding requires to stay;
- an external gate decision carries a `MANUAL_REVIEW`, or its final recommendation is
  `Do not send`;
- the constraints ledger is unreadable or malformed — the run stops rather than starting a new one.

An unbound capability is **not** an escalation: it is a SKIPPED step with instructions, recorded in
`run.md`, and the flow continues.

## Usage

`setup-master.register-with-harness` makes this repository's skills discoverable by the harness in
use. **Where registration succeeded, the flow is invoked by name:**

> run `generate-targeted-cv` for `<run-id>`

**By-path invocation is valid wherever the user has these files at a path they can name** — which is
the case when this engine is cloned. Point the agent at this file, whose location the skills index
gives for the name `generate-targeted-cv`, and pass it the same `<run-id>`. Once this engine is
installed as a package, the public skills are invocable by name and that is the supported route: an
installed package sits at a location the user never chose and that moves whenever the package is
updated, so a path to it is not a thing to hand out.

An adapter is never authority. However the flow was reached, the executing agent reads this file, and
the loading rule in `engine-conventions` — with its role-side reasoning in `role-conventions` —
governs what
else a step's executor opens. This flow points at that rule rather than keeping its own copy: a rule
with several homes ages at different rates, and the copy an agent happens to read is the one it
obeys.

Before the first run:

1. the user's context must exist — if it does not, the correct outcome of preflight is a question,
   and the supported answer is `setup-master.bootstrap`;
2. the knowledge bank must exist and be usable — `refresh-knowledge-bank`;
3. the job dossier must exist at `<run>/position/` — created by `scripts/create_run.py` as stubs the
   user fills, or copied from the previous run of the same vacancy.

A typical invocation, in the user's own words:

```text
Run generate-targeted-cv for the vacancy in <path-to-job-material>.
Use my registered validation set.
```

Individual pieces can also be run on their own, without this flow: a tool invoked standalone defaults
to `outputs/<tool-name>/<run-id>/` with a minimal `run.md`, and a role invoked directly takes
explicit paths from the user. That is a different thing from resuming this flow — a run is
resumed by reading its `run.md`, not by re-running the steps that already have artifacts.

## User-context settings

**This skill recognizes no per-skill settings keys**, so this section carries no key table — the
shape `skill-conventions` prescribes for a skill with nothing to declare. A `### generate-targeted-cv`
subsection under `## Skill settings` in the user's local rules file has no meaning; report it as
unrecognized rather than interpreting it. Every setting this run needs belongs to the skill that owns
it — the render template to `render-cv-pdf`, a service's parameters to that validator's own
subsection.

The table below is **not** a key declaration. It indexes the sections of contract `user-context` this
flow reads, and what it does with each:

| Item | Contract section | Use |
|---|---|---|
| Canonical experience sources | `## Experience sources (canonical)` | Required. Passed to `check-freshness` at step 2 and to nothing else — this flow never reads a canonical source directly; the bank is its only view of the candidate. |
| The active validation set | `## Validation skills` | Required section, optionally empty. Entries of kind `internal` instantiate step 10 and the `checks/` pattern; entries of kind `external` instantiate steps 18–20 and the `external/` patterns. The mandatory truthfulness check is never in this list. |
| Per-skill settings | `## Skill settings` | Resolved and **passed through** to the skill each subsection names — the render tool's template, an external entry's service parameters. This flow validates that the owning skill recognizes the keys; it never interprets a value belonging to another skill. |
| Additional rules | `## Additional rules` | Optional free text, passed to the writer as `additional_rules` and honoured throughout, so long as it does not weaken truthfulness, run isolation, the sole-writer rule, or validation independence. |

## Dependencies

Direct needs of the flow itself. Everything the tools it invokes require — the typesetting
toolchain, text extraction, browser automation, a service's own runtime — is declared by those
skills and inherited transitively; `setup-master.check-environment` aggregates both.

| Name | Kind | Needed for | Required / optional | When unbound |
|---|---|---|---|---|
| File reading and writing within the paths this flow computes | capability | Creating the run directory, writing and updating `run.md` throughout the run, and reading the knowledge bank and the repository definitions the steps need. | required | Nothing can run. The flow reports `blocked` naming the path it could not reach; it never writes outside the paths it computed. |
| A question channel to the user | capability | Every escalation in this flow is a question, not a decision: unresolvable context, a `## Candidate` section a refresh could not supply, the fit escalation at step 13, a `MANUAL_REVIEW`, a source conflict. | required | The flow records the question in `run.md` `## Open questions`, sets `status: blocked`, and stops. It never answers its own question. |
| `python3` ≥ 3.10 | tool | Running this skill's `scripts/create_run.py` (step 3) and the curator's bundled freshness script (step 2). | optional | Create the layout and seed `run.md` by hand from the declarations above; compare source and index timestamps with the harness's own file tools. Note in `run.md` that both were done manually. A missing script runtime never fails this flow. |
| Concurrent step execution (subagents or an equivalent) | capability | Running the declared parallel groups A, B and C at the same time. | optional | The groups run sequentially in table order. The outcome is identical by construction — no group member reads another's output — so this only costs time. |
| Web search | capability | The optional company and market enrichment the job-side steps (4, 5) may request. | optional | The affected entry is recorded `SKIPPED` with instructions inside the artifact that wanted it; the analysis proceeds from the provided inputs alone. Recalled knowledge is never a substitute for a lookup that did not happen. |
| Professional-network profile lookup | capability | The optional people/team context for the recruiter-signals step (6) when the dossier names interviewers. | optional | The entry is recorded `SKIPPED` with instructions; positioning proceeds from the notes the run actually has. |

Concrete bindings for these live in the user's harness configuration, not here. Unbound entries are
aggregated and reported by `setup-master.check-environment`.
