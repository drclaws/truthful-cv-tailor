---
name: connect-environment
description: Connects this package to a machine and to one project, and says what will actually run there — it settles the harness-native local rules file that holds the user's own context, records the experience sources, checks and settings only a person can supply, reports a dependency matrix giving every declared need a status and naming the steps it costs, and, only on the user's assent and item by item, closes the gaps it can and makes the public skills reachable by name. Reach for it when a request sounds like set this up, connect these toolchains to my project, what will run on this machine, I just installed or updated this, that step keeps coming out skipped, change my experience sources, or register another validator — the first connection and every later update pass are one and the same pass. It prepares and never executes; it builds no knowledge bank and writes no CV, which are refresh-knowledge-bank and generate-targeted-cv, and a gap it may not close itself — read access to these files, or a harness that keeps registration only inside its own configuration file — it reports with the manual step rather than working around it.
---

# Workflow: connect-environment

Flow version: 1.0

## Purpose

The front door to setup. One pass answers three questions — **what does this package need from you**,
**what will actually run on this machine**, and **what will not** — and then, only on the user's
assent and item by item, closes what can be closed.

It orchestrates one role, `setup-master`, and adds what no role may do for itself: resolving where
this package sits on this machine, confirming that a session can read it, ordering the capabilities,
holding the gates between them, and composing the closing report.

**This flow holds no rule of its own.** Every rule it applies belongs to a `setup-master` capability,
and this file names the owner instead of repeating it. That is not tidiness. The two rules that
matter most here — what a machine-changing item must name before it is offered, and where this role
may look at all — are the ones that role exists to protect, and a rule with two homes ages at two
rates. The copy an agent happens to read is the one it obeys, so there is one copy.

What this pass deliberately does not do: it runs no workflow and no tool, because `setup-master`
prepares rather than executes; it produces no artifact on disk; and it grants itself no access it was
not given. Everything it does that changes the machine at all goes through the assent rule in
`setup-master`'s `## Authority`, unchanged and uncopied.

## When to run

Run this flow when:

- these toolchains have not been connected to this project yet;
- the package was installed or updated, and what it declares may have changed;
- a recorded value has to change — an experience source, a per-package setting, a check;
- you want to know what runs here as things stand, rather than letting a run find out for you;
- a gap an earlier pass reported is worth closing now;
- the public skills should be discoverable in the harness in use.

**The first pass and every later one have the same shape.** Bringing a connected environment forward
is not a separate mode with a separate entry point; `setup-master.bootstrap` states why the two are
one capability rather than two, and this flow has one shape for the same reason. What a later pass
adds is a comparison against what the last one recorded, which step 8 reports.

**It happens because someone asked for it.** Nothing here arranges to run itself later. A pass that
changed a machine nobody was watching would be precisely the surprise the assent rule exists to
prevent, so this stays something a user invokes.

## What this pass writes

There is no run identifier, no run directory and no artifact: setup's reports are interactive, and
`setup-master` records that about itself. Two things may change, and both are the user's own:

- **the local rules file** — created or merged at step 3, and the only file this pass writes on its
  own initiative;
- **whatever an assented item creates** at steps 6 and 7, outside this package, at a location the
  user confirmed — with its provenance in that file's `## Environment record` and
  `## Harness registration` sections, whose shape contract `user-context` owns.

This flow needs no output root, because it produces nothing to put in one. This package is read-only
to it, as `engine-conventions` requires of everything that runs here.

## Inputs

Three rows, and each is a question this pass asks rather than a value it assumes. An index, not a
second home for rules.

| Input | Contract / description | Required |
|---|---|---|
| `request` | What this pass is for: a first connection, a recorded value to change, a check to register, an environment report, a gap to close, or discoverability in the harness. It is what selects between `setup-master`'s capabilities. | required |
| `project_root` | The user's working project, or none. *None* is an answer rather than a missing value: it decides where step 1's ignore question is asked, and where an assented item may write. | required |
| `local_rules_file` | The harness-native file that holds the user's context. Normally not supplied: step 1 determines it with the user and confirms it before anything is written. | optional |

**`package_root` is not an input.** It is resolved at step 0 by the arithmetic that step states, and
passed explicitly to every capability a step invokes. Where the contracts, the roles, the tools and
the public skills sit inside this package is fixed, so it is not a thing a user has an answer to: the
package describes itself, and the one value that genuinely differs between machines is the one the
harness already supplies. Asking for the rest would be configuration for something this package
knows already.

Nothing here is defaulted. An input that did not resolve is a question to the user.

## Steps

