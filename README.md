# Truthful CV Tailor

A set of **toolchains for CV and job-search work**, driven by an AI agent: they turn your canonical
experience sources plus one vacancy's material into a truthful, ATS-friendly, target-specific CV —
rendered to PDF, checked at every step, with the gaps written down instead of papered over.

It ships **no personal data, no machine settings, and no idea of where your files are**. It defines
*what* the flows need; you connect it to your own environment once, and the connection lives in your
local rules file, outside version control. Where your results go is something **you tell it, with
each request** — nothing is ever written inside this package.

Three guarantees shape everything in here:

1. **Truth first.** Nothing is invented. Weak evidence is called weak, an unsupported requirement
   becomes a recorded gap, and machine-readability never outranks the truth.
2. **One source of candidate facts.** A knowledge bank, built from your canonical sources by a single
   role, is the only thing the CV flow reads about you — so every claim is traceable to a citation.
3. **Validation is independent and advisory.** The reviewer never edits the CV; external services
   never edit it either, and their scores are never treated as truth.

## Quickstart

**Three skills are the whole public surface.** Once this is installed, you invoke them by name:

```text
1. Connect it to your environment — once per project:
   run connect-environment

2. Build the knowledge bank from your experience sources:
   run refresh-knowledge-bank

3. Produce a CV for one vacancy:
   run generate-targeted-cv for <run-id>
```

Steps 2 and 3 need to know **where to write** before they start, and they will ask if you have not
said. That location is yours: it holds personal data, and it has to outlive any version of these
toolchains that reads it, so this package holds no default for it and never falls back on one. If
you **cloned** this repository rather than installing it, `outputs/` is the conventional answer — it
is already gitignored, and the examples below point at it. That is a convention for a clone, not a
default the flows apply.

Step 3 wants a job dossier — at minimum a job description — under the run's `position/` directory;
the flow's scaffolding script creates the stubs for you to fill. The result lands in
`<your output root>/generate-targeted-cv/<run-id>/`: the manifest `run.md` with every step and gate,
the analysis artifacts, the checked document, the rendered PDF under `exports/`, and the gap report.

**The first time a run opens these files, your harness will probably ask you to allow it.**
An installed package sits outside the project your session was started in, and reading outside that
location is normally permission-gated; approving it once is what makes the flows work. Setup checks
for this at its second step and reports it plainly, but it cannot grant the access itself — that is
your harness's own configuration or your own permission state, and nothing here edits either. A run
that is refused says which path it could not read and stops; it never works around it by copying a
rule inward.

**Roles and tools are internal.** The six roles and the four tools are registered with no harness and
appear in no menu: they are reached from a flow's step table, or by naming one with explicit paths if
you have these files at a path you can name. That is deliberate — a component reached only through a
flow has no business in a list where a request could land on it and skip the gates the flow holds.

**Invocation by path stays valid wherever you have these files at a path you can name**, which is the
case when you clone: point the agent at the skill's own file, and each directory's `INDEX.md` turns a
name into its location. Once this is installed as a package it sits somewhere you never chose and
that moves whenever it is updated, so by name is the supported route. What a *run* obeys — the
invariants, the reference grammar, how the package works out where it sits, what each step loads and
where a run writes — lives in [`contracts/engine-conventions.md`](contracts/engine-conventions.md),
which every public skill loads before doing anything else. [`AGENTS.md`](AGENTS.md) is its companion
for authors, and describes how this tree is *written*.

## Setup

**Setup is a skill with a role behind it.** `connect-environment` is the front door and holds the
ordering and the gates; the `setup-master` role holds every rule the pass applies. Run the skill by
name, or invoke the role directly with explicit paths — the way in is
[`roles/README.md`](roles/README.md). The role's capabilities:

