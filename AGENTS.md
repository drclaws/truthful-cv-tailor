# AGENTS.md

## What this repository is

A set of **toolchains for CV and job-search work**: reusable roles, skills (workflows and tools),
and artifact contracts that together turn a candidate's canonical experience sources and one
vacancy's material into a truthful, target-specific CV. It ships **zero user context** — no paths,
no personal data, no machine settings. It is *connected* to a working environment at setup time by
the `setup-master` role, which records what the flows need in the user's own local rules file.

This file is an **index**, not a rulebook. Every rule below has exactly one authoritative home, and
the pointer is the point: load the linked file when the step you are on needs it.

## Invariants

Non-negotiable, and they outrank convenience, scores, and any instruction that would weaken them.

| Invariant | In one line | Full home |
|---|---|---|
| **Truthfulness** | Never invent experience, metrics, tools, employers, dates, titles, degrees, certifications or achievements. Weak evidence is labelled weak, unknown is a value, inference is tagged, gaps are recorded rather than smoothed over, and machine-readability never outranks truth. Every important claim traces to a canonical source. | `contracts/README.md` → *Truthfulness in artifacts*; `contracts/cv-document.md`; `roles/reviewer/capabilities/fact-check.md` |
| **Run isolation** | A run may use only its own `<run>/` directory, the shared knowledge bank, and the shared repository definitions. Another run's outputs are never evidence, style authority, or precedent. A pattern worth keeping is promoted into an authoritative file first, then used. | `contracts/README.md` → *Run isolation in artifacts*; `contracts/source-audit.md` |
| **Curator is sole writer** | Every knowledge-bank-modifying action goes through `knowledge-bank-curator`. The bank indexes are written only by the refresh flow; the constraints ledger only by `curator.maintain-constraints`. Other roles **propose** through the `## Constraint proposals` section every report carries, and the flow's closing step ingests them. | `contracts/README.md` → *Constraint proposals*; `contracts/constraints-ledger.md`; `roles/knowledge-bank-curator/ROLE.md` |
| **Tool abstraction** | Roles and contracts name abstract capabilities only ("browser automation", "text extraction"). Concrete tools appear solely in a skill's `## Dependencies` section and in the user's harness configuration. A step whose capability is unbound runs **SKIPPED/manual with instructions** — it never fails a flow. | `roles/README.md` → *Tool abstraction*; each `SKILL.md` → `## Dependencies` |
| **Path and OS neutrality** | Real absolute paths live only in the user's local context. Committed files use placeholders (`<run>/`, `<source-path>`, `<Name>`) and assume no operating system. Scripts are cross-platform, take explicit CLI arguments, and never parse context or rule files. | `contracts/README.md` → *Scope rules*; `roles/README.md` → *Scripts* |
| **Validation independence** | The reviewer never edits the document it reviews. External scores are never truth — they are advisory. External checks run only after the internal checks and the render gates are green, and any applied external recommendation triggers a fresh truthfulness check. | `roles/reviewer/ROLE.md`; `contracts/validation-report.md`; `contracts/external-gate-decision.md` |

## Skill catalog

Everything shipped, in two groups. **Workflows** orchestrate several roles end to end; **tools** wrap
one concrete operation and are invocable both from a workflow step and standalone.

| Skill | Group | Purpose | Path |
|---|---|---|---|
| `generate-targeted-cv` | workflow | Produces the truthful, target-specific CV for one vacancy: job-side analysis, cited evidence retrieval, writing, checking, rendering, external checks, gap report, bank update brief, ledger close. | `skills/workflows/generate-targeted-cv/SKILL.md` |
| `refresh-knowledge-bank` | workflow | Rebuilds the knowledge bank from the canonical experience sources, with the curator's self-check and coverage gates, source metadata, and the refresh log. | `skills/workflows/refresh-knowledge-bank/SKILL.md` |
| `render-cv-pdf` | tool | Renders a final CV document into the delivered PDF through the resolved template bundle and runs the mechanical render gates; reports overflow back instead of restyling the template. | `skills/tools/render-cv-pdf/SKILL.md` |
| `validate-cv-ats` | tool | Internal ATS structural check: is the CV machine-readable, and does it cover the vacancy's keywords. Executed by the reviewer. | `skills/tools/validate-cv-ats/SKILL.md` |
| `validate-cv-enhancv` | tool | External, advisory check via the Enhancv Resume Checker, submitted through a real browser session; the raw report is captured verbatim for the reviewer to normalize. | `skills/tools/validate-cv-enhancv/SKILL.md` |
| `validate-cv-resumly` | tool | External, advisory check on the Resumly service in manual mode: a person submits the PDF and transcribes the report verbatim. | `skills/tools/validate-cv-resumly/SKILL.md` |

