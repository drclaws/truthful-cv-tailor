# Capability: setup-master.register-with-harness

## Purpose

Makes this package's **public skills** reachable in the harness in use, so that a user's request can
land on one by name. Whatever is created is generated **from** the canonical packages and never the
other way round: the packages stay the source of truth, and nothing created here is ever read as
authority.

**Installing this package is what registers it**, wherever the harness in use can install one: it
finds the public skills inside by itself, so there is nothing per-skill to generate and nothing that
can drift out of step with a canonical file. What is left is the genuinely uncertain part — *whether*
this harness loads such a package, *where* from, and whether that place is somewhere this role may
write at all. So the capability is a **probe followed by a choice**: establish four facts, then use
the mechanism they allow. Where they allow none, registration **cannot complete**, and saying so is
the correct outcome.

Every machine-changing action here is an item of the assented plan defined in this role's
`## Authority`, and no item is offered until it names all five things that section requires of it.

It is invoked by the user, or offered by `bootstrap` at the end of a setup pass.

## Inputs

- `package_root` — the resolved root of this package — required. What registration covers is the
  public skills, which are the immediate children of the skills directory inside it; that directory
  is enumerated, never filtered. Contract `user-context` is read from it as well, when the
  registration record does not exist in the local rules file yet: the record's shape comes from that
  contract's section template and is never invented here.
- `local_rules_file` — path to the harness-native local rules file — required. It receives the
  registration record.
- `project_root` — the user's working project, or none — required, because it decides where
  registration may write and lets anything created inside that project be checked against its ignore
  rules.
- `request` — register, re-register (reconcile), or remove a previous registration — required.

## Outputs

- **What the harness will now load** — this package, or a link to it, at a location the user agreed
  to; or, where the harness has no package format, one entry per public skill at the location it
  reads. These live outside this package, are never artifacts of it, and are never tracked by it.
- **The registration record** in the local rules file's `## Harness registration` section: what the
  probe established and how, then per entry the location created, the canonical name it was created
  from, the mechanism, and the date. Anything that could **not** be registered is recorded too, with
  the reason, so a later pass does not silently retry it.
- **An interactive report**: what the harness will now find; what could not be registered, why, and
  the manual steps for it; and how these files can be reached meanwhile.

## Procedure

1. **Establish the facts about the harness in use.**
   The answers come from the harness's own documentation where the agent can read it, from the user,
   or from inspection within the boundary in *Rules*. Each answer is stated as established or as
   **undetermined** — undetermined is a real answer here, and step 4 handles it. State the questions,
   never presume the product that answers them. There are four:

   1. Does the harness load a package of this shape from a location of its own, and where — per user,
      and per project?
   2. When it presents a file from such a package to an agent, does the agent also receive **where
      that file lives**, and in what form? This one decides whether a run can reach the rest of this
      package at all, so it is asked here rather than left for the first run to discover.
   3. Is that location something this role may create in, or is it an entry inside a configuration
      file the user owns? This one is decisive in a way the others are not: an entry inside the
      user's own configuration is a place this role may not write, so the answer decides whether
      registration can complete at all.
   4. Where there is no package format: does the harness read loose skill directories from a location
      of its own, so that placing this package's public skills there serves the same purpose?

2. **Settle question 2 before anything is created, and record how.**
   Read what the harness documents about it; where that does not settle it, **ask the user**.
   Documentation-plus-ask is the rule. One minimal empirical registration — a single entry created
   only to observe whether a location comes back — may be **offered as its own assent item** and is
   never required: an undetermined answer does not block registration, it is a fact a run will meet
   and report honestly, so an empirical check buys knowledge earlier rather than correctness, and it
   writes into the user's environment to buy it. If the user declines it, or it is inconclusive, the
   answer is undetermined and is recorded as such with the reason.

3. **Resolve where registration would write — never assume it.**
   Questions 1 and 3 give the *shape* of the location; which instance of it to use is a question, not
   a derivation. Where a per-user location and a per-project one both exist, ask which the user
   wants: a package installed for the user is present in every project, and connecting it to one
   project is not the same act as connecting it to all of them. Propose the location, show it
   exactly, and confirm it. Anything created inside the user's project must be ignored by version
   control before it is created.

