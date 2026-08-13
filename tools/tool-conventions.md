# Tool conventions

The house rules for every tool package in this directory: the package layout, the frontmatter, the
required section set, and the three rules that decide what a tool may be. Two formats a tool
declares are owned elsewhere and are **named** here rather than repeated, because a rule copied into
a second file is a rule that can drift.

This is an ordinary document of the tools directory, listed in the index like any tool. Refer to it
by the name `tool-conventions`.

A **tool** wraps one concrete operation — render this document, run this check — and ships what that
operation needs. It is a sibling of a role package and of a skill package, not a variety of either: a
role is an actor with a mission and an authority boundary, a skill is a procedure a user may invoke,
and a tool is neither. Keeping it its own kind is what lets the tool own the *operation* while the
role owns the *actor's invariants*, so that neither has to restate the other.

## Package layout

A tool package is a directory named for the tool, and it travels as a unit:

```
<tool-name>/
├── TOOL.md                     # the tool's spec
├── scripts/                    # optional; bundled scripts, explicit CLI arguments only
└── templates/                  # optional; bundles the tool resolves and fills
```

Everything the package refers to inside itself is written relative to the package. Anything outside
it — a contract, a role, a `role.capability`, a skill, another tool — is referred to by name, never
by path.

**A tool that is invoked directly is presented from `<package root>/tools/<tool-name>/`, and the
package root is two levels above that directory.** The same arithmetic every public skill does is
stated here because a user naming a tool directly lands on its `TOOL.md` first, with nothing having
resolved the root on its behalf. The rule itself — where that base comes from, why the absolute
result is what gets read, and what to do when the base is not supplied — is in `engine-conventions`,
and this line does not replace it.

## Frontmatter, and the name rule

`TOOL.md` opens with YAML frontmatter carrying exactly two fields:

```yaml
---
name: <tool-name>
description: <one paragraph — what the tool does, for whom, and what it deliberately does not do>
---
```

**The package's directory name and the frontmatter `name` must be the same string.** This is a hard
rule, and it is worth being explicit about why it survives here, where nothing discovers a tool: the
name is the identity a workflow's step table, a registered validation-set entry and a report all use,
so a mismatch makes the package resolvable under one name and invisible under the other — usually
silently. A machine-readable name is what makes that checkable instead of noticed later. The same
rule binds skill packages and role packages, and a role is not a skill either, so frontmatter is not
what makes something a skill.

## Required sections

Present in **every** tool:

| Section | Holds |
|---|---|
| an opening statement | what this tool is and is not. The heading wording is free. |
| `## Inputs` | every input the tool takes, as an index: name — what it is (a contract name where one applies) — required or optional. An index, never a second home for rules. |
| `## Outputs` | each output as: name — contract or description — the status values it may set. |
| `## Runbook` | how the operation is actually performed. |
| `## User-context settings` | the settings section. Present even when the tool recognizes no keys. |
| `## Dependencies` | the dependency declaration. It is the **last** section of the file. |

Sections beyond the required set are free, and every shipped tool has several.

## The three rules that keep a tool a tool

### A tool never names a calling workflow or a calling step

Naming a caller would couple the tool to a flow, which the interaction model forbids, and it would
cost two things that are relied on elsewhere. The tool stops being invocable on its own, because part
of its meaning would then live in a file it does not ship with. And the dependency-to-step mapping
that `setup-master.check-environment` builds — which steps stop working when this binding is missing
— is derived **downward from the workflow** that names the tool, never read upward out of the tool;
a tool that listed its callers would offer a second answer to that question, free to drift from the
first.

### A tool is procedures-plus-assets, never an actor

A tool defines no role, holds no agent, and carries no authority of its own. It is executed by a role
— `renderer.render-document`, `reviewer.run-check` — and **that role's invariants apply to every line
of it and outrank anything written here**. This is what makes it safe for a tool to ship concrete
commands and template mechanics: none of it can grant a permission the executing role does not
already have.

### A tool is internal

A tool is present on disk and resolvable by name through this directory's index, and absent from
every selection surface: never registered with a harness, never discovered, never offered to a user
to choose from. It is reached in exactly three ways — a flow step naming `tool:<name>`,
`reviewer.run-check` given its spec, or a user naming it directly with explicit paths.

The reason is not tidiness. A component reached only through a flow depends on the flow having
already done something: gathered inputs, held a gate, established that the earlier checks were green.
Put it in a routing table and a request can land on it directly, skipping all of that, and the gate
that was supposed to be unconditional quietly is not. Being in this directory rather than beside the
public skills is what makes that structural rather than a rule someone has to remember: no packaging
format looks anywhere but the skills directory, so nothing here is ever scanned.

## Two declaration formats a tool uses, and where they are defined

These bind tool packages exactly as they bind skill packages, and they are **stated once**, in
`skill-conventions`:

| What a tool declares | Whose format it is |
|---|---|
| `## Dependencies` — the five columns, the four kinds, what each kind must additionally state, and the no-version-pinning rule | `skill-conventions` |
| `## User-context settings` — the heading, the five columns, and the rule that a key declared required with no default is also a `setting` row in `## Dependencies` | `skill-conventions` |

Keeping them there is deliberate. Both formats are read by things that do not care which kind of
package declared them — `setup-master.check-environment` aggregates every `## Dependencies` section
in the tree, and contract `user-context` describes one settings shape for the user's own file — and
splitting one format across two authorities is how two authorities end up disagreeing. Nor is this
arrangement new here: a directory-scoped conventions document already owns a rule that binds
packages elsewhere, and the script conventions below are the standing example.

## Scripts

Tool-owned scripts live in the package's own `scripts/` directory and follow the same conventions as
role-owned and skill-owned scripts — explicit CLI arguments, no parsing of context, rule or contract
files, cross-platform, and the two conventions for reading a script's exit code. Those are stated
once, in `role-conventions`, and they bind every bundled script in this package.
