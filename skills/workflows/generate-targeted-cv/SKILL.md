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

Do not run it while the bank is stale. Step 2 checks; a stale verdict routes to
`skills/workflows/refresh-knowledge-bank/SKILL.md` first, and this flow resumes afterwards.

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

- **`## Candidate` is absent** (a bank imported before the section existed): ask the user for the
  name, or run `refresh-knowledge-bank` so the curator derives it. Record the answer in `run.md`.
- **`## Candidate` records two spellings** with the conflict marked: ask which to use. The flow never
  picks one.
- **The rule yields a name the filesystem cannot hold**: report it and ask. Do not silently
  substitute characters.

The resolved name is passed on as a value, three times: to the render tool as `export_name` (its
gate 5 checks the produced filename against it), to any external entry whose spec declares a
naming-pattern parameter (so the entry enforces *this* rule rather than nothing), and into `run.md`
so the user can find the file by name.