4. **Choose the mechanism.**
   - **The harness has a package format, and question 3 says this role may create at that location**
     → place this package, or a link to it, there, as an assented item. Nothing is copied out of a
     canonical file, so nothing can drift.
   - **No package format, but a location the harness reads loose skill directories from** → link each
     public skill package into it. This is why the flat shape of the skills directory is the better
     fallback: every public skill is one directory at one depth, so the fallback needs no generated
     file, has nothing to keep in step, and follows from the layout rather than from a mechanism
     maintained here.
   - **Neither, or the harness holds that kind of thing only inside a configuration file the user
     owns** → **registration cannot complete.** Write nothing, report which kind and why in one
     sentence the user can act on, hand over the manual steps, and record the outcome so a later pass
     does not silently retry it. This is the outcome the never-edit-a-harness's-configuration rule
     produces, and it is a correct one, not a degraded one.

5. **Write the plan, and act only on assented items.**
   One item per location to be created, each named exactly, in the form `## Authority` requires:
   what will be reachable afterwards in the user's words, the exact path, the mechanism, the bounded
   verification, and how to undo it. Present the whole plan, then run agreed items one at a time. A
   declined item is recorded as declined and is not attempted by another route.

6. **What becomes discoverable, and what deliberately does not.**
   The public skills are what a user's request is meant to land on, and they are what the harness is
   made to see. The roles, the tools and the contracts are components: they are reached through a
   flow, by name, from inside this package, and putting them in a selection surface would let a
   request bypass the flow that holds the gates. Registration therefore covers the public skills and
   nothing else — not as a limitation, but because a component reached only through a flow has no
   business in the user's or the model's menu.

   Every public skill, on every run of this capability — not on request and not selectively.

   - **Link the folder, never a definition file.** Where the mechanism is a link, it points at the
     *directory*. A harness may accept a linked directory and ignore a linked definition file
     entirely, and it may do so without saying anything.
   - **The link name equals the frontmatter `name`.** No aliasing at registration, ever. A harness may
     derive identity from the entry name or from the frontmatter, and a mismatch makes the package
     resolvable under one and invisible under the other. The frontmatter `name` and the package
     directory name are already the same string in every package here.
   - **Reconcile, do not repeat.** Where the record shows an earlier registration, add what is
     missing, remove what no longer has a canonical source, and leave the rest untouched. Removing an
     entry is itself an assent item. Anything at the location that the record does not claim was
     created here is **left alone** — it may be the user's own.
   - **Undoing registration is this same capability**, invoked with that request — the case when the
     user disconnects these toolchains from the harness. It removes exactly what the record claims was
     created here, as assented items, and clears those entries from the record. It is never a separate
     mechanism and never a wider sweep of the location.

7. **Verify each item, then record.**
   One bounded check per item, as `ROLE.md` defines a verification probe — the entry resolves to the
   canonical package, and the package appears in whatever the harness reports as loadable, where it
   reports anything. **Read back from where the harness reads**, because a write that returned
   successfully is not by itself evidence that what was written survived and will be found. Then
   record every executed item in the local rules file's `## Harness registration` section, merging
   into what is there and clobbering nothing. An item that could not be verified is recorded as
   created-but-unverified and reported as such.

8. **Report — including what could not be done.**
   What the harness will now find and where from; what was declined; and what **cannot** be registered
   on this harness, in one sentence the user can act on, followed by the manual steps they would take
   to do it themselves — quoted from what the facts established, never invented. In every case say how
   these files can be reached meanwhile: by-path invocation is valid wherever the user has these files
   at a path they can name, which is the case when this engine is cloned; once it is installed as a
   package, the public skills are invocable by name and that is the supported route.

## Why nothing is generated per entity

