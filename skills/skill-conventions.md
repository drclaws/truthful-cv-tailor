# Skill conventions

The house rules for every skill package in this directory: the package layout, the frontmatter, the
required section set, the settings section, and the `## Dependencies` declaration format. This
document is the authority on what a declaration must **contain**; how a declaration is probed and
what counts as evidence belongs to `setup-master.check-environment`.

This is an ordinary document of the skills directory, listed in the index like any skill. Refer to it
by the name `skill-conventions`.

## The two groups

- A **workflow** orchestrates several roles end to end. It owns the ordering, the gates and the run
  layout; it never contains the rules of the roles it invokes.
- A **tool** wraps one concrete operation and is invocable both from a workflow step and standalone.
  A tool never names a calling workflow or a calling step: that would couple tools to flows, which
  the interaction model forbids.

## Package layout

A skill package is a directory named for the skill, inside its group directory, and it travels as a
unit:

```
<group>/<skill-name>/
├── SKILL.md                    # the skill itself
├── scripts/                    # optional; bundled scripts, explicit CLI arguments only
└── templates/                  # optional; bundles the skill resolves and fills
```

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
packages.

## Required sections

Present in **every** skill:

| Section | Holds |
|---|---|
| an opening statement | what this skill is and is not. The heading wording is free. |
| `## Inputs` | every input the skill takes, as an index: name — what it is (a contract name where one applies) — required or optional. An index, never a second home for rules. |
| `## User-context settings` | the settings section, below. Present even when the skill recognizes no keys. |
| `## Dependencies` | the dependency declaration, below. It is the **last** section of the file. |

A **tool** skill additionally carries `## Outputs` (each output as: name — contract or description —
the status values it may set) and `## Runbook` (how the operation is actually performed).

A **workflow** additionally carries `## Steps` (the step table: step → executor → inputs → outputs),
`## Gates` (the named gates, whose names are used verbatim in the steps), `## Definition of done`
and `## Escalation`.

Sections beyond the required set are free, and every shipped skill has several.

## The settings section

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

**Dependencies are declared once, here.** A workflow declares only its *direct* dependencies and
inherits the rest from the tool skills and capabilities its steps invoke;
`setup-master.check-environment` resolves that transitively.

## Scripts

Skill-owned scripts live in the package's own `scripts/` directory and follow the same conventions as
role-owned scripts — explicit CLI arguments, no parsing of context or rule files, cross-platform, and
the two outcome conventions for reading a script's exit code. Those conventions are stated once, in
`role-conventions`, and they bind every bundled script in the repository.