`executor` is the `role.capability` that runs the step, or `flow` for orchestration this flow does
itself. Every path a capability receives is passed to it explicitly.

| # | Step | Executor | Passed | Gate |
|---|---|---|---|---|
| 0 | Resolve this package's root, then load `engine-conventions` | `flow` | — | G0 |
| 1 | Identify the harness, the local rules file it auto-loads, and the project | `setup-master.bootstrap` (its steps 1–2) | `package_root`, `project_root`, `local_rules_file` where supplied | G1 |
| 2 | Confirm this package's own files are readable from a working session | `flow` | the root resolved at step 0 | G2 |
| 3 | Ask for what only the user can supply, and write it | `setup-master.bootstrap` (its steps 3–7) | `package_root`, `project_root`, `local_rules_file`, `request` | G3 |
| 4 | Aggregate the declared dependencies and probe them | `setup-master.check-environment` | `package_root`, `local_rules_file` | G4 |
| 5 | Choose how each gap should be closed, with the user | `flow` + `setup-master.prepare-environment` | the matrix of step 4, `package_root` | G5 |
| 6 | Close the assented gaps, verify each, record | `setup-master.prepare-environment` | the matrix, the chosen `gaps`, `local_rules_file`, `package_root`, `project_root` | G6 |
| 7 | Make the harness load this package, where that is not already true | `setup-master.register-with-harness` | `package_root`, `project_root`, `local_rules_file`, `request` | G7 |
| 8 | Report: what runs, what is SKIPPED or manual, what to do next | `flow` | — | — |

Steps run in order, and this flow declares no parallel groups: each step's question depends on the
previous step's answer, and there is one conversation with one user.

**A narrower request runs the subset that serves it.** The nine rows are the shape of a first
connection and of an update pass. Where the request concerns one recorded value, the capability that
owns it does the work — `setup-master.update-settings` for a value already recorded,
`setup-master.register-skill` for a check to activate — with steps 0 and 1 before it and step 8
after, and the steps that do not apply reported as not attempted rather than quietly dropped.

### 0. Resolve this package's root, then load the engine's conventions

This file was presented from `<package root>/skills/connect-environment/`. The package root is two
levels above that directory; resolve it to an absolute path from the location the harness supplied
with this file. Then read `engine-conventions` — the invariants, the reference grammar, the anchor
rule, the loading rule and the rule about where a run writes — from the contracts directory at that
root, before doing anything else. If the location was not supplied, or the file cannot be read, do
not proceed: report which of the two happened, and ask.

Every public skill of this package carries that paragraph, and the duplication is deliberate: an
entry point cannot read the engine's conventions to learn how to find the engine's conventions, so
something has to anchor the scheme. The rule itself — where the base comes from, why the absolute
result is what gets read, what a refusal to read it means, and what to do when no base was supplied —
lives once, in `engine-conventions`, and this step never becomes a second copy of it. Do not tidy the
step away as a duplicate.

The resolved root is what every capability below is handed: `setup-master` takes it as a parameter
and defaults nothing from layout, so a root this step could not establish is a pass that cannot
start.

### 1. Identify the harness, the local rules file, and the project

Hand `setup-master.bootstrap` the resolved root, the project — or the answer *none* — and
`local_rules_file` where the user supplied one. Its first two steps determine the harness in use;
the name, location and format of the local rules file it auto-loads; the confirmation of that file
with the user; and whether it is ignored by version control. Those rules are that capability's, and
this flow adds nothing to them.

**G1** is the file being settled and the ignore question answered, including in the case where there
is no project — an answer bootstrap has its own handling for. Where the harness cannot be identified,
or the file is not ignored, bootstrap stops and asks; that is a stop of this flow too, and step 3
does not begin until the question is answered.

### 2. Confirm this package's own files are readable from a working session

Read one known file of this package back through the root resolved at step 0: **the contracts
index**, the file that maps each contract name to its location. It is small, every copy of this
package has it, and it carries nothing personal.

**Why this is a step of its own, when step 0 already read a file.** The two reads answer different
questions. Step 0 needs one document in order to proceed at all, and a failure there stops the pass
where it stands. This step asks whether a *run* — later, in a session nobody is watching — will be
able to open the files its steps need, and it establishes at the same time that the root resolved at
step 0 is this package rather than some other tree that happens to sit two levels up. An installed
package sits outside the location a session was started in, and reading outside that location can be
permitted separately from everything else a session may do. A pass that did not ask would leave every
future run to discover that one file at a time.