| Capability | What it does |
|---|---|
| `bootstrap` | **Connecting a project, and bringing an already-connected one forward — the same pass.** Determines your harness and the local rules file it auto-loads (for Claude Code, `CLAUDE.local.md`), then creates or updates that file from the template in the `user-context` contract — your experience sources, the active validation set, per-package settings, and your own additional rules. It records **nothing about where the files of this package live**: it travels as one unit, so where each kind sits inside it is fixed and is not yours to choose or to keep in step. Then it checks the environment and **offers** the two capabilities below. |
| `prepare-environment` | Closes the gaps the check found — an interpreter, a browser build, a typesetting toolchain — by whatever means your machine actually offers, verifying each one and recording what it did. |
| `register-with-harness` | Makes this package's three public skills discoverable by your harness, generated from the packages themselves and never the other way round, so that invocation by name works. Installing the package is often what registers it, in which case this reconciles what is already there. Roles and tools are never registered. |
| `update-settings` | Revisit or change any recorded setting later. |
| `register-skill` | Activate a check — one of the validator **tools** shipped here, or a validator you keep in your own environment. **This is also the guide for adding a new validator.** |
| `check-environment` | Aggregate the `## Dependencies` of this package's public skills and internal tools, plus every check you registered wherever it lives, and report the dependency matrix: dependency → status → affected steps. It only ever reads. |

**Nothing changes your machine unless you agree to it, item by item.** Your local rules file is the
only thing setup writes on its own initiative; `prepare-environment` and `register-with-harness` are
the only things here that change anything beyond it, and each one tells you, before it runs, what
will exist afterwards, at exactly which path, by what means, how it will be checked, and how to undo
it. Declining an item is a normal outcome, not a broken setup: the
steps it affects are reported SKIPPED or manual with instructions, and nothing is retried by another
route behind your back. An agreement given in an earlier session does not carry into a new one, and
neither capability ever edits your harness's own configuration files — where that would be the only
way to register something, it says so and hands you the manual steps instead.

The local rules file is gitignored (`*.local.md`) and must never be committed: it holds real paths
and personal data.

### What the flows can use

Every capability below is checked at setup time and again at run time. The first three are what a
flow cannot proceed without, and an unbound one of those is reported plainly and stops the flow.
**Every other unbound capability is never a failure** — the step that needed it runs SKIPPED or
manual, with instructions, and the flow continues. Only the truthfulness check is unskippable.

| Capability | Used by | Typical binding | Required? |
|---|---|---|---|
| Read access to this package's own files | all three skills | your harness's file tools, plus whatever permission it needs to read outside the project the session started in | required — nothing runs without it, and it is the one thing setup cannot grant for you |
| A question channel to you | all three skills | the interactive session | required — every escalation is a question, never a decision |
| Read and write access under the output root you name | both CV flows | your harness's file tools, or a shell that can reach it | required — a run has nowhere to put its results otherwise |
| Read access to your canonical experience sources | `refresh-knowledge-bank` | the harness's own file tools, or a shell that can reach them | required — the bank cannot be built without it |
| A LaTeX-class typesetting toolchain | `render-cv-pdf` | `pdflatex` (pdfTeX) with the packages the shipped template names | required for the PDF — unbound, the typeset source is still written and the render is reported SKIPPED with manual instructions |
| PDF text extraction and inspection | `render-cv-pdf`, `validate-cv-ats` | Poppler/Xpdf `pdftotext`, `pdffonts`, `pdfinfo` | required for the render gates — unbound, each affected gate is recorded *not run* rather than passed |
| Browser automation | `validate-cv-enhancv` | a browser-driver package plus a browser build, in a session with a visible window | optional — external checks are advisory |
| A person with a browser | `validate-cv-resumly` | you, interactively | optional — the manual-mode external check |
| Web search | both CV flows | any search binding the harness offers | optional — company/market enrichment, and verifying inferred capability names |
| Professional-network profile lookup | `generate-targeted-cv` | any binding that reaches public profiles | optional — people/team context for recruiter signals |
| `python3` ≥ 3.10 | the bundled scripts | a local interpreter | optional — every script has a documented manual fallback |
| Concurrent step execution | `generate-targeted-cv` | subagents, where the harness has them | optional — the parallel groups then run sequentially, with an identical result |

The exact, authoritative list is each package's own `## Dependencies` section — a skill's or a
tool's; the table above is the overview. PDF is the only deliverable this repository produces.

**An unbound capability does not have to stay unbound.** `prepare-environment` will close the ones
your machine can be made to provide — with your agreement, and one verification each. The rest are
**structural**: no network, no visible desktop session, a shell that is not permitted to install.
Those stay recorded gaps with manual instructions, which is the honest outcome rather than a retry
loop, and the flow runs around them.

## How it fits together

- **Contracts** ([`contracts/`](contracts/README.md)) define the format and semantics of every
  artifact — and never its location. Paths are computed by the flow and passed to roles and tools as
  explicit parameters. One document there is not a contract at all: `engine-conventions`, the rules a
  *run* obeys, which every public skill loads first.
