# Contract: user-context

Version: 1.1

Defines **what** the flows in this repository need from the user, and **nothing about where the user
keeps it**. The repository ships zero user context: it is a set of toolchains that are connected to
a working environment at setup time.

Unlike every other contract, `user-context` does not describe a produced artifact and therefore
**carries no envelope** — the user's context lives in a free-form, harness-native file that the user
owns. What follows is the required information, how flows resolve it, and a copyable template.

## What flows need

Sections 1–5 are what a flow resolves at preflight. Sections 6 and 7 are setup's own records, kept in
the same file because it is the user's file: a flow neither reads them nor acts on them.

### 1. Canonical experience sources (required)

A **free-form** list of the sources of the candidate's experience: paths, URLs, or plain
descriptions, in any form and any number. No source kinds are prescribed and no structure is
imposed — the knowledge-bank-curator interprets whatever is listed.

Candidate identity (full name and similar identity facts) is **not** a separate context item: the
curator derives it from these sources into the knowledge bank's `## Candidate` section.

### 2. The active validation set (optional entries, required section)

The list of validation skills the user wants run, each with:

- **name** — the skill name (e.g. a `validate-cv-*` skill shipped in this repository, or a skill the
  user keeps in their own environment);
- **kind** — `internal` (runs in the pre-render check group) or `external` (runs only after internal
  and render gates pass);
- **location** — omitted for skills shipped in this repository; a path or description for skills
  that live outside it.

This set contains **optional validators only**. The mandatory truthfulness check is
`reviewer.fact-check`, a role capability that every CV flow invokes regardless of this list; it is
never recorded here. Everything in the set — including any ATS validator — is the user's choice: a
user whose render target is not an ATS-oriented CV may legitimately record an empty set.

A listed validator whose dependencies are unbound runs as SKIPPED with instructions. That is a
recorded outcome, never a flow failure.

### 3. Per-skill settings (optional)

Settings are recorded **per entity — one subsection per skill**. The recognized keys of a subsection
are defined by that skill's own `SKILL.md`; this contract defines only the shape. Machine-specific
bindings of a skill's external dependencies belong under the skill they serve, never in a shared
lump.

### 4. Additional rules (optional)

Free text the flows must honour: personal preferences, wording rules, things to avoid. Flows read it
and apply it; it never overrides the hard invariants (truthfulness, run isolation, sole-writer,
validation independence).

### 5. Toolchain directories (recorded at setup; needed wherever a name must be resolved)

The rules and cards of these toolchains refer to contracts, roles and skills **by name**. This
section records, for this machine, the directory that holds each of those three kinds, so that a name
can be turned into a file. It is a *location for names* and nothing more: each directory carries its
own index of what it holds, and a name absent from that index is an unresolved reference — reported,
never guessed into a path.

It is written by `setup-master.bootstrap` and revisited by `setup-master.update-settings`. It confers
no authority: nothing runs, and nothing becomes active, because it appears here.

### 6. Environment record (optional; written by setup-master)

A dated record of what setup prepared or bound on this machine and how that was verified — for each
entry: what it is, where it resolved to, which capability prepared it and when, and the verification
that was run with its result and date. Written by `setup-master.prepare-environment` and
`setup-master.register-with-harness`; those are the only writers.

It is a **record, not configuration**. Nothing is executed because it appears here, and it never
becomes a second home for bindings: a machine-specific value a skill declares stays under that
skill's subsection in section 3, and this section adds only provenance and verification. Its one
reader is `setup-master.check-environment`, which treats it as *dated evidence* — never stronger than
a fresh probe, and good only while the thing it names still resolves at the recorded location. Free
text elsewhere in the file is not a record and is not read as one.

### 7. Harness registration (optional; written by setup-master)

What was established about how the harness in use presents this repository's content to an agent, and
what registration created as a result: each location created, the canonical name it was created from,
the mechanism used, and the date. Written by `setup-master.register-with-harness` only.

