# Roles

A **role** is a specialized actor with a mission, an authority boundary, and a set of capabilities.
Roles are reusable across flows: the same role serves the CV flow, the bank refresh flow, and any
flow added later.

Each role lives in `roles/<role-name>/`:

```
roles/<role-name>/
├── ROLE.md                     # compact index card — see the template below
├── capabilities/<name>.md      # one file per capability: the full rules of that capability
└── scripts/                    # optional; role-owned scripts, explicit CLI arguments only
```

## Interaction model

- **Data flows only through file artifacts governed by contracts.** A role reads its inputs from
  paths it was given and writes its outputs to paths it was given.
- **Orchestration happens only through flow skills.** There are **no direct role-to-role calls**. A
  role never invokes another role; it produces an artifact, and the flow decides who reads it next.
- **All paths are mandatory role parameters.** A role card never assumes repository layout. The flow
  — or the user, when invoking a role directly — passes explicit input and output paths.
- **The same text runs on any harness.** A harness with subagents may run the flow's declared
  parallel groups concurrently; a single-context harness follows the same steps sequentially. The
  result must not differ.
- **The user may invoke a role directly**, passing explicit paths. That is the normal way to use
  `setup-master`.

## Progressive disclosure

`ROLE.md` is an **index card, never the rulebook**. It must stay small enough to load cheaply on
every step that touches the role.

The full definition of each capability lives in its own file, `capabilities/<capability>.md`:
procedure, detailed rules, inputs and outputs by contract, failure and skip conditions, and examples
where they earn their place.

Flow step tables reference `role.capability`. That name resolves to exactly one capability file, and
the executing agent loads **`ROLE.md` plus that one file — nothing else**.

Consequence, and it is a hard rule: **cross-capability material belongs in `ROLE.md`.** Invariants,
authority, and anything two capabilities both rely on live on the index card, so that no capability
file ever requires another capability file to be loaded to be correct.

## Role card template

Every `ROLE.md` follows this shape. YAML frontmatter carries `name` and `description` so that future
harness adapters can generate agent wrappers from it.

```markdown
---
name: <role-name>
description: <one line — what this role is for>
---

# Role: <Name> — <one-line mission>

## Mission
2–4 sentences. Model-agnostic and flow-agnostic: what this role is responsible for, and what it is
deliberately not responsible for.

## Parameters
The explicit paths and inputs the role MUST receive on invocation. No defaults derived from
repository layout.

## Authority
What the role owns and may write. Everything else is read-only.

## Consumes / Produces
Contract names only — placement is decided by the calling flow.

## Capabilities
INDEX ONLY. One line per capability: purpose, inputs → outputs, and a link to
`capabilities/<name>.md` holding the full rules.

## Tool requirements
ABSTRACT capability needs only — "browser automation", "LaTeX + poppler toolchain", "web search
(optional)". Concrete tool names never appear here; they appear only in skill `## Dependencies`
sections.

## Invariants
Pointers to the repository-wide invariants, plus the hard rules specific to this role.

## Escalation
When to stop and ask the user instead of deciding.
```

## Capability file template

```markdown
# Capability: <role>.<capability>

## Purpose
One paragraph: what this capability produces and why.

## Inputs
Each input as: parameter name — contract (or description) — required/optional.

## Outputs
Each output as: parameter name — contract — status values it may set.

## Procedure
The ordered steps. Written so that an agent holding only ROLE.md and this file can execute it.

## Rules
The detailed rules of this operation, including how it upholds the role's invariants.

## Failure and skip conditions
What makes this capability stop, what it reports instead, and what it hands back to the flow. An
unavailable optional capability is reported as SKIPPED with instructions — it does not fail a flow.
```

## Tool abstraction

Roles declare **abstract capability needs** only. Concrete bindings — which browser driver, which
LaTeX distribution, which service reaches a professional network — live in skills (each `SKILL.md`'s
`## Dependencies` section and runbook) and in the user's harness configuration.

Roles therefore do **not** carry a `## Dependencies` section; that section is a skill construct,
aggregated at setup time by `setup-master.check-environment`.

Availability is checked at setup time and again at run time. A step whose capability is not bound is
marked SKIPPED or manual, with instructions — it does not fail the flow.

## Scripts

Role-owned scripts live in `roles/<role-name>/scripts/`. They take **explicit CLI arguments**: the
agent resolves values (from user context, from artifacts) and passes them in. Scripts never parse
context files, rule files, or contracts themselves.

Scripts are cross-platform: `pathlib` for paths, `shutil.which` for binary discovery, no hardcoded
tool paths, no OS-specific assumptions.

### Reading a script's outcome

This applies to **every bundled script**, role-owned and skill-owned alike, and it exists because the
scripts do not all answer in the same way.

- **The printed report is always authoritative.** Every script writes its findings to stdout or to
  the path it was given; that text is what the calling agent reads and what goes into the artifact.
  No script is a verdict — a script measures, and the role decides.
- **The exit code carries at most a summary, and never more than the report.** Two conventions are in
  use, both deliberate:
  - *outcome in the report only* — the exit code distinguishes "the script ran" from "the script
    could not run" and nothing else. `roles/setup-master/scripts/check_environment.py` (`0` for any
    valid invocation, a missing tool being a reported status rather than a failure),
    `skills/tools/validate-cv-enhancv/scripts/run_enhancv.py` (the outcome is the printed
    `completed` / `not-completed` / `blocked` / `skipped` line), and
    `skills/tools/validate-cv-ats/scripts/{ats_static_check,keyword_match}.py` (`0` produced a
    report, `2` could not read an input or write an output);
  - *outcome also in the exit code* — a gate-shaped script additionally encodes its verdict, so a
    caller that only checks the status can still branch.
    `roles/knowledge-bank-curator/scripts/check_sources_freshness.py` (`0` fresh, `1`
    refresh-required, `3` unknown) and `skills/tools/render-cv-pdf/scripts/pdf_text_check.py` (`0`
    pass, `1` fail, `2` usage error, `3` skipped, `4` error).
- **Never assume which convention a script follows.** The list above is the summary; the scripts that
  encode a verdict also state their codes in their module docstring and in `--help`. A non-zero exit
  is never by itself a reason to fail a step — read the report, then apply the owning skill's or
  capability's failure-and-skip rules. A script added later declares its convention the same way.

## The role set

| Role | Directory | Mission in one line |
|---|---|---|
| setup-master | `roles/setup-master/` | Connects the toolchains to the user's environment; prepares, never executes flows. |
| knowledge-bank-curator | `roles/knowledge-bank-curator/` | Builds and maintains the knowledge bank; the sole writer of the bank and the constraints ledger. |
| vacancy-analyst | `roles/vacancy-analyst/` | Everything about the vacancy and the candidate-to-vacancy fit. |
| experience-writer | `roles/experience-writer/` | Writes and revises candidate documents from evidence. |
| reviewer | `roles/reviewer/` | Independent QA; never edits the document under review. |
| renderer | `roles/renderer/` | Template-driven production of the final file. |

A meeting **transcriber** role is planned but not built; only its output contract (`transcript`)
exists today. See `skills/BACKLOG.md`.
