# Skill conventions

The house rules for every skill package in this directory: the package layout, the frontmatter, the
required section set, the settings section, and the `## Dependencies` declaration format. This
document is the authority on what a declaration must **contain**; how a declaration is probed and
what counts as evidence belongs to `setup-master.check-environment`. The last two of those — the
settings section and the dependency format — are declared by **tool** packages as well, and are
stated here for both; `tool-conventions` owns everything else about a tool.

This is an ordinary document of the skills directory, listed in the index like any skill. Refer to it
by the name `skill-conventions`.

## What a skill is

A **skill** orchestrates several roles end to end. It owns the ordering, the gates and the run
layout; it never contains the rules of the roles it invokes.

This directory holds **only** skills, and it holds all of them. The packages that wrap one concrete
operation — the renderer, the validators — are **tools**, they live in the tools directory, and
`tool-conventions` governs them. The split is a fact about where a package sits rather than a
property an auditor has to check, which is what keeps it true: this directory is what a client scans
to learn what may be invoked, so anything that should not be invoked directly is simply not in it.

## Package layout

A skill package is a directory named for the skill, directly inside the skills directory, and it
travels as a unit:

```
<skill-name>/
├── SKILL.md                    # the skill itself
├── scripts/                    # optional; bundled scripts, explicit CLI arguments only
└── templates/                  # optional; bundles the skill resolves and fills
```

**One level, never two.** A client looks for a definition file in the *immediate* children of the
skills directory and is forbidden from searching deeper, so a package one level further down is not
found at all — and, because every skill then sits at the same depth, one relative form reaches the
package root from any of them.

Everything the package refers to inside itself is written relative to the package. Anything outside
it — a contract, a role, a `role.capability`, another skill — is referred to by name, never by path.

## Frontmatter, and the name rule

`SKILL.md` opens with YAML frontmatter carrying exactly two fields:

```yaml
---
name: <skill-name>
description: <one paragraph — what the skill does, for whom, and what it deliberately does not do>
---
```

**The package's directory name and the frontmatter `name` must be the same string.** This is a hard
rule. A harness may derive a skill's identity from either one, and a mismatch makes the skill
resolvable under one name and invisible under the other — usually silently. The same rule binds role
packages and tool packages.

## Required sections

Present in **every** skill:

| Section | Holds |
|---|---|
| an opening statement | what this skill is and is not. The heading wording is free. |
| `## Inputs` | every input the skill takes, as an index: name — what it is (a contract name where one applies) — required or optional. An index, never a second home for rules. |
| `## Steps` | the step table: step → executor → inputs → outputs. |
| `## Gates` | the named gates, whose names are used verbatim in the steps. |
| `## Definition of done` | what must be true before the run is finished. |
| `## Escalation` | what stops the flow and what it asks. |
| `## User-context settings` | the settings section, below. Present even when the skill recognizes no keys. |
| `## Dependencies` | the dependency declaration, below. It is the **last** section of the file. |

`## Outputs` and `## Runbook` are **not** in this set; they are a tool's required sections and
`tool-conventions` states them. A skill has no runbook of its own because it performs nothing
itself: every concrete operation it needs is a `role.capability` or a tool that its step table
names, and each of those states its own procedure.

Sections beyond the required set are free, and every shipped skill has several.

## The settings section

**This section and the `## Dependencies` section below are the two formats this document owns that
also bind tool packages.** They are stated once, here, because the things that read them do not care
which kind of package declared them: `setup-master.check-environment` aggregates every
`## Dependencies` section in this package, and contract `user-context` describes one settings shape
for the user's own file. Splitting either format across two authorities is how two authorities end
up disagreeing. `tool-conventions` names both rather than repeating them.

One name and one shape, so that a reader and an aggregating capability find the same thing in every
skill:

- the heading is exactly `## User-context settings`;
- the keys are declared in a table with exactly these columns, in this order:

  | Key | Required | Values | Default | Meaning |
  |---|---|---|---|---|

- `Required` is `required` or `optional`. `Values` states the accepted values or the value shape;
  `Default` states the value used when the key is absent, or `none` when there is none;
- a skill that recognizes **no** keys keeps the heading and states that in prose instead of a table;
- a key declared `required` with **no** default is also declared as a `setting` row in
  `## Dependencies`, so that its absence is noticed at setup rather than at preflight.

## The `## Dependencies` declaration

One table, one row per entry, with these fixed columns:

| Column | Meaning |
|---|---|
| `Name` | what is needed, named once and unambiguously |
| `Kind` | one of the four kinds below |
| `Needed for` | the task it serves |
| `Required / optional` | whether the owning step can proceed without it |
| `When unbound` | the declared behaviour, typically: the step runs SKIPPED/manual with instructions |

Every field is present in every row. A row that omits a field or contradicts itself is malformed, and
the capability that reads it reports it as malformed rather than repairing it by guessing.

The four kinds:

| Kind | What it declares | What the row must additionally state |
|---|---|---|
| `capability` | some tool able to perform a stated task, named abstractly ("browser automation", "text extraction") | nothing beyond the columns |
| `tool` | one concrete instrument the implementation genuinely requires, and **one checkable thing** — not a set | when it does not answer to `--version`, the argument it does answer to; when it is probed against a binding recorded in user context rather than against `PATH`, which binding |
| `component-set` | a requirement satisfied by a set of components that are not individually discoverable as executables | the **exact check** to run, as a command the skill itself authors, one per component |
| `setting` | a user-context settings key the skill declares required with no default | what the skill does when the key is not recorded |

Two rules that follow from `tool` meaning one checkable thing:

- a binary plus the package set it needs is **two** rows — a `tool` row for the binary and a
  `component-set` row for the packages, with the check the skill declares;
- a declared minimum version with no working probe is a documentation gap in this skill, not
  something the reading capability resolves by choosing a flag itself.

**No version pinning.** A skill declares what it must be able to do, not which release does it. A
genuine requirement — a specific engine because the shipped material uses that engine's primitives —
is not a pin, and the row says why it is genuine.

**Dependencies are declared once, by the package that needs them** — a skill or a tool, in its own
`## Dependencies` section. A skill declares only its *direct* dependencies and inherits the rest
from the tools and capabilities its steps invoke; `setup-master.check-environment` resolves that
transitively.

## Scripts

Skill-owned scripts live in the package's own `scripts/` directory and follow the same conventions as
role-owned scripts — explicit CLI arguments, no parsing of context or rule files, cross-platform, and
the two outcome conventions for reading a script's exit code. Those conventions are stated once, in
`role-conventions`, and they bind every bundled script in this package.

That is the same arrangement as the two sections above, seen from the other side: a directory's
conventions document may own a rule that binds packages in another directory, and here one does.
The test is not which directory the rule was written in but whether it has exactly one home.
