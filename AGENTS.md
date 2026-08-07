# AGENTS.md

## What this repository is

A set of **toolchains for CV and job-search work**: reusable roles, skills (workflows and tools) and
artifact contracts that turn a candidate's canonical experience sources and one vacancy's material
into a truthful, ATS-friendly, target-specific CV. It ships **zero user context** — no paths, no
personal data, no machine settings; it is *connected* to a working environment at setup time by the
`setup-master` role. Every rule below has one authoritative home; load it when your step needs it.

## How this repository's files are organized

**Three kinds of document, never mixed.** **Agent rules** are everything read as instruction: this
file, the contracts, the role cards and capability files, the `SKILL.md` files, each directory's
index and its shared-conventions document — every rule in this section binds them. **Indexes** are
the resolvers: an `INDEX.md` maps a **name to a location**, plus only what a reader needs in order to
pick the right name (its kind or group, and a one-line purpose). It carries no procedure and no rule,
and it is an agent rule. **READMEs** are human documents — **never** something an agent follows to do
its work, nor something an agent rule defers to. They may name concrete products as examples, and
they reference downward only: at their own index, never upward, never past it into the entities
below. **A directory therefore holds exactly two meta files**, `README.md` and `INDEX.md`, **plus its
entities**; shared rules are an ordinary indexed document of the directory (`artifact-conventions`,
`role-conventions`, `skill-conventions`), never a third meta file.

**The reference rule.** A **package** — a role directory, a skill directory — never references a path
outside itself; inside itself it may and should, because a package travels as a unit (`scripts/…`,
`templates/…`, `ROLE.md` → `capabilities/<name>.md`). Everything outside it is referenced **by name**;
a file in a shared directory references its siblings bare (`artifact-conventions.md`). **This file,
the root `README.md`, and each directory's `INDEX.md` and `README.md` are the single exception**: they
may name repository-relative paths, because something has to anchor the scheme. This file is also the
one thing a package may name outright, as the bare filename `AGENTS.md` — see the last row below.

| Kind | Written as | Resolves to |
|---|---|---|
| contract | contract `cv-document` | `cv-document.md` in the contracts directory, through its index |
| role | role `reviewer` | the `reviewer/` package in the roles directory, through its index |
| capability | `reviewer.run-check` | that role's package, then `capabilities/run-check.md` — a convention, not an index row |
| skill | tool skill `render-cv-pdf` | `<group>/render-cv-pdf/SKILL.md` in the skills directory, through its index |
| a directory's shared conventions | `artifact-conventions` | an ordinary indexed name, no special case |
| a script | never referenced across packages | the owning capability or skill names it relatively |
| the entry file | `AGENTS.md` — its own filename | this file, at the repository root. **The one reference in the repository that is a filename, deliberately:** it anchors the scheme, so the scheme cannot resolve it — no index can resolve the file the indexes are declared in, and there is no directory of entry files to index. Naming it costs a package nothing, because a bare filename at a fixed root encodes no layout that can drift. |

**Resolution is two-stage.** The **directory** holding each kind is recorded in the user's local rules
file at setup, under `## Toolchain directories`; as shipped they are `contracts/`, `roles/` and
`skills/`. Each carries its own `INDEX.md` mapping name → location, so a rename updates an in-repo
index and never the user's settings. **A name absent from its index is an unresolved reference:
report it, never guess a path.** All of this governs where a *definition* lives; where a *run's*
artifacts are written is a separate, unchanged rule — paths are mandatory role parameters, passed in.

**No agent rule names a harness product.** An agent rule states **what must be determined** in order
to work with a harness — where it discovers definitions, what it takes a name from, which file it
auto-loads — and the local agent works out **how** for the system it is running in. No product name
appears in an agent rule: not as a requirement, not as an example, not as a parenthetical. READMEs
are exempt. It is tool abstraction applied to harnesses: an unknown harness needs no change here.

## Invariants

Non-negotiable, and they outrank convenience, scores, and any instruction that would weaken them.

