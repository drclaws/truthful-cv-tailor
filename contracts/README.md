# Contracts

Orientation for a human reader. This is not a file an agent follows to do its work.

A **contract** defines the FORMAT and SEMANTICS of one artifact: what it contains, what each part
means, who may produce it, and who consumes it. Contracts are the only interface between roles —
data flows through file artifacts, never through direct role-to-role calls.

A contract never defines PLACEMENT. Where an artifact is written is decided by the flow that runs the
step, or by the user when a role is invoked directly; the path is always passed to the role as an
explicit parameter.

## What is in here

Four kinds of file, and nothing else:

- **the contracts themselves** — one file per artifact, each declaring its own `Version:`, its status
  vocabulary and its sections;
- **the shared conventions** — one ordinary document holding the rules every contract inherits: the
  common envelope, artifact naming, truthfulness, run isolation, constraint proposals, versioning,
  and which capability produces which artifact. It is an entity of this directory, not a second
  README;
- **the engine's runtime conventions** — one ordinary document holding the rules a *run* obeys rather
  than the rules an artifact obeys: the invariants every step is bound by, how a name written in one
  file resolves to a file on disk, how an agent works out where this package sits on the machine,
  what each step loads, and where results are written. It lives here rather than at the package root
  because a root instruction file is not loaded when this package is installed rather than cloned,
  and a rule that never reaches the agent running the flow is not doing its job. Also an entity of
  this directory, not a second README;
- **an archival map** from the rules of the predecessor engine this repository replaced to the files
  that own them today.

## Where to start

**[`INDEX.md`](INDEX.md)** lists every document above by name, with a one-line purpose and the file
it resolves to. That index is the resolver an agent uses, and it is the fastest way for a person to
find the right contract too. Nothing in this directory is unlisted there.