**It reads** → the fact becomes a dated verification: what was read, through which resolved root, and
on what date. This flow does not write that down itself — contract `user-context` names the writers
of the `## Environment record`, and step 6 is where this pass's entries are made. Once it is there,
it is the evidence `setup-master.check-environment` reads at its fourth rung, on that capability's
own terms about what such evidence is worth.

**It is refused** → this is a gap, and this flow does not close it. Report, in the user's own terms:
the exact path that was refused, that the flows cannot run until a session may read these files, and
the one manual step — *grant this session read access to these files, by whatever means your setup
offers*. Record the outcome so that a later pass does not retry it in silence; where the local rules
file does not exist yet, the report is the only record there can be, and it says so. Then stop.
Step 3 reads the section template out of contract `user-context`, and steps 4 and 7 enumerate this
package's own files, so none of them can proceed: name the steps that were therefore not attempted.

**Granting that access is not this flow's to do**, and `setup-master`'s `## Authority` is where the
reason lives: read access is either the harness's own configuration or the user's permission state,
and that role is barred from touching either. So reporting it plainly is the correct outcome of this
step rather than a degraded one — the same shape `setup-master.register-with-harness` has for a
registration that cannot complete.

### 3. Ask for what only the user can supply, and write it

Hand bootstrap the same root, the project, the confirmed file and the request. Its steps 3 to 7 read
the section template out of contract `user-context`, plan the merge against whatever the file already
holds, fill the sections with what the user states, mark as `planned` anything this package does not
ship yet, and write. The experience sources, the active validation set, the per-package settings and
the additional rules are the four things no probe can discover — which is why this step is a
conversation rather than a scan.

**G3** is the file holding what the user stated, with a section they had nothing for left explicitly
empty rather than carrying a template placeholder, as bootstrap's own write step requires.

**Where this flow takes over from bootstrap.** That capability closes by triggering
`check-environment` and by offering the two capabilities that can act on the matrix. This flow makes
those its own steps 4 to 7, so that the gate between seeing the matrix and acting on it sits in one
table with the rest, and so that step 2's outcome is in front of the user when the choosing of step 5
happens. Nothing about the capabilities changes; what changes is who holds the gate.

### 4. Aggregate the declared dependencies and probe them

`setup-master.check-environment`, with the resolved root and the local rules file. It covers this
package's public skills and tools plus every check the user recorded, resolves what a flow's steps
inherit, settles each row by the best evidence rung it can reach, and reports the matrix with the
consequences per flow.

**G4** is a matrix in which every row carries a status and the rung that produced it — or, where the
capability could not run at all, a report saying so and how to obtain the matrix later, which
bootstrap's own failure table treats as a setup that still succeeded.

Where the local rules file already carried an environment record, the comparison against it is what
step 8 reports as the change list: what is newly bound, what the record claims that no longer
resolves, and what a package now declares that nothing declared last time.

### 5. Choose how each gap should be closed, with the user

The matrix says what is missing. This step is where the user is helped to *choose*, because a
`capability` row names an abstraction and an abstraction is not something anyone can answer. Per gap,
put three lists and one question in front of them:

1. **What this machine already offers that would satisfy it** — found only within the discovery
   boundary `setup-master`'s `## Authority` defines. That boundary is why this list is short, and it
   is not widened here to make it longer.
2. **The declared candidate kinds that are not present** — from the row's `Candidate means`, the
   optional field whose format `skill-conventions` owns — each with what obtaining it would take in
   *this* environment, worked out at that moment rather than read out of a file.
3. **Something else you name.** The user may already prefer something this package has not heard of.
   Recording that preference is a setting, not an installation.

Then the question, in the user's own words: *which of these do you want to use, and may I set it up?*
The answer becomes an item of the plan `setup-master.prepare-environment` writes — naming the five
things `## Authority` requires of an item before it may be offered at all — or a recorded decline.
Both are outcomes. A decline costs exactly what the matrix already said it costs, and this flow
reports that instead of asking again.

**G5** is a plan the user assented to item by item, or a recorded decline per gap.

### 6. Close the assented gaps, verify each, record

`setup-master.prepare-environment`, with the matrix, the gaps the user chose, the local rules file,
the resolved root and the project. It takes the goal from the package that declared the gap, works
the means out for the machine in front of it, resolves where a prepared thing will live, runs the
agreed items one at a time, verifies each within its own bounds, and records what happened.

**G6** is every agreed item having an outcome on the record: closed and verified; closed but
unverified, and therefore still counted unbound; declined; or not possible in this environment, with
the reason. That last one is a result of the capability rather than a failure of it, and the report
states what it costs in the flows' own terms — which steps now run SKIPPED or manual.

