# Capability: setup-master.register-with-harness

## Purpose

Makes the skills and roles this repository ships discoverable by the harness in use, so that they can
be invoked by name rather than only by path. Whatever is created is generated **from** the canonical
packages and never the other way round: the packages stay the source of truth, and nothing created
here is ever read as authority.

This is not a fixed procedure. Harnesses differ in where they look for definitions, and — decisively
— in what an agent actually receives when one is presented to it. So the capability is a **probe
followed by a choice**: establish a short set of facts about the harness in use, then register each
package by the mechanism those facts allow. Where they allow none, registration **cannot complete**
for that kind, and saying so is the correct outcome.

Every machine-changing action here is an item of the assented plan defined in this role's
`## Authority`, and no item is offered until it names all five things that section requires of it.

It is invoked by the user, or offered by `bootstrap` at the end of a first setup pass.

## Inputs

- `skills_root` — path to the directory holding the shipped skills — required. Every skill package
  under it is registered; the directory is enumerated, never filtered.
- `local_rules_file` — path to the harness-native local rules file — required. It supplies the
  recorded toolchain directories — including where the role packages live — and it receives the
  registration record. Where a directory is not recorded yet, it is *proposed* from `repo_root` and
  confirmed by the user before anything is registered from it; an unconfirmed proposal is not used.
- `repo_root` — path to the repository being connected — required, to tell whether these toolchains
  stand on their own or are attached to another project (which decides where registration may write),
  and to confirm that anything created inside the repository is ignored by version control.
- `user_context_contract` — path to the `user-context` contract file — required when the registration
  record does not exist in the local rules file yet: its shape comes from the contract's section
  template, never invented here.
- `request` — register, re-register (reconcile), or remove a previous registration — required.

## Outputs

- **Discovery entries in the user's environment** — one per registered skill and per registered role,
  each at a location the user agreed to. They live outside this repository, are never artifacts of it,
  and are never tracked by it.
- **A resolution pointer** placed where the harness will read it, so that a name in these rules can be
  resolved to a file — in one location, or in more than one where that is what it takes to reach a
  delegated agent.
- **The registration record** in the local rules file's `## Harness registration` section: what the
  probe established and how, then per entry the location created, the canonical name it was created
  from, the mechanism, and the date. Kinds that could **not** be registered are recorded too, with the
  reason, so a later pass does not silently retry them.
- **An interactive report**: what is now invocable by name; what could not be registered, why, and the
  manual steps for it; and that invocation by path keeps working regardless.

## Procedure

1. **Establish the facts about the harness in use.**
   The answers come from the harness's own documentation where the agent can read it, from the user,
   or from inspection within the boundary in *Rules*. Each answer is stated as established or as
   **undetermined** — undetermined is a real answer here and the choice in step 4 handles it. State
   the questions, never presume the product that answers them:

   1. Does the harness discover skills from a directory of its own, and where — per user, and per
      project?
   2. Are the entries of that directory **directories**, or single files?
   3. Where does the harness take a skill's **name** from — the entry's directory name, or the
      definition's frontmatter?
   4. When the harness presents a skill's or an agent's body to an agent, **does that agent also
      receive the source location, and how is it expressed?** This is the probe of step 2, and it is
      the fact that decides the mechanism.
   5. Does the harness have a concept of a named agent, persona or mode — something addressable by
      name that runs with instructions of its own?
   6. Is such a definition **a file of its own, or an entry inside a shared configuration file the
      user also owns?** This one is decisive in a way the others are not: an entry inside the user's
      own configuration is a place this role may not write, so the answer decides whether registration
      of that kind can complete at all.
   7. What fields does that definition take, and in what format is its body?
   8. Which file does the harness auto-load as instructions for the main session?
   9. Does that auto-loaded content also reach delegated agents or sub-sessions? If not, what does?
   10. Are there limits on those files — a size cap, a first-match-wins or shadowing rule — that could
       silently drop content appended to them? And which of these locations are the **user's own
       configuration** rather than something registration may create?

2. **Settle fact 4 before anything is created, and record how.**
   Read what the harness documents about it; where that does not settle it, **ask the user**.
   Documentation-plus-ask is the rule. One minimal empirical registration — a single entry created
   only to observe whether a location comes back — may be **offered as its own assent item** and is
   never required: the fallback of step 4 is safe whenever the answer is unknown, so an empirical
   check buys efficiency, not correctness, and it writes into the user's environment to do it. If the
   user declines it, or it is inconclusive, the answer is undetermined and the fallback applies.

3. **Resolve where registration would write — never assume it.**
   Fact 1 and fact 6 give the *shape* of the location; which instance of it to use is a question, not
   a derivation. When these toolchains are **attached to another project**, that project owns its
   discovery locations: ask, and never derive one from this repository's layout. When the repository
   stands on its own, propose the per-user or per-project location the facts name, show it exactly,
   and confirm it. Anything created inside this repository must be ignored by version control before
   it is created.

