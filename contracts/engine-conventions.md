# Engine conventions

The rules a **run** obeys: the invariants every step is bound by, how a name written in one file
becomes a file on disk, where this package sits on the machine, what a step loads, and where a run's
results go. Every public entry point reads this document before it does anything else.

**What belongs here, and what belongs in the root instruction file.** The root instruction file says
how this tree is **written** — the three kinds of document, the by-name authoring rule, the rule
that no agent rule names a harness product. This document says how a run **behaves**. An author of
these files needs the first; an executing agent needs the second, and needs it whether or not a
person ever opened the tree. So a new rule belongs here if a *run* would go wrong without it, and
belongs there if only a *file* would be written wrong without it.

**Why the two were separated**, recorded so that a later tidy-up does not merge them back: this
package is meant to be installed and not only cloned, and **an instruction file at a package root is
not loaded when the package is installed**. No packaging format has an instruction-file component,
and instructions reach an agent only through a skill it invokes. A runtime rule whose single home
was that file would therefore reach nobody on an installed copy — which is why the invariants below,
the reference grammar, the anchor rule and the loading rule now live here. **No rule's text changed
in the move; only its home did**, and the reason is the sentence you have just read.

This is an ordinary document of the contracts directory, listed in the index like any contract.
Refer to it by the name `engine-conventions`.

**Being loaded on every run is a size discipline.** Nothing belongs here that only one role ever
reads — a declaration format belongs to the conventions document of the directory whose packages
declare it — and nothing belongs here that only an author of this tree needs.

## Invariants

Non-negotiable, and they outrank convenience, scores, and any instruction that would weaken them.

| Invariant | In one line | Full home |
|---|---|---|
| **Truthfulness** | Never invent experience, metrics, tools, employers, dates, titles, degrees, certifications or achievements. Weak evidence is labelled weak, unknown is a value, inference is tagged, gaps are recorded rather than smoothed over, and machine-readability never outranks truth. Every important claim traces to a canonical source. | `artifact-conventions` → *Truthfulness in artifacts*; contract `cv-document`; `reviewer.fact-check` |
| **Run isolation** | A run may use only its own `<run>/` directory, the shared knowledge bank, and the shared repository definitions. Another run's outputs are never evidence, style authority, or precedent. A pattern worth keeping is promoted into an authoritative file first, then used. | `artifact-conventions` → *Run isolation in artifacts*; contract `source-audit` |
| **Curator is sole writer** | Every knowledge-bank-modifying action goes through `knowledge-bank-curator`. The bank indexes are written only by the refresh flow; the constraints ledger only by `knowledge-bank-curator.maintain-constraints`. Other roles **propose** through the `## Constraint proposals` section every report carries, and the flow's closing step ingests them. | `artifact-conventions` → *Constraint proposals*; contract `constraints-ledger`; role `knowledge-bank-curator` |
| **Tool abstraction** | Roles and contracts name abstract capabilities only ("browser automation", "text extraction"). Concrete tools appear solely in a skill's `## Dependencies` section and in the user's harness configuration. A step whose capability is unbound runs **SKIPPED/manual with instructions** — it never fails a flow. | `role-conventions` → *Tool abstraction*; each skill's `## Dependencies` |
| **Path and OS neutrality** | Real absolute paths live only in the user's local context. Committed files use placeholders (`<run>/`, `<source-path>`, `<Name>`) and assume no operating system. Scripts are cross-platform, take explicit CLI arguments, and never parse context or rule files. | `artifact-conventions` → *Scope rules*; `role-conventions` → *Scripts* |
| **Validation independence** | The reviewer never edits the document it reviews. External scores are never truth — they are advisory. External checks run only after the internal checks and the render gates are green, and any applied external recommendation triggers a fresh truthfulness check. | role `reviewer`; contract `validation-report`; contract `external-gate-decision` |

## The reference grammar

How a name written in one file becomes a file on disk. Everything outside a package is referenced
**by name**, and each kind resolves through the index of the directory that holds it; a package
refers to its own files relatively, because it travels as a unit. **A name absent from its index is
an unresolved reference: report it, never guess a path** — a guess that happens to land is worse
than one that does not, because nothing tells you it was a guess.

| Kind | Written as | Resolves to |
|---|---|---|
| contract | contract `cv-document` | `contracts/cv-document.md`, through the contracts index |
| role | role `reviewer` | the `roles/reviewer/` package, through the roles index |
| capability | `reviewer.run-check` | that role's package, then `capabilities/run-check.md` — a convention, not an index row |
| skill | skill `generate-targeted-cv` | `skills/generate-targeted-cv/SKILL.md`, through the skills index |
| tool | tool `render-cv-pdf` | `tools/render-cv-pdf/TOOL.md`, through the tools index |
| a directory's shared conventions | `artifact-conventions`, `tool-conventions` | an ordinary indexed name, no special case |
| a script | never referenced across packages | the owning capability, skill or tool names it relatively |