| Invariant | In one line | Full home |
|---|---|---|
| **Truthfulness** | Never invent experience, metrics, tools, employers, dates, titles, degrees, certifications or achievements. Weak evidence is labelled weak, unknown is a value, inference is tagged, gaps are recorded rather than smoothed over, and machine-readability never outranks truth. Every important claim traces to a canonical source. | `artifact-conventions` → *Truthfulness in artifacts*; contract `cv-document`; `reviewer.fact-check` |
| **Run isolation** | A run may use only its own `<run>/` directory, the shared knowledge bank, and the shared repository definitions. Another run's outputs are never evidence, style authority, or precedent. A pattern worth keeping is promoted into an authoritative file first, then used. | `artifact-conventions` → *Run isolation in artifacts*; contract `source-audit` |
| **Curator is sole writer** | Every knowledge-bank-modifying action goes through `knowledge-bank-curator`. The bank indexes are written only by the refresh flow; the constraints ledger only by `knowledge-bank-curator.maintain-constraints`. Other roles **propose** through the `## Constraint proposals` section every report carries, and the flow's closing step ingests them. | `artifact-conventions` → *Constraint proposals*; contract `constraints-ledger`; role `knowledge-bank-curator` |
| **Tool abstraction** | Roles and contracts name abstract capabilities only ("browser automation", "text extraction"). Concrete tools appear solely in a skill's `## Dependencies` section and in the user's harness configuration. A step whose capability is unbound runs **SKIPPED/manual with instructions** — it never fails a flow. | `role-conventions` → *Tool abstraction*; each skill's `## Dependencies` |
| **Path and OS neutrality** | Real absolute paths live only in the user's local context. Committed files use placeholders (`<run>/`, `<source-path>`, `<Name>`) and assume no operating system. Scripts are cross-platform, take explicit CLI arguments, and never parse context or rule files. | `artifact-conventions` → *Scope rules*; `role-conventions` → *Scripts* |
| **Validation independence** | The reviewer never edits the document it reviews. External scores are never truth — they are advisory. External checks run only after the internal checks and the render gates are green, and any applied external recommendation triggers a fresh truthfulness check. | role `reviewer`; contract `validation-report`; contract `external-gate-decision` |

## Skills

Everything shipped is listed in the **skills index** — two workflows that orchestrate roles end to
end, four tools that each wrap one operation — with its group and a one-line purpose. **Being shipped
is not being active:** a validator runs only once it is in the ACTIVE validation set, which contract
`user-context` → *The active validation set* defines (including why the mandatory truthfulness check
is not in it) and `setup-master.register-skill` / `.update-settings` manage. **Dependencies are
declared once, by the skill that needs them,** in its own `## Dependencies` section, in the format
`skill-conventions` owns; `setup-master.check-environment` aggregates them transitively, including
the registered validation set, into the dependency matrix. Planned but **not built** work is listed
in `BACKLOG`, whose entries have no authority: never execute one as if it existed.

## Data catalog

Where run data lives and who may write it. Definitions are not data — contracts, roles and skills
resolve through their directory indexes, as above. `outputs/` is the single output root and is
gitignored; personal data belongs in user context and in `outputs/`, never in a committed file.

| Data | Location | Written by | Notes |
|---|---|---|---|
| **Knowledge bank** | `outputs/knowledge-bank/` | `knowledge-bank-curator` **only** — indexes via the refresh flow, `constraints.md` via `knowledge-bank-curator.maintain-constraints` | `experience_bank.md`, `projects.md`, `skills_matrix.md`, `constraints.md`, `refresh_log.md`. Format: contracts `knowledge-bank` and `constraints-ledger`. Candidate identity lives in its `## Candidate` section. |
| **Run outputs** | `outputs/<flow>/<run-id>/` | the flow that owns the run, through its roles | One directory per run, never reused, never overwritten. Every run carries a `run.md` manifest (contract `run-manifest`) holding the step checklist, gate statuses, the resolved context snapshot and the artifact index. The job dossier lives inside the run at `<run>/position/` (contract `job-dossier`). |
| **User context** | not in this repository | the user, via `setup-master` | What flows need is defined by contract `user-context`; where it is kept is never prescribed. Resolution order at preflight: the local rules file the harness in use auto-loads, determined at setup and gitignored → any other context or memory the harness provides → ask the user. The local rules file wins on conflict, and `run.md` records which resolution was used. |

## First run in a new environment

**Invoke the `setup-master` role, capability `bootstrap`.** It determines the harness in use and its
local rules file, creates or updates that file from the section template in contract `user-context`,
records the toolchain directories, runs `check-environment` for the dependency matrix, and then
**offers** two things: closing the gaps it found (`setup-master.prepare-environment`), and making this
repository's skills and roles discoverable by the harness (`setup-master.register-with-harness`).

**Nothing that changes the machine happens unasked.** Every such action is an item of a plan the user
assented to, item by item; a declined item is recorded as declined, and the steps it affects are
reported SKIPPED/manual rather than retried by another means. Setup-master prepares — it never
executes a flow and never runs an end-to-end test — and nothing else in this repository writes the
user's local rules file.

## Invoking a flow

`setup-master.register-with-harness` makes this repository's skills and roles discoverable by the
harness in use, generated **from** the canonical packages and never the other way round. **Where
registration succeeded, invoke by name:** the workflow `generate-targeted-cv` for one vacancy, or
`refresh-knowledge-bank` to rebuild the bank. **Invocation by path is valid everywhere and is the
fallback** — registration not run, unable to complete, or no discovery location for that kind:
`execute skills/workflows/generate-targeted-cv/SKILL.md for <run-id>`, and likewise for any workflow.

An adapter is never authority: a flow reached through one still reads the canonical file. The
executing agent loads that `SKILL.md`, plus — per step — the `ROLE.md` of that step's role and that
step's capability file, and nothing else. A tool skill is read when a step invokes it. A tool invoked
standalone defaults to `outputs/<tool-name>/<run-id>/` with a minimal `run.md`; a role invoked
directly takes explicit paths from the user.