4. **Choose the mechanism, per kind.**
   - **The presented body carries its source location** (fact 4 established), **and** the discovery
     location takes directory entries (fact 2) → **link the package directory** into the discovery
     location. No copy is made, so nothing can drift.
   - **The presented body does not carry its location, or fact 4 is undetermined, or the location
     takes files rather than directories, or this environment cannot make such a link** → **a
     wrapper carrying a pointer** (see *The wrapper*). This is the universal fallback, and it is the
     same rule for skills and for roles. A copy of the canonical body is never a third option.
   - **There is no discovery location for that kind, or the harness represents that kind only as an
     entry inside a configuration file the user owns** → **registration cannot complete for that
     kind.** Write nothing for it and go to step 9.

5. **Write the plan, and act only on assented items.**
   One item per location to be created, each named exactly, in the form `## Authority` requires:
   what will be invocable afterwards in the user's words, the exact path, the mechanism, the bounded
   verification, and how to undo it. Present the whole plan, then run agreed items one at a time. A
   declined item is recorded as declined and is not attempted by another route.

6. **Register every shipped skill and every shipped role.**
   Both kinds, on every run — not on request and not selectively. A role the user cannot see is a role
   the user cannot invoke, and invoking a role directly with explicit paths is a first-class use.
   - **Link the folder, never the definition file.** Where the mechanism is a link, it points at the
     package *directory*. A harness may accept a linked directory and ignore a linked definition file
     entirely, and it may do so without saying anything.
   - **The link name equals the frontmatter `name`.** No aliasing at registration, ever. A harness may
     derive identity from the entry name or from the frontmatter, and a mismatch makes the entity
     resolvable under one and invisible under the other. The frontmatter `name` and the package
     directory name are already the same string in every shipped package.
   - **Reconcile, do not repeat.** Where the record shows an earlier registration, add what is
     missing, remove what no longer has a canonical source, and leave the rest untouched. Removing an
     entry is itself an assent item. Anything at the discovery location that the record does not claim
     was created here is **left alone** — it may be the user's own.

7. **Place the resolution pointer.**
   The recorded toolchain directories have to reach the agent, or no name in these rules can be
   resolved. The pointer states where the contracts, the roles and the skills of this repository live
   on this machine, and it goes into the file fact 8 names — **and, where fact 9 says that content
   does not reach delegated agents, into whatever does as well.** More than one location is allowed;
   **each location is its own assent item**, named exactly and recorded separately. The same authority
   limit applies: the pointer is written only into a file this role creates itself or into the user's
   own local rules file, never into a harness's own configuration.

8. **Verify each item, then record.**
   One bounded check per item, as `ROLE.md` defines a verification probe — the entry resolves to the
   canonical package; the wrapper exists at the named path and the canonical path it names resolves;
   the entity appears in whatever the harness reports as discoverable, where it reports anything.
   **Verify the pointer by reading it back from where the harness will read it**, because fact 10's
   caps and shadowing rules discard appended content silently: a write that returned successfully is
   not evidence that the content survived. Then record every executed item in the local rules file's
   `## Harness registration` section, merging into what is there and clobbering nothing. An item that
   could not be verified is recorded as created-but-unverified and reported as such.

9. **Report — including what could not be done.**
   Per kind: what is now invocable by name and where from; what was declined; and what **cannot** be
   registered on this harness, in one sentence the user can act on, followed by the manual steps they
   would take to do it themselves — quoted from what facts 6 and 7 established, never invented. State
   in every case that invocation by path still works and is valid everywhere.

## The wrapper

The fallback mechanism, and the only thing besides a link that this capability creates. A wrapper is a
file it writes at the discovery location, in the field vocabulary and body format fact 7 established,
containing exactly:

- the entity's **`name` and short `description`, copied verbatim** from the canonical frontmatter —
  the only thing ever copied out of a canonical file, and the only place drift is possible, which is
  what step 6's reconciliation exists to correct;
- a body whose **first instruction** is, in imperative form: *before any other action, read the
  canonical definition at `<its real path on this machine>` and follow it*. The agent then holds a
  **path**, not a copy — it reads the canonical file where it actually lives, so every relative link
  inside the package resolves;
- for a **role**, the interaction model below, and nothing else.

**The cost, stated plainly:** a wrapper depends on the agent obeying the read instruction. There is no
mechanism behind it. It is mitigated by imperative phrasing — *before any other action, read …* — and
by keeping the wrapper body short enough that the instruction cannot be lost in it. It is not
mitigated by adding a summary of the canonical file, which would be the copy this design exists to
avoid.

### A role wrapper carries the interaction model