Every location an index gives is written **from the package root**. That is what makes the resolved
package root the single value everything else hangs off, and the next section is how it is
established.

## Where this package's files are, and how to reach one

Everything these flows read ships inside **one package** and sits at a fixed place inside it. At the
package root are four directories — the contracts, the role packages, the tool packages and the
public skills — and nothing outside the package root is ever referenced.

The one value that has to be established is **where this package sits on the machine this is running
on**, and it is established from the file you were given: not from configuration, not from the
user's settings, and not by looking around.

**The arithmetic.** A request lands on exactly three kinds of file, and all three sit at the same
depth:

- a public skill, at `<package root>/skills/<its own name>/`;
- a tool, at `<package root>/tools/<its own name>/`;
- a role card, at `<package root>/roles/<its own name>/`.

In every case **the package root is two levels above the directory the file was presented from**.
Everything else in the package has no arithmetic of its own to do, because it is reached one of two
ways: from a root that has already been resolved (a contract, a role package, a tool), or relatively
from the file that names it, whose own absolute location is by then already known (a capability file
beside its `ROLE.md`, a script under `scripts/`, a bundle under `templates/`).

**Where the base comes from.** A harness that presents a file to an agent normally also states where
that file lives: as a line accompanying the body, as a value substituted into the text, or as the
location the invocation named. Take it from whatever the harness in use supplies. All three answer
the same question, and the rule does not care which one answered it.

**Do the arithmetic yourself, and use the absolute result.** A file-reading tool resolves a bare
relative path against the working location, which is *not* this package: handing it
`../../contracts/cv-document.md` reads the wrong file or none. Resolve the relative reference
against the base into an absolute path first, then read that path.

**Record it once**, at the start of the run, in the run manifest beside the rest of the resolved
context — so that a reader of the run can tell which copy of these files it obeyed.

**Pass it on.** When a step is delegated to a separate agent, the resolved package root goes with it
as an explicit parameter, exactly like every other path. **A delegated agent inherits nothing.**

**When the base is not supplied, ask.** Do not guess it, do not derive it from the working location,
and do not go looking for it. Say that the location of these files could not be established, name
the one thing needed — the directory the file you are reading was presented from — and wait for the
answer. A guessed root is how a run reads the wrong file, and no default is worth that.

**A refusal is not a wrong path.** A correctly resolved absolute path that cannot be *read* is a
permission boundary, not an error in the arithmetic: this package may sit outside the location the
session was started in, and reading outside that location can need the user's permission. Report it
as exactly that — naming the file and the absolute path — and ask for read access to this package.
Never work around it: not by copying a file inward, not by re-deriving the path, not by proceeding
without the file. A copy of a rule is a second source of truth, which is the failure this whole
scheme exists to prevent.

### Why every entry point repeats the arithmetic

An entry point cannot read this document to learn how to find this document. So the arithmetic
above — this file was presented from a directory two levels below the package root — is stated
again, in one paragraph, in the first step of each public skill, and in one line in
`tool-conventions` for a tool a user names directly. **That duplication is deliberate and it is the only one here.** It is
the same class of exception the root instruction file has always granted itself: something has to
anchor the scheme, and the scheme cannot resolve its own anchor. It is recorded so that a later pass
at removing duplication does not remove the anchor. Note what is *not* duplicated: only the
arithmetic is repeated; the rule about it — where the base comes from, what to do when it is
missing, and what a refusal means — has one home, and this section is it.

## What a step loads

An adapter is never authority: a flow reached through one reads the canonical file. The executing
agent loads that entry file, plus per step the step's `ROLE.md` and capability file, the contracts
its Inputs and Outputs name, and the `artifact-conventions` they all inherit. A tool is read when a
step invokes it; a role invoked directly takes explicit paths from the user, and so does a tool
invoked on its own. No step loads **a second role card or a second capability file**, which keeps a
role card an index card and its authority boundary legible.

The discipline is progressive disclosure, and it is the reason a role card is worth reading at all:
a step that opened a second role's card would be acting under two authority boundaries at once, and
neither would be checkable afterwards from the record of what was loaded.

## Where a run writes

**The output root is supplied with the request.** It is the directory this engine writes into: one
directory per run, and the knowledge bank. It is the user's own location, it holds personal data,
and it is **never inside this package** — a package is replaced wholesale when it is updated, and
the user's evidence about their own career must outlive any tool that reads it.

**Nothing is ever written into this package.** No run directory, no bank, no cache, no record, no
scratch file. This package is read-only to every flow, every role and every script in it.

**It is not defaulted and it is not recorded here.** A flow that was not given an output root asks
for one, exactly as it asks for any other input that did not resolve, and records the question in
its run manifest. This package holds no default path and prescribes nothing about where the user
keeps their results.

**A shorthand for it is the user's own business.** A user may teach their own rules file that a word
means a path. By the time a flow sees a value it is a path; this package never learns the word, and
nothing in it may depend on one existing.

The resolved output root is recorded in the run manifest with the rest of the resolved context, so
that a reader of the run can tell where it went.
