# Capability: setup-master.prepare-environment

## Purpose

Closes gaps that `check-environment` reported, by means worked out for the environment that is
actually present, and records what was done so a later check can see it. The dependency matrix says
*what is missing*; the package that declared it says *what must become possible*; this capability
works out *how*, here, on this machine — and asks before anything changes. It may also conclude that a gap
cannot be closed in this environment: that is a result of the capability, not a failure of it.

Every machine-changing action here is an item of the assented plan defined in this role's
`## Authority`, and no item is offered until it names all five things that section requires of it.

It is invoked by the user, or offered by `bootstrap` once the dependency matrix exists.

## Inputs

- `dependency_matrix` — the matrix `check-environment` produced — required. If none is at hand, run
  `check-environment` first. This capability never re-derives dependencies of its own and never adds
  a requirement no package declared.
- `gaps` — which of the reported gaps to work on — required, and it is the user's answer. "All of
  them" is a valid answer; "none" ends the capability with a report and no action.
- `local_rules_file` — path to the harness-native local rules file — required. It holds any binding
  the user already recorded, and it receives the environment record.
- `package_root` — the resolved root of this package — required, to read the declaring package's
  `## Dependencies` entry and its runbook, which are the only source of the goal; and to read
  contract `user-context` when the record section does not exist in the local rules file yet, since
  its shape is taken from that contract's section template and is never invented here.
- `project_root` — the user's working project, or none — required, because it decides where a
  prepared thing may live and lets anything created inside that project be checked against its
  ignore rules.

## Outputs

- **What now exists in the user's environment**, one item per agreed gap, each verified once. These
  live outside this package; they are never artifacts of it and are never tracked by it.
- **An entry per executed item** in the local rules file's environment record: what was prepared, its
  resolved location, which capability prepared it and when, and the verification that was run with
  its result and date.
- **An interactive report**: per gap, closed / declined / not possible here, and for the last two
  what that costs — which steps now run SKIPPED or manual, and the instructions to do it by hand,
  quoted from the declaring package's runbook.

## Procedure

1. **Take the goal from the package that declared the gap.**
   For each gap the user chose, read the declaring package's `## Dependencies` row and its runbook,
   and state the goal in that package's own terms — what must become *possible* ("an interpreter that
   can drive a browser"; "a browser build that driver accepts"). Quote it; never sharpen it into a
   particular release, and never invent a goal the package did not state. A requirement whose runbook
   says nothing about what would satisfy it is a documentation gap reported against that package, and
   this capability prepares nothing for it.

   **Where the row carries `Candidate means`, that is the shortlist to offer — nothing more.** The
   field, whose format `skill-conventions` owns, names the *kinds* of thing that would satisfy the
   need, and it exists because a bare abstraction is not something a user can answer. It binds
   nothing: an environment that already satisfies the need by some other means satisfies it, and a
   row with no such field is not defective. Offer the list, add to it from what step 2 finds within
   the boundary, and let the user add whatever they already prefer. Where more than one candidate is
   present, **that is a question, not a choice this capability makes** — `ROLE.md`'s "never guess a
   user value" covers it, and a means picked here would be exactly the kind of guess that later reads
   as the package's requirement.

2. **Establish what this environment offers**, within the boundary in *Rules*: which interpreters and
   package managers answer, whether this session may reach the network, whether an interactive
   desktop session or a display exists, what the user's own policy permits. This step only looks.

3. **Resolve where a prepared thing will live — never assume it.**
   - Propose the **persistent per-installation data location the harness in use provides**, where it
     provides one — the location intended for installed dependencies and environments that must
     survive an update. Where it provides none, propose a location the user names.
   - Where the prepared thing belongs to the user's own project rather than to this installation,
     **always ask**: that project owns its environment, and its layout is not this package's to
     guess.
   - Either way: show the exact location, confirm it, and record it with the item. **Never propose a
     location inside this package.** A location is never derived from something noticed on the
     machine.

   **Why never inside this package.** An installed package is replaced wholesale when it is updated,
   so anything written into it disappears on the next update — silently, and at the worst possible
   moment, because what disappears is the environment a flow was relying on. An install location is
   also not a version-controlled tree, so the ignore rules that used to make writing there safe do
   not exist to be checked. The harness's persistent data location is the one place designed to
   outlive an update, which is why it is the proposal rather than a convenience.

   That location cannot be written down here: it differs per harness, and no portable way to name it
   exists. Determine it as this role determines everything else about the harness in use — from what
   the harness supplies where it supplies it, otherwise by asking — and record the resolved path with
   the item in `## Environment record`, which exists for exactly this.