It exists so that a later pass can reconcile — add what is missing, remove what no longer has a
canonical source — instead of silently repeating itself, and so that a kind of thing which **could
not** be registered is recorded as such, with the manual steps, rather than being retried every run.
Anything recorded here is a generated pointer to the canonical definition; it is never authority, and
a flow reached through it still reads the canonical file.

## Resolution

Flows resolve user context at **preflight**, in this order:

1. the harness-native local agent rules file (see below);
2. any other context or memory the harness provides;
3. ask the user.

On conflict, **the local rules file wins**. Every flow records in its `run.md` which resolution was
used and a snapshot of the resolved values.

Scripts never read context or rules files. The agent resolves values and passes them to scripts as
explicit command-line arguments.

## Default mechanism: the harness-native local rules file

An agent harness normally auto-loads a local rules file into every session. Its **name, location and
format differ per harness** and are determined by `setup-master.bootstrap` from the harness in use —
never assumed here. Using that file makes the context simply present, with zero resolution steps, and
lets the same file carry any personal rules the user wants honoured.

The repository does **not** ship this file. `setup-master.bootstrap` creates or updates it from the
template below, merging sections and never overwriting existing content without confirmation.

The file is **gitignored** (`*.local.md`) and must never be committed: it contains real paths and
personal data.

The mechanism is deliberately not mandated. Any way the user can make this information available
counts; the local rules file is the default because it is the cheapest.

## Preflight validation

Free-form input needs checking, not guessing. At preflight a flow validates the resolved context and
**asks the user** about anything missing or ambiguous:

- the experience-source list is non-empty, and each source is readable (an unreadable source is
  reported per source — it never crashes the flow; see the curator's freshness capability);
- every validation-set entry has a name and a kind, and resolves to an existing skill;
- every per-skill settings subsection names a skill that exists, and its keys are recognized by that
  skill's `SKILL.md` — unrecognized keys are reported, never silently ignored;
- when the flow's export naming needs candidate identity, the knowledge bank has a `## Candidate`
  section; if it does not, the flow asks the user or triggers a bank refresh;
- if a `validate-cv-*` skill shipped in this repository is absent from the recorded set, the flow
  **warns** — adding a validation skill without recording it leaves it inactive. The supported way
  to change the set is `setup-master.register-skill` / `setup-master.update-settings`;
- the toolchain directories are recorded and each one exists, whenever a name in the rules has to be
  resolved to a file. A missing directory, or one that no longer exists, is reported and asked about
  — a flow never guesses a path in its place, and an unresolved name is reported as unresolved.

The environment record and the harness-registration record are **never** preflight requirements: a
flow neither needs them nor acts on them. They are read by `setup-master` alone.

## Section template

The copyable template `setup-master.bootstrap` writes into the user's local rules file. Committed
form contains **placeholders only**.

```markdown
# Local context (gitignored — never commit)

## Experience sources (canonical)
Free-form list — any sources of the candidate's experience, in any form; the Curator interprets
them (identity included — no separate "candidate" entry is needed):
- <path or description>
- <path or description>

## Validation skills (the ACTIVE set; managed by setup-master.register-skill)
- <validator-skill-name>   (internal)
- <validator-skill-name>   (external)
# OPTIONAL validators only — the mandatory fact-check is a reviewer capability, not listed here.
# User skills may live outside this repo — register them here with kind + location.

## Skill settings (optional; ONE subsection per skill — keys defined by that skill's SKILL.md)
### <skill-name>
- <key>: <value>
### <skill-name>
- <per-service settings and dependency bindings for this machine>

## Additional rules (optional)
(free text the flows must honor)

## Toolchain directories (recorded at setup; how a name in the rules resolves to a file)
- contracts: <path to the directory holding the artifact contracts>
- roles: <path to the directory holding the role packages>
- skills: <path to the directory holding the skill packages>

## Environment record (written by setup-master; a record of this machine, not configuration)
- <what was prepared or bound>: <resolved location>
  — prepared by <capability> on <date>; verified by <the probe that was run> → <result> on <date>

## Harness registration (written by setup-master.register-with-harness)
- probe: <what was established about how this harness presents content> — determined <how>, <date>
- <what was registered>: <location created> ← <canonical name> (<mechanism>), created <date>
```
