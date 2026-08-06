# Capability: setup-master.prepare-environment

## Purpose

Closes gaps that `check-environment` reported, by means worked out for the environment that is
actually present, and records what was done so a later check can see it. The dependency matrix says
*what is missing*; the skill that declared it says *what must become possible*; this capability works
out *how*, here, on this machine — and asks before anything changes. It may also conclude that a gap
cannot be closed in this environment: that is a result of the capability, not a failure of it.

Every machine-changing action here is an item of the assented plan defined in this role's
`## Authority`, and no item is offered until it names all five things that section requires of it.

It is invoked by the user, or offered by `bootstrap` once the dependency matrix exists.

## Inputs

- `dependency_matrix` — the matrix `check-environment` produced — required. If none is at hand, run
  `check-environment` first. This capability never re-derives dependencies of its own and never adds
  a requirement no skill declared.
- `gaps` — which of the reported gaps to work on — required, and it is the user's answer. "All of
  them" is a valid answer; "none" ends the capability with a report and no action.
- `local_rules_file` — path to the harness-native local rules file — required. It holds any binding
  the user already recorded, and it receives the environment record.
- `skills_root` — path to the directory holding the shipped skills — required, to read the declaring
  skill's `## Dependencies` entry and its runbook, which are the only source of the goal.
- `repo_root` — path to the repository being connected — required, to tell whether the toolchains
  stand on their own or are attached to another project, and to confirm that anything created inside
  the repository is ignored by version control.
- `user_context_contract` — path to the `user-context` contract file — required when the record
  section does not exist in the local rules file yet: its shape is taken from the contract's section
  template, never invented here.

## Outputs

- **What now exists in the user's environment**, one item per agreed gap, each verified once. These
  live outside this repository; they are never artifacts of it and are never tracked by it.
- **An entry per executed item** in the local rules file's environment record: what was prepared, its
  resolved location, which capability prepared it and when, and the verification that was run with
  its result and date.
- **An interactive report**: per gap, closed / declined / not possible here, and for the last two
  what that costs — which steps now run SKIPPED or manual, and the instructions to do it by hand,
  quoted from the declaring skill's runbook.

## Procedure

1. **Take the goal from the skill that declared the gap.**
   For each gap the user chose, read the declaring skill's `## Dependencies` row and its runbook, and
   state the goal in that skill's own terms — what must become *possible* ("an interpreter that can
   drive a browser"; "a browser build that driver accepts"). Quote it; never sharpen it into a
   particular release, and never invent a goal the skill did not state. A requirement whose runbook
   says nothing about what would satisfy it is a documentation gap reported against that skill, and
   this capability prepares nothing for it.

2. **Establish what this environment offers**, within the boundary in *Rules*: which interpreters and
   package managers answer, whether this session may reach the network, whether an interactive
   desktop session or a display exists, what the user's own policy permits. This step only looks.

3. **Resolve where a prepared thing will live — never assume it.**
   - The repository is used **standalone**: propose `repo_root`, whose ignore rules already cover the
     conventional local-environment directories, so nothing created there can be committed. Propose,
     show the exact location, and confirm.
   - The toolchains are **attached to another project**: **always ask**. That project owns its
     environment and its layout is not this repository's to guess.
   - Either way the resolved location is recorded with the item. A location is never derived from
     something noticed on the machine.

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
   no real CV, vacancy or bank data, no flow, no tool skill. If the verification fails or cannot be
   run, record the item as created-but-unverified, treat the dependency as still unbound in the
   report, and do not repeat the action.

7. **Record the outcome** in the local rules file's `## Environment record`, merging into what is
   there and clobbering nothing. Only that section counts: a free-text note elsewhere in the file is
   not a record and will not be read as evidence later. Declined items and items that were not
   possible here are recorded too, with their reason, so that a later pass does not silently retry
   them.

8. **Report.** Per gap: what now exists and how it was verified; or that the user declined it; or
   that it cannot be done in this environment and why. For the last two, state the consequence in the
   flows' own terms — which steps run SKIPPED or manual — and hand over the manual instructions from
   the declaring skill's runbook.

## Rules

- **The goal comes from the skill; the means comes from the environment.** This file deliberately
  carries no command sequence. A fixed recipe would presume a network, a package manager, a shell
  allowed to reach out, and a machine like the author's — presumptions that have each been observed
  to fail. The agent determines the means at preparation time, for the machine in front of it.
- **Nothing is pinned.** The goal is a capability, never a release. Whatever the current toolchain
  resolves to at preparation time is what gets installed, and this repository never writes that down
  — not in this file, not in the record, not in a report.
- **Bounded discovery.** This capability, and everything it invokes, looks only where the discovery
  boundary defined in this role's `## Authority` permits.
- **It may conclude "not here".** In a session with no network, in a shell that cannot start what it
  just created, or under a policy that forbids the change, the correct outcome is a recorded gap plus
  the SKIPPED/manual consequence the declaring skill states — a success of this capability. Retrying
  by another route, or widening what may be touched "just for this", is the failure.
- **Prepare, never execute**, as `ROLE.md` defines both: the verification of step 6 is not execution,
  and nothing here runs a flow, a tool skill, or another role's capability.
- **Merge, never clobber.** The record is added to; existing content in the user's file is preserved,
  and changing an existing entry needs confirmation of that specific change.
- **Bindings stay where they belong.** A machine-specific value a skill declares stays under that
  skill's own subsection in the local rules file; the environment record adds provenance and
  verification, not a second home for bindings.
- **No private path leaves the machine.** Resolved locations belong in the user's local file and in
  the interactive report — never in a file tracked by this repository.

## Failure and skip conditions

| Situation | Behaviour |
|---|---|
| No dependency matrix, and `check-environment` cannot be run | Stop before acting. Report that the gaps are unknown and that guessing which to close is not permitted here. |
| `local_rules_file` does not exist yet | Stop. Point at `bootstrap`, which creates it; there is nowhere to record an outcome until it exists. |
| The user declines every item | Write nothing, report the no-op and which steps run SKIPPED/manual as a result. Not an error. |
| The session cannot reach the network, cannot start what was created, or policy forbids the change | Record the gap with its reason, report SKIPPED/manual with the declaring skill's instructions. Not an error, and not retried another way. |
| The toolchains are attached to another project and no location is agreed | Prepare nothing for that item. Report what the owner of that project would need to decide. |
| An item's means turns out to touch a tracked file, a harness configuration file, or a path outside the boundary | Do not offer it; if it is already under way, stop and report. There is no variant of the item that makes this acceptable. |
| A verification fails after the item ran | Record what exists, mark it unverified, treat the dependency as unbound in the report, and leave the item alone. |
| The declaring skill states a requirement but no goal that can be acted on | Report a documentation gap against that skill. Prepare nothing for it and invent nothing. |
| The recorded location of an earlier entry no longer resolves | Report it as stale, with what no longer resolves. Offer to prepare it again as a new item; never edit the old entry into looking current. |