4. **Choose the means and write the plan.**
   Pick the means from what step 2 established, not from habit: what this environment actually
   offers, what the user is permitted to change, and what can be undone most easily. Where two means
   would both reach the goal, take the one that changes least. Write each item out in the form
   `## Authority` requires, and present the whole plan before anything runs.

5. **Ask item by item, and act only on what was agreed.**
   Run agreed items one at a time, in the order presented. A declined item is recorded as declined,
   its steps are reported SKIPPED/manual, and it is not attempted by another route. If an item
   behaves differently from what it announced — a different location, something else changed as a
   side effect — stop and report before continuing.

6. **Verify each executed item, once and narrowly.**
   One bounded action showing that the thing now answers, as `ROLE.md` defines a verification probe:
   no real CV, vacancy or bank data, no flow, no tool. If the verification fails or cannot be run,
   record the item as created-but-unverified, treat the dependency as still unbound in the report,
   and do not repeat the action.

7. **Record the outcome** in the local rules file's `## Environment record`, merging into what is
   there and clobbering nothing. Only that section counts: a free-text note elsewhere in the file is
   not a record and will not be read as evidence later. Declined items and items that were not
   possible here are recorded too, with their reason, so that a later pass does not silently retry
   them.

8. **Report.** Per gap: what now exists and how it was verified; or that the user declined it; or
   that it cannot be done in this environment and why. For the last two, state the consequence in the
   flows' own terms — which steps run SKIPPED or manual — and hand over the manual instructions from
   the declaring package's runbook.

## Rules

- **The goal comes from the package; the means comes from the environment.** This file deliberately
  carries no command sequence. A fixed recipe would presume a network, a package manager, a shell
  allowed to reach out, and a machine like the author's — presumptions that have each been observed
  to fail. The agent determines the means at preparation time, for the machine in front of it.
- **Nothing is pinned.** The goal is a capability, never a release. Whatever the current toolchain
  resolves to at preparation time is what gets installed, and this package never writes that down
  — not in this file, not in the record, not in a report.
- **Bounded discovery.** This capability, and everything it invokes, looks only where the discovery
  boundary defined in this role's `## Authority` permits.
- **It may conclude "not here".** In a session with no network, in a shell that cannot start what it
  just created, or under a policy that forbids the change, the correct outcome is a recorded gap plus
  the SKIPPED/manual consequence the declaring package states — a success of this capability.
  Retrying by another route, or widening what may be touched "just for this", is the failure.
- **Prepare, never execute**, as `ROLE.md` defines both: the verification of step 6 is not execution,
  and nothing here runs a flow, a tool, or another role's capability.
- **Merge, never clobber.** The record is added to; existing content in the user's file is preserved,
  and changing an existing entry needs confirmation of that specific change.
- **Bindings stay where they belong.** A machine-specific value a package declares stays under that
  package's own subsection in the local rules file; the environment record adds provenance and
  verification, not a second home for bindings.
- **No private path leaves the machine.** Resolved locations belong in the user's local file and in
  the interactive report — never in a file tracked by this repository.

## Failure and skip conditions

| Situation | Behaviour |
|---|---|
| No dependency matrix, and `check-environment` cannot be run | Stop before acting. Report that the gaps are unknown and that guessing which to close is not permitted here. |
| `local_rules_file` does not exist yet | Stop. Point at `bootstrap`, which creates it; there is nowhere to record an outcome until it exists. |
| The user declines every item | Write nothing, report the no-op and which steps run SKIPPED/manual as a result. Not an error. |
| The session cannot reach the network, cannot start what was created, or policy forbids the change | Record the gap with its reason, report SKIPPED/manual with the declaring package's instructions. Not an error, and not retried another way. |
| The toolchains are attached to another project and no location is agreed | Prepare nothing for that item. Report what the owner of that project would need to decide. |
| An item's means turns out to touch a tracked file, a harness configuration file, or a path outside the boundary | Do not offer it; if it is already under way, stop and report. There is no variant of the item that makes this acceptable. |
| A verification fails after the item ran | Record what exists, mark it unverified, treat the dependency as unbound in the report, and leave the item alone. |
| The declaring package states a requirement but no goal that can be acted on | Report a documentation gap against that package. Prepare nothing for it and invent nothing. |
| The recorded location of an earlier entry no longer resolves | Report it as stale, with what no longer resolves. Offer to prepare it again as a new item; never edit the old entry into looking current. |
