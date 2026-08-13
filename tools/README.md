# Tools

Orientation for a human reader. This is not a file an agent follows to do its work.

A **tool** wraps one concrete operation — render this document, run this check — and ships whatever
that operation needs with it: its own scripts, its own template bundles. It is a procedure plus its
assets, never an actor: it defines no role, holds no authority of its own, and the invariants of
whichever role executes it always apply to it.

## Tools are internal, and that is a structural fact

Nothing here is offered to a user to pick from. A tool is reached in exactly three ways: a workflow
step names it, `reviewer.run-check` is handed its spec, or a user names one directly and passes the
paths. It lives in this directory rather than beside the public skills precisely so that no harness
can put it in a routing table — a component that exists to be reached *through* a flow has no
business in a surface where a request could land on it and skip the gates the flow holds.

That also means a tool is never a smaller skill and is not written like one. The word "skill" is
reserved for the packages a user may invoke; the document at the root of a tool package is `TOOL.md`,
and it is that tool's **spec** — the same word `reviewer.run-check` already uses for it.

## What is in here

- **the tool packages** — one directory per tool, each holding a `TOOL.md` and optionally its own
  scripts and template bundles. A package is self-contained: it refers to its own files relatively
  and to everything else by name;
- **the shared conventions** — one ordinary document holding the house rules every tool package
  follows: the layout, the frontmatter, the required sections, and the three rules that keep a tool
  a tool. It is an entity of this directory, not a second README.

Tools, like skills, are where **concrete tool names are allowed to appear**: each package declares
what it genuinely needs in its own `## Dependencies` section, and that declaration is the only place
in this directory where a real binary or service is named. Everywhere else the need is stated
abstractly, so that the same rules run on a machine bound differently.

## Where to start

**[`INDEX.md`](INDEX.md)** lists every tool and every other document here by name, with the file it
resolves to and a one-line purpose. That index is the resolver an agent uses, and it is the fastest
way for a person to find the right tool too. Nothing in this directory is unlisted there.
