# Skills

Orientation for a human reader. This is not a file an agent follows to do its work.

A **skill** is a procedure. Skills come in two groups:

- **workflows** orchestrate several roles end to end — they own the ordering, the gates and the run
  layout, and none of the rules of the roles they invoke;
- **tools** wrap one concrete operation. A tool can be run from a workflow step or on its own, and it
  never knows which workflow called it.

Skills are where concrete tool names are allowed to appear: each one declares what it genuinely needs
in its own `## Dependencies` section, and that declaration is the only place a real binary or service
is named.

## What is in here

- **the skill packages** — one directory per skill, inside its group directory, each holding a
  `SKILL.md` and optionally its own scripts and template bundles. A package is self-contained: it
  refers to its own files relatively and to everything else by name;
- **the shared conventions** — one ordinary document holding the house rules every package follows:
  the layout, the frontmatter, the required sections, the settings section and the dependency
  declaration format. It is an entity of this directory, not a second README;
- **the backlog** — planned but unbuilt work, recorded so that a decision already taken is not
  rediscovered later. Its entries have **no authority**: nothing in it exists, and nothing in it may
  be executed or cited as a rule.

## Where to start

**[`INDEX.md`](INDEX.md)** lists every skill and every other document here by name, with its group,
the file it resolves to and a one-line purpose. That index is the resolver an agent uses, and it is
the fastest way for a person to find the right skill too. Nothing in this directory is unlisted
there.