A registered role is presented by the harness as an **independently callable agent**, which makes the
one call path this design forbids — role calling role — the easiest one in the interface. So the
interaction model has to travel with the wrapper. Its body states, in its own words:

- **data flows only through file artifacts governed by contracts** — the role reads its inputs from
  paths it was given, and writes its outputs to paths it was given;
- **a role never invokes another role.** Orchestration happens only through flow skills; a role
  produces an artifact, and the flow decides who reads it next;
- **all paths are mandatory parameters.** The role assumes no repository layout; the caller — a flow,
  or the user — passes explicit input and output paths.

**This duplicates `role-conventions`, deliberately.** It is the one duplication in this design, and it
is not a defect to be cleaned up later: the wrapper is what the harness presents to the agent, and a
rule the reader never receives does not bind. Whoever tidies this must keep the two in step instead of
deleting one.

## Rules

- **The canonical packages are the source of truth, and generation runs one way.** Everything created
  here is derived from them. A canonical file is never edited to suit a harness, never moved to a
  discovery location, and never copied into one.
- **An adapter is never authority.** A flow or a role reached through a link, a wrapper or a pointer
  still reads the canonical file, and that file is what governs. A wrapper that starts to carry rules
  of its own has become a second source of truth, which is precisely the failure this mechanism is
  shaped to prevent.
- **This role creates its own files and nothing else.** It never edits a harness's own configuration
  file — not to add an entry, not to fix one, not "just this once". Where a harness holds a kind of
  definition **only** as an entry inside a configuration file the user owns, there is no file here to
  create, so **registration of that kind cannot complete**: write nothing, report which kind and why
  in one sentence the user can act on, hand over the manual steps quoted from what the facts
  established, state that invocation by path still works everywhere, and record the outcome so a later
  run does not retry it. This is not a degraded mode to be worked around. An agent that edits the
  user's configuration *because otherwise registration fails* has broken the one invariant this role
  exists to protect.
- **Both skills and roles, always.** Every shipped skill and every shipped role is registered on every
  run of this capability.
- **Bounded discovery.** This capability, and everything it invokes, looks only where the discovery
  boundary defined in this role's `## Authority` permits. A discovery location that is not inside it
  is a question to the user, never something to go looking for.
- **Nothing is pinned and nothing is recited.** This file names no harness, no discovery path and no
  file name of any harness's own: it states what must be *determined*, and the agent working inside a
  given harness determines it. A harness that did not exist when this was written is supported by
  answering the same ten facts, with no change here.
- **Prepare, never execute**, as `ROLE.md` defines both. Registering a flow is not running it, and the
  verifications of step 8 use no CV, vacancy or bank data.
- **Merge, never clobber.** The record is added to; content this role does not own in the user's file
  is preserved, and changing an existing entry needs confirmation of that specific change.
- **No private path leaves the machine.** Resolved locations belong in the user's local file and in
  the interactive report — never in a file tracked by this repository.

## Failure and skip conditions

| Situation | Behaviour |
|---|---|
| The harness in use cannot be identified, or facts 1–3 cannot be established | Register nothing. Report what could not be determined and what would settle it. Guessing a discovery location is never permitted. |
| Fact 4 is undetermined | Not a failure: use the wrapper, which is safe under either answer, and record fact 4 as undetermined with the reason. |
| The harness has no discovery location for a kind, or holds that kind only inside the user's own configuration | Registration of that kind **cannot complete**. Write nothing for it; report it with the manual steps and with what still works; record it so it is not retried silently. |
| This environment cannot create a link at the agreed location | Fall back to a wrapper for that entry. Never a copy, and never a different location than the one agreed. |
| `local_rules_file` does not exist yet | Stop. Point at `bootstrap`, which creates it: there is nowhere to record an outcome, and the toolchain directories the pointer needs are not recorded yet. |
| The toolchain directories are not recorded and the user does not confirm a proposal | Register nothing that depends on the unconfirmed directory, and place no pointer. Report what is still needed. |
| The toolchains are attached to another project and no location is agreed | Register nothing there. Report what the owner of that project would need to decide. |
| The user declines every item | Write nothing, report the no-op, and state that invocation by path is unaffected. Not an error. |
| A pointer was written but reading it back does not find it | Report it as not in effect, name the limit that most likely discarded it, and leave the file as it is. Do not write it again elsewhere on this capability's own initiative — a different location is a new assent item. |
| An entity's frontmatter `name` differs from its package directory name | Register neither name. Report it as a defect of that package; renaming a package is not this capability's to do, and aliasing it here would hide the defect. |
| The record claims an entry that no longer exists, or a discovery location holds an entry the record does not claim | Report both. Recreate only what the user agrees to recreate, and never remove what this capability did not create. |
| A verification fails after an item ran | Record the item as created-but-unverified, report the entity as not confirmed discoverable, and leave it alone. |