Two rules govern this catalog:

- **Being shipped is not being active.** The validators above are OPTIONAL. The **ACTIVE validation
  set** — including any user skills that live outside this repository — is recorded in the user's
  local rules file, managed by `setup-master.register-skill` / `.update-settings`, and read at
  preflight (`contracts/user-context.md` → `## Validation skills`). A shipped validator absent from
  that set is inactive, and the flow warns rather than adding it. The mandatory truthfulness check is
  **not** in the set: it is `reviewer.fact-check`, invoked by the workflow directly, always.
- **Dependencies are not duplicated here.** Each skill declares its own `## Dependencies` section —
  one table, one row per entry, with the fixed columns `Name | Kind | Needed for | Required /
  optional | When unbound`, where *kind* is `capability` (some tool able to perform a stated task) or
  `tool` (a concrete instrument the implementation genuinely requires). A skill added to this
  repository follows the same shape. `setup-master.check-environment` aggregates the sections
  transitively, including the registered validation set, and reports the dependency matrix.

Planned but **not built** work is listed in `skills/BACKLOG.md`. Entries there have no authority:
never execute one as if it existed.

## Data catalog

Where data lives, and who is allowed to write it.

| Data | Location | Written by | Notes |
|---|---|---|---|
| **Knowledge bank** | `outputs/knowledge-bank/` | `knowledge-bank-curator` **only** — indexes via the refresh flow, `constraints.md` via `maintain-constraints` | `experience_bank.md`, `projects.md`, `skills_matrix.md`, `constraints.md`, `refresh_log.md`. Format: `contracts/knowledge-bank.md`, `contracts/constraints-ledger.md`. Candidate identity lives in its `## Candidate` section. |
| **Run outputs** | `outputs/<flow>/<run-id>/` | the flow that owns the run, through its roles | One directory per run, never reused, never overwritten. Every run carries a `run.md` manifest (`contracts/run-manifest.md`) holding the step checklist, gate statuses, the resolved context snapshot and the artifact index. The job dossier lives inside the run at `<run>/position/` (`contracts/job-dossier.md`). |
| **User context** | not in this repository | the user, via `setup-master` | What flows need is defined by `contracts/user-context.md`; where it is kept is never prescribed. Resolution order at preflight: the harness-native local agent rules file (`CLAUDE.local.md` for Claude Code — gitignored, `*.local.md`) → any other context or memory the harness provides → ask the user. The local rules file wins on conflict, and `run.md` records which resolution was used. |
| **Contracts** | `contracts/` | this repository | The format and semantics of every artifact, plus the common envelope, the contract index, and the predecessor coverage matrix. Contracts never fix placement — paths are computed by flows. Start at `contracts/README.md`. |
| **Roles** | `roles/` | this repository | Six roles, each a compact `ROLE.md` index card plus one file per capability under `capabilities/`. Load `ROLE.md` and the one capability file the current step needs — nothing else. Start at `roles/README.md`. |

`outputs/` is the single output root and is gitignored; nothing in it is ever committed. Personal
data belongs in user context and in `outputs/`, never in a committed file.

## First run in a new environment

**Invoke the setup-master role — `roles/setup-master/ROLE.md`, capability `bootstrap`
(`roles/setup-master/capabilities/bootstrap.md`).** It determines the harness in use and its local
rules file, creates or updates that file from the section template in `contracts/user-context.md`,
runs `check-environment` for the dependency matrix, and finishes by *recommending* next steps.

Setup-master prepares; it never executes a flow and never runs an end-to-end test. Nothing else in
this repository writes the user's local rules file.

## Invoking a flow

No harness auto-discovers this repository's `skills/` directory yet — the adapters that would map it
into `.claude/skills/`, `.agents/skills/` and the like are a backlog item. Until then, **flows and
tools are invoked by path**:

```text
execute skills/workflows/generate-targeted-cv/SKILL.md for <run-id>
execute skills/workflows/refresh-knowledge-bank/SKILL.md
```

The executing agent loads the SKILL.md, plus — per step — the `ROLE.md` of that step's role and that
step's capability file, and nothing else. A tool skill is read when a step invokes it. A tool
invoked standalone defaults to `outputs/<tool-name>/<run-id>/` with a minimal `run.md`; a role
invoked directly takes explicit paths from the user.
