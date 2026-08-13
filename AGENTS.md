# AGENTS.md

## What this repository is

A set of **toolchains for CV and job-search work**: reusable roles, skills, tools and artifact
contracts that turn a candidate's canonical experience sources and one vacancy's material into a
truthful, ATS-friendly, target-specific CV. It ships **zero user context** — no paths, no personal
data, no machine settings; it is *connected* to a working environment at setup time by the
`setup-master` role. Every rule in it has one authoritative home; load it when your step needs it.

**This file says how this tree is written. `engine-conventions` says how a run behaves.** That is
the whole of the division, and it decides where a new rule belongs: here if only a *file* would be
written wrong without it, there if a *run* would go wrong without it. The invariants, the reference
grammar, how an agent establishes where this package sits on the machine, what each step loads and
where a run writes are all in `engine-conventions`, and every public skill loads it before doing
anything else. They are there rather than here because **a file at a package root is not loaded when
this package is installed rather than cloned** — no packaging format has an instruction-file
component, and instructions reach an agent only through a skill it invokes. So **nothing depends on
this file having been read**: it is the author's document, and an executing agent that never opens
it is still bound by every rule it needs.

## How this repository's files are organized

**Three kinds of document, never mixed.** **Agent rules** are everything read as instruction: this
file, the contracts, the role cards and capability files, the `SKILL.md` and `TOOL.md` files, each
directory's index and its shared-conventions document — every rule in this section binds them.
**Indexes** are the resolvers: an `INDEX.md` maps a **name to a location**, plus only what a reader
needs in order to pick the right name (its kind and a one-line purpose). It carries no procedure and
no rule, and it is an agent rule. **READMEs** are human documents — **never** something an agent
follows to do its work, nor something an agent rule defers to. They may name concrete products as
examples, and they reference downward only: at their own index, never upward, never past it into the
entities below. **A directory therefore holds exactly two meta files**, `README.md` and `INDEX.md`,
**plus its entities**; shared rules are an ordinary indexed document of the directory
(`artifact-conventions`, `engine-conventions`, `role-conventions`, `skill-conventions`,
`tool-conventions`), never a third meta file.

**The package is what ships.** Everything in this tree travels as one unit and nothing outside it is
ever referenced — a harness that installs this package will not resolve a path that leaves it.
Inside it, a directory still refers to its own files relatively, and to everything else **by name**,
resolved through that kind's index. The by-name rule is no longer a limit; it is what keeps a rename
a one-line change in one index, and what lets a reader open any file without a map of the tree in
their head. **This file, the root `README.md`, and each directory's `INDEX.md` and `README.md` are
the single exception**: they may name package-relative paths, because something has to anchor the
scheme.

**No agent rule names a harness product.** An agent rule states **what must be determined** in order
to work with a harness — where it discovers definitions, what it takes a name from, which file it
auto-loads — and the local agent works out **how** for the system it is running in. No product name
appears in an agent rule: not as a requirement, not as an example, not as a parenthetical. READMEs
are exempt. It is tool abstraction applied to harnesses: an unknown harness needs no change here.

## Where the rest of it is

Each of the four directories carries an `INDEX.md` mapping name → location, written from the package
root, and a shared-conventions document holding the house rules its own entries follow. Start from
the index of the kind you need. Four names are worth knowing before you have one:

| Name | What it is |
|---|---|
| `engine-conventions` | The rules a run obeys, and the first thing a public skill loads: the invariants, the reference grammar, how the package root is established, what a step loads, and where a run writes. |
| `connect-environment` | The skill that connects this package to a machine — the harness in use and the local rules file it auto-loads, what the flows need from the user, the dependency matrix, and an offer to close the gaps it found. Nothing that changes the machine happens unasked. |
| `generate-targeted-cv` | The workflow that produces the CV for one vacancy, end to end. |
| `refresh-knowledge-bank` | The workflow that rebuilds the knowledge bank from the canonical experience sources. |

**Being shipped is not being active:** a validator runs only once it is in the ACTIVE validation
set, which contract `user-context` → *The active validation set* defines (including why the
mandatory truthfulness check is not in it) and `setup-master.register-skill` / `.update-settings`
manage. **Dependencies are declared once, by the package that needs them, skill or tool,** in its
own `## Dependencies` section, in the format `skill-conventions` owns;
`setup-master.check-environment` aggregates them transitively, including the registered validation
set, into the dependency matrix. Planned but **not built** work is listed in `BACKLOG`, whose
entries have no authority: never execute one as if it existed.