An earlier form of this capability wrote a **wrapper** per entity at the discovery location: a small
file carrying the entity's name and description plus an instruction to read the canonical definition.
Recorded here as rejected, so that nobody reintroduces it. A directory the harness loads does the same
job with no generated file — nothing to keep in step, nothing to drift, and no dependence on an agent
obeying a read instruction, which was the wrapper's one real weakness and had no mechanism behind it.
The case it existed for, a **role** presented as an independently callable agent, is gone with it: no
role is registered, because a role reached outside a flow is a role reached around the flow's gates,
and the interaction model a role wrapper carried has one home in `role-conventions`.

## Rules

- **The canonical packages are the source of truth, and generation runs one way.** Everything created
  here is derived from them. A canonical file is never edited to suit a harness, never moved to the
  location the harness reads, and never copied into it.
- **A pointer is never authority.** A skill reached through a link still reads the canonical file, and
  that file is what governs. Anything created here that starts to carry rules of its own has become a
  second source of truth, which is precisely the failure this mechanism is shaped to prevent.
- **This role creates its own files and nothing else.** It never edits a harness's own configuration
  file — not to add an entry, not to fix one, not "just this once". Where a harness holds a kind of
  definition **only** as an entry inside a configuration file the user owns, there is no file here to
  create, so **registration of that kind cannot complete**: write nothing, report which kind and why
  in one sentence the user can act on, hand over the manual steps quoted from what the facts
  established, state how these files can be reached meanwhile, and record the outcome so a later run
  does not retry it. This is not a degraded mode to be worked around. An agent that edits the user's
  configuration *because otherwise registration fails* has broken the one invariant this role exists
  to protect.
- **The public skills, and all of them.** Every public skill on every run of this capability, and no
  role, tool or contract ever. The first half is why a skill is never missed; the second is why a
  request cannot land on a component and bypass the flow that holds the gates.
- **Bounded discovery.** This capability, and everything it invokes, looks only where the discovery
  boundary defined in this role's `## Authority` permits. A location that is not inside it is a
  question to the user, never something to go looking for.
- **Nothing is pinned and nothing is recited.** This file names no harness, no location and no file
  name of any harness's own: it states what must be *determined*, and the agent working inside a given
  harness determines it. A harness that did not exist when this was written is supported by answering
  the same four questions, with no change here.
- **Prepare, never execute**, as `ROLE.md` defines both. Making a flow reachable is not running it, and
  the verifications of step 7 use no CV, vacancy or bank data.
- **Merge, never clobber.** The record is added to; content this role does not own in the user's file
  is preserved, and changing an existing entry needs confirmation of that specific change.
- **No private path leaves the machine.** Resolved locations belong in the user's local file and in
  the interactive report — never in a file tracked by this repository.

## Failure and skip conditions

| Situation | Behaviour |
|---|---|
| The harness in use cannot be identified, or questions 1 and 3 cannot be established | Register nothing. Report what could not be determined and what would settle it. Guessing a location is never permitted. |
| Question 2 is undetermined | Not a failure: register anyway and record the answer as undetermined with the reason. A run that then cannot establish where its files are says so and asks, which is the anchor rule's own outcome. |
| The harness has no location for this at all, or holds it only inside the user's own configuration | Registration **cannot complete**. Write nothing; report it with the manual steps and with how these files can be reached meanwhile; record it so it is not retried silently. |
| This environment cannot create a link at the agreed location | Offer placing the package itself there instead, as its own assent item. Never a copy of a definition file, and never a different location than the one agreed. |
| `local_rules_file` does not exist yet | Stop. Point at `bootstrap`, which creates it: there is nowhere to record an outcome. |
| The user's project is where registration would write and no location is agreed | Register nothing there. Report what the owner of that project would need to decide. |
| The user declines every item | Write nothing, report the no-op, and state how these files can be reached meanwhile. Not an error. |
| An entity's frontmatter `name` differs from its package directory name | Register neither name. Report it as a defect of that package; renaming a package is not this capability's to do, and aliasing it here would hide the defect. |
| The record claims an entry that no longer exists, or a location holds an entry the record does not claim | Report both. Recreate only what the user agrees to recreate, and never remove what this capability did not create. |
| A verification fails after an item ran | Record the item as created-but-unverified, report the entity as not confirmed loadable, and leave it alone. |