This is also where step 2's outcome is written down, whichever way it went: the dated verification
that this package is readable through the resolved root, or the gap with its manual step, so that the
next pass starts from what this one established.

### 7. Make the harness load this package, where that is not already true

`setup-master.register-with-harness`, with the resolved root, the project, the local rules file and
the request — register, reconcile, or remove an earlier registration. It establishes what the harness
in use offers, chooses among the mechanisms those facts allow, and creates only what the user
assented to. Installing the package is itself what registers it wherever the harness can install one,
so on many machines this step reconciles what is already there rather than creating anything.

**G7** is an outcome on the record either way: what the harness will now load and from where, or a
registration that cannot complete — the case where the harness holds this kind of thing only inside a
configuration file the user owns, which that capability treats as a correct outcome with the manual
steps attached. In both cases the report states how these files can be reached meanwhile.

### 8. Report: what runs, what is SKIPPED or manual, what to do next

The body of the report is the one bootstrap composes at its own closing step: what was written and
where, section by section; the matrix, with the steps that would run SKIPPED or manual; the change
list against the environment record; the sentence that says plainly when nothing needs doing; and one
line per bound-but-degraded row saying what closing it would save. This flow adds only what only it
knows:

- **the resolved package root**, so the user can tell which copy of these files this pass obeyed;
- **the outcome of step 2** — first in the report where it was a refusal, because nothing else in it
  matters until a session may read these files;
- **what steps 6 and 7 did, what was declined, and what could not be done**, each with its
  consequence;
- **the next thing to invoke, by name**: the knowledge bank has to exist before the first CV run, so
  `refresh-knowledge-bank` comes before `generate-targeted-cv`. Name it and stop there — this flow
  recommends, and running it is the user's next act, which is `setup-master`'s own boundary.

Where the harness in use asks the user rather than refusing outright, the honest sentence to include
is that the first time a run opens these files the user will be asked to allow it, and that approving
it once is what makes the flows work. It belongs in this report rather than in a rule, because it
describes how one harness behaves rather than what this package requires.

## Gates

The gate numbers match the step they close. There is no run manifest to evidence them in — setup's
reports are interactive — so each gate is evidenced by the report and, where the outcome is durable,
by the section of the user's own file that holds it.

| Gate | Requires | Evidenced by |
|---|---|---|
| G0 root resolved | The package root resolved to an absolute path from the location supplied with this file, and `engine-conventions` read from it. | the report, which names the resolved root |
| G1 file settled | The harness identified, the local rules file named and confirmed with the user, and the ignore question answered. | bootstrap's report |
| G2 package readable | The contracts index read back through the resolved root and carried to step 6 as a dated verification; or the gap named with the path and the manual step, and the pass stopped. | the report; `## Environment record` |
| G3 context recorded | Every template section either filled with what the user stated or explicitly empty, with nothing invented and nothing left as a placeholder. | `local_rules_file` |
| G4 matrix produced | A status and an evidence rung on every row, plus the per-flow consequences; or a statement that the matrix could not be obtained and how to get it later. | the report |
| G5 plan assented | Per gap: an item the user agreed to, naming the five things `## Authority` requires, or a recorded decline. | the report |
| G6 items closed | Every agreed item verified, or recorded unverified and counted unbound; declined and not-possible items recorded with their reason. | `## Environment record` |
| G7 registration decided | What the harness will now load recorded; or recorded as unable to complete, with the manual steps. | `## Harness registration` |

## Definition of done

- The package root was resolved, and the report names it.
- The local rules file is settled with the user, ignored by version control, and holds what the user
  stated — anything they had no value for left explicitly empty.
- Step 2's outcome is recorded: a dated verification, or the gap with the path and the manual step.
- The dependency matrix exists, or the report says why it could not be obtained and how to get it.
- Every gap the user chose has an outcome — closed and verified, closed unverified, declined, or not
  possible here — each with its consequence stated in the flows' own terms.
- Registration is recorded, or recorded as unable to complete with the manual steps, and either way
  the report says how these files can be reached meanwhile.
- The closing report names what runs, what runs SKIPPED or manual, the change list where there was a
  record to compare against, and the next flow to invoke — and says in one sentence when nothing
  needs doing.
- Everything that changed on this machine is an item the user assented to in this session and is on
  the record. Anything else is a defect of the pass, whatever else it accomplished.

## Escalation

Stop and ask the user in the situations `setup-master`'s own `## Escalation` lists — both halves of
it: what stops a pass before it acts, and what stops an action already under way. That list is the
role's, and this flow keeps no copy of it; it is read from the role card at the step whose executor
names the capability concerned.

Two escalations are this flow's own, because they belong to the two steps no capability executes:

- **the root could not be resolved** — the location this file was presented from was not supplied, or
  `engine-conventions` could not be read at the root computed from it. Stop at step 0, report which
  of the two happened, and ask for the one thing that would settle it. The anchor rule in
  `engine-conventions` states that outcome; step 0 is where this flow meets it.
- **this package could not be read through the resolved root** — stop at step 2, name the path that
  was refused and the manual step that would grant access, and say which of the later steps were
  therefore not attempted. There is no arrangement of this pass that reads a file the session may not
  read, so there is nothing else to try.

## Usage

`setup-master.register-with-harness` makes this package's public skills discoverable by the harness
in use. **Where registration succeeded, the flow is invoked by name:**

> run `connect-environment`

**By-path invocation is valid wherever the user has these files at a path they can name** — which is
the case when this engine is cloned. Point the agent at this file, whose location the skills index
gives for the name `connect-environment`. Once this engine is installed as a package, the public
skills are invocable by name and that is the supported route: an installed package sits at a location
the user never chose and that moves whenever the package is updated, so a path to it is not a thing
to hand out.

A typical invocation, in the user's own words:

```text
Connect these toolchains to this project.
```

and, on a machine that is already connected:

```text
Check what will run here, and close the gaps you can.
```

**This is also the update pass.** Running it again against the same project converges on what is
already there — bootstrap's idempotence rule — so there is no separate update entry point to choose
between. A package is installed once for the user and is then present in every project, while the
local rules file belongs to one project: connecting a second project is a second pass, and
deliberately an explicit act.

The order for a machine that has never run any of this: `connect-environment`, then
`refresh-knowledge-bank` so that a knowledge bank exists, then `generate-targeted-cv` per vacancy.

However this flow was reached, the executing agent reads this file. What each step's executor may
open is the loading rule in `engine-conventions`, and this flow keeps no copy of that either: a rule
with several homes ages at different rates, and the copy an agent happens to read is the one it
obeys.

## User-context settings

**This skill recognizes no per-skill settings keys**, so this section carries no key table — the
shape `skill-conventions` prescribes for a skill with nothing to declare. A `### connect-environment`
subsection under `## Skill settings` in the user's local rules file has no meaning; report it as
unrecognized rather than interpreting it.

The table below is **not** a key declaration, and it is not a reading list either — this flow reads
no section of contract `user-context` for its own use. It indexes which section each step touches,
through the capability that owns that section.

| Item | Contract section | Which step touches it, and how |
|---|---|---|
| Canonical experience sources | `## Experience sources (canonical)` | Step 3 — asked for and recorded by `bootstrap`. It is the one input the bank refresh later runs on. |
| The active validation set | `## Validation skills` | Step 3 — offered from the tools this package ships. A check the user keeps elsewhere is added by `setup-master.register-skill`, which is where that step points them. |
| Per-package settings | `## Skill settings` | Step 3, and step 5 where the means a user names is a recorded preference rather than something to install. |
| Additional rules | `## Additional rules` | Step 3 — offered as free text the flows honour. |
| Environment record | `## Environment record` | Written at step 6, including step 2's outcome; read at step 4 as dated evidence. |
| Harness registration | `## Harness registration` | Written at step 7. |

## Dependencies

Direct needs of the flow itself, and there are two. Everything else this pass depends on belongs to
the capabilities its steps invoke and to the packages whose declarations they read;
`setup-master.check-environment` resolves that transitively at step 4.

| Name | Kind | Needed for | Required / optional | When unbound |
|---|---|---|---|---|
| Interactive dialogue with the user | capability | Every step here is a question before it is an action: which harness and which file, what the user's sources and checks are, which gap to close and by what means, and the assent each item of steps 6 and 7 needs before it may run. | required | Nothing here can happen. Report that setup needs a channel to ask on, and stop before writing anything: a pass that answered its own questions would be recording guesses as the user's context. |
| Reading this package's own files from a working session | capability | Step 0 reads `engine-conventions`; step 2 reads the contracts index back through the resolved root; steps 3, 4 and 7 read contract `user-context`, the `## Dependencies` sections of this package's skills and tools, and the public skills themselves. This package may sit outside the location the session was started in, and reading outside that location can be permitted separately. | required | Step 2 names the gap, the exact path and the one manual step, and the pass stops there with the steps it did not attempt listed. Granting the access is the user's to do; `setup-master`'s `## Authority` is why it is not this flow's. |

Both rows enter the same matrix step 4 produces — this flow is covered by the check it runs — so an
unbound row of its own is also the reason the report will give for a pass that ended early.
