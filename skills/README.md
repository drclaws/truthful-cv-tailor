# Skills

Orientation for a human reader. This is not a file an agent follows to do its work.

A **skill** is a procedure that orchestrates several roles end to end — it owns the ordering, the
gates and the run layout, and none of the rules of the roles it invokes.

This directory is the **public surface**: it holds every skill and nothing else, one directory per
skill, one level deep. That is not a filing preference. It is what a client scans to learn what may
be invoked, it looks only at the immediate children, and it is forbidden from searching deeper — so
a package any further down would not be found at all, and anything sitting here is offered whether
or not it was meant to be.

The single-operation packages — the renderer and the validators — are therefore **not** here. They
are **tools**, they live in the tools directory next door, and being there rather than here is
exactly what keeps them out of every selection surface. The index below carries the pointer for a
reader who arrives looking for one.

Skills are where concrete tool names are allowed to appear: each one declares what it genuinely needs
in its own `## Dependencies` section, and that declaration is the only place a real binary or service
is named.

## What is in here

- **the skill packages** — one directory per skill, each holding a `SKILL.md` and optionally its own
  scripts and template bundles. A package is self-contained: it refers to its own files relatively
  and to everything else by name;
- **the shared conventions** — one ordinary document holding the house rules every package follows:
  the layout, the frontmatter, the required sections, the settings section and the dependency
  declaration format. The last two of those bind tool packages as well, which is why they are stated
  there rather than twice. It is an entity of this directory, not a second README;
- **the backlog** — planned but unbuilt work of every kind, recorded so that a decision already
  taken is not rediscovered later. Its entries have **no authority**: nothing in it exists, and
  nothing in it may be executed or cited as a rule.

## Where to start

**[`INDEX.md`](INDEX.md)** lists every skill and every other document here by name, with the file it
resolves to and a one-line purpose. That index is the resolver an agent uses, and it is the fastest
way for a person to find the right skill too. Nothing in this directory is unlisted there.
