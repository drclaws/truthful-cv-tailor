# Roles

Orientation for a human reader. This is not a file an agent follows to do its work.

A **role** is a specialized actor with a mission, an authority boundary, and a set of capabilities.
Roles are reusable across flows: the same role serves the CV flow, the bank refresh flow, and any
flow added later. Roles never call each other — data flows only through file artifacts, and
orchestration belongs to the flows.

## What is in here

- **the role packages** — one directory per role, each a compact `ROLE.md` index card plus one file
  per capability, and optionally its own scripts. A package is self-contained: it refers to its own
  files relatively and to everything else by name;
- **the shared conventions** — one ordinary document holding the house rules every package follows:
  the layout, the interaction model, progressive disclosure, the role-card and capability-file
  templates, tool abstraction, and the script conventions. It is an entity of this directory, not a
  second README.

A meeting **transcriber** role is planned but not built; only its output contract, `transcript`,
exists today. The entry for it lives in the skills backlog, and a backlog entry has no authority.

## Where to start

**[`INDEX.md`](INDEX.md)** lists every role and every other document here by name, with the location
it resolves to and a one-line mission. That index is the resolver an agent uses, and it is the
fastest way for a person to find the right role too. Nothing in this directory is unlisted there.