- **Skills** ([`skills/`](skills/README.md)) are the **public surface, and all of it** — three of
  them, one directory level deep. Each orchestrates roles end to end and owns the ordering and the
  gates; the two CV flows own their run layout as well.
- **Roles** ([`roles/`](roles/README.md)) are the actors: `setup-master`, `knowledge-bank-curator`,
  `vacancy-analyst`, `experience-writer`, `reviewer`, `renderer`. Each is a compact `ROLE.md` index
  card plus one file per capability. Roles never call each other — data flows only through artifacts
  — and none of them is registered with any harness.
- **Tools** ([`tools/`](tools/README.md)) wrap one concrete operation each: `render-cv-pdf` and the
  three `validate-cv-*` validators. Internal as well — reached from a flow's step table, from the
  reviewer executing one as a check spec, or by naming one with explicit paths.
- **Your output root** is not in this tree at all. `outputs/` is gitignored and is the conventional
  place to point a clone at; it is not a default, and no rule in this package names it.

Each of those four directories carries an `INDEX.md` — the name → location resolver, written from the
package root, and the fastest way to find the right contract, role, skill or tool — plus the house
rules that its own entries follow. Everything here travels as one unit and references nothing outside
it; inside it, a package refers to its own files by relative path and to everything else **by name**,
so a rename is a one-line change in one index.

## Repository map

```text
AGENTS.md                                    How this tree is WRITTEN; for authors. No run loads it
README.md                                    This file
contracts/README.md                          What a contract is; orientation, points at the index
contracts/INDEX.md                           Name -> file for every document in the directory
contracts/engine-conventions.md              How a RUN behaves; the first thing a public skill loads
contracts/artifact-conventions.md            Rules every contract inherits, incl. the common envelope
contracts/predecessor-map.md                 Archival: the deleted engine's rules -> their homes today
contracts/*.md                               One file per artifact contract
roles/README.md                              What a role is; orientation, points at the index
roles/INDEX.md                               Name -> location for every role and document here
roles/role-conventions.md                    House rules every role package follows
roles/<role>/ROLE.md                         Compact index card per role
roles/<role>/capabilities/<name>.md          Full rules of one capability
roles/<role>/scripts/*.py                    Role-owned helpers, explicit CLI arguments only
skills/README.md                             What a skill is; orientation, points at the index
skills/INDEX.md                              Name -> file for every skill and document here
skills/skill-conventions.md                  House rules every skill package follows
skills/<skill>/SKILL.md                      End-to-end flows; the public surface, one level deep
skills/<skill>/scripts/*.py                  Skill-owned helpers, explicit CLI arguments only
skills/BACKLOG.md                            Deferred work; entries have NO authority
tools/README.md                              What a tool is; orientation, points at the index
tools/INDEX.md                               Name -> file for every tool and document here
tools/tool-conventions.md                    House rules every tool package follows
tools/<tool>/TOOL.md                         Single-operation packages, incl. the validators; internal
tools/<tool>/scripts/*.py                    Tool-owned helpers, explicit CLI arguments only
tools/render-cv-pdf/templates/               Shipped CV template bundles (default: ats-onepage-latex)
outputs/                                     Gitignored; the conventional output root FOR A CLONE.
                                             Not a default: only .gitkeep is tracked, and no rule
                                             in this package names it
```

Point a run at any output root you like and it lays out the same two things under it: the knowledge
bank at `<output root>/knowledge-bank/`, and one directory per run at
`<output root>/<flow>/<run-id>/`.

## Privacy and git hygiene

This repository is safe to publish, and the strongest reason is structural: **nothing is written into
this package**, so your material is not in here to leak. It has no output root of its own, no cache,
no record and no scratch file — a run writes only under the root you gave it, which is somewhere
else.

Ignored by default, for the case where you point a clone at itself: everything under `outputs/` (the
knowledge bank, every run, every export), the harness-native local rules file (`*.local.md`), local
AI-assistant settings (`.claude/`, `.codex/`, `.cursor/`, `.continue/`, `.windsurf/`, …), virtual
environments, LaTeX byproducts, and rendered PDF/DOCX files.

The rule behind the list: **committed files carry rules and scripts, never personal data.** Real
paths, real names and real job material belong in your local rules file and under the output root you
named. Committed examples use placeholders.

## License

See [LICENSE](LICENSE).
