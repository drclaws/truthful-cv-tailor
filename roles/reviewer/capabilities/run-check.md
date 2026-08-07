# Capability: reviewer.run-check

## Purpose

Executes **one registered validator tool's spec** and reports the result as a `validation-report`.

The spec lives in the validator tool skill: it owns the rules of that one check — what it inspects,
which inputs it needs, which measurements it produces, which scripts it ships, how it behaves when
something is unavailable. This capability owns the *execution*: it runs that spec faithfully, under
the reviewer's invariants, and converts the outcome into the uniform report envelope.

The capability is **generic over validators**. It contains no knowledge of any particular check and
must never grow any: everything specific to a check belongs to that check's own spec. Which
validators exist and which of them run is the user's registered validation set, resolved by the
calling flow and passed in — never decided here.

## Inputs

| Parameter | Contract / description | Required |
|---|---|---|
| `check_spec` | path to the registered validator tool's spec (its `SKILL.md`) | required |
| `check_name` | the registered name of the entry being executed, as recorded in the user's validation set | required |
| `check_inputs` | the artifacts the spec declares as its inputs, each passed as an explicit path (the document under review, the rendered deliverable, job-side artifacts, and so on) | required — exactly the set the spec declares |
| `check_settings` | the per-skill settings recorded for this entry in the user's context, if any | optional |
| `report_path` | where to write the report | required |
| `run_manifest` | `run-manifest` — read for the run id and prior gate statuses | required |

A check spec may declare further inputs of its own. The reviewer resolves them from the parameters it
was given; if the spec needs an input the flow did not pass, that is a precondition failure (below),
not something to substitute.

## Outputs

| Parameter | Contract | Status values |
|---|---|---|
| `report_path` | `validation-report` | `pass`, `pass-after-edits`, `fail`, `skipped`, `blocked` |

One report per registered entry, at the path the flow passed. The report names the entry it executed
and the spec version it read, so a reader can tell which rules produced the findings.

A report may additionally be marked **partial**, naming the parts of the spec that did not run and
why — including any item whose subject does not exist yet (see *Rules*). `partial` is a property of
the report, not a sixth status value: the five above are the whole vocabulary, because the calling
flow routes on the status, and a status it does not know is one it cannot route.

## Procedure

1. **Read the spec.** Determine, from the spec alone: what the check inspects, which inputs it
   requires and in which form, which measurements or scores it produces, which scripts it ships and
   with which arguments, what its declared thresholds are (if any), and what it says to do when
   something it needs is unavailable.
2. **Check preconditions.**
   - every input the spec requires was passed and is readable;
   - each input is an instance of the contract the spec expects, at a compatible major version;
   - every dependency the spec declares as *required* is bound in this environment.
   A missing binding ⇒ **SKIPPED** with instructions (see Failure and skip conditions). A missing or
   unreadable input ⇒ **blocked**, reported back to the flow. An input whose subject the flow has not
   produced yet — a rendered deliverable, before the render — is not missing in that sense: the items
   that need it are pending, the rest of the spec runs, and the report says so (see *Rules*).
3. **Execute the spec as written.** Perform exactly the checks it declares — no more, no fewer. Run
   any script it ships, passing values the reviewer resolved as explicit command-line arguments.
   Never invent an additional rule because it seems sensible, and never quietly drop a declared rule
   because it seems awkward.
4. **Treat script output as evidence, not as a verdict.** A script measures; the reviewer judges. A
   script that exits non-zero is a finding to interpret (or a tooling failure to report), never an
   automatic verdict.
5. **Map the outcome into the report envelope.** Findings with severity and the concrete edit each
   requires; the measurements the spec produced, recorded with the spec's own labels; any coverage
   listing the spec produces. Where a spec output has no place in the envelope, record it as a note
   in the report rather than reshaping the envelope.
6. **Derive the verdict** from the findings, using the role's verdict vocabulary. When the spec
   declares a threshold on a measurement, record both the measurement and the spec's threshold rule,
   and let the threshold produce a finding — the verdict still follows from findings.
7. **Write the report** with the common envelope, naming the entry, the spec, and the inputs actually
   consumed.
8. **Propose constraints.** Recurring wording or structure traps this check surfaced belong under
   `## Constraint proposals`; nothing to propose ⇒ `None.`
9. **On a re-run** — after edits, or once a subject that did not exist yet is available: re-execute
   the **whole** spec, not the failed portion or the pending portion only, overwrite the report and
   increment `revision:`.

## Rules

- **The role's invariants outrank the spec.** A spec can never authorize editing the document under
  review, inventing a fact, weakening a truthfulness finding, or overriding the mandatory
  truthfulness check. Where a spec asks for any of that, the invariant wins, the instruction is not
  followed, and the conflict is reported as a finding and escalated.
- **Tool skills are procedures, not actors.** A validator tool defines no agent and holds no
  authority of its own; the executing role's invariants always apply. Shipped and user-added
  validators are identical in rights.
- **Faithful execution.** The spec is the single source of the check's rules. Do not carry a rule
  from another entry's spec into this one, do not reuse a previous run's expectations, and do not let
  a familiar check name imply rules the spec does not state.
- **Measurements are not truth.** Any score the spec produces is a measurement under that spec's
  definition. It is recorded as such, never presented as an independent judgement of the candidate,
  and never allowed to outrank a truthfulness finding.
- **The spec decides what is inspected** — the markdown document, a rendered deliverable, or both.
  The reviewer does not substitute one for the other; a declared subject that should exist by now and
  is absent is a precondition failure. A subject the flow has not produced yet is the separate case
  below.
- **A subject that does not exist yet is not a failure.** A spec may declare items whose subject does
  not exist at this point in the flow — most commonly items inspecting a rendered deliverable, run
  before the render. Report those items as **not applicable at this stage**: not a finding, not a
  failure and not a skip, because the spec did run and the part of it whose subject existed was
  executed. Mark the report **partial**, name which items are pending, and re-run the whole spec once
  the subject exists. The calling flow keeps its gate open until then — a pending item is the reason
  that gate is still open, not a reason to fail it. The two neighbouring states would each say
  something untrue: `blocked` would stop a flow that is proceeding exactly as designed, and `Pass`
  would claim an inspection that has not happened.
- **No membership decisions.** The reviewer never adds an entry the flow did not pass, never drops
  one it did, and never re-orders the registered set.
- **Partial execution is marked.** If part of the spec could not be executed, report which parts ran
  and which did not, and why. A partial result is never presented as a complete one, and a check that
  could not read part of a subject that **should** have been readable cannot return `Pass` — an
  unreadable file is not an inspection. That is the `blocked` and unbound-dependency case above, not
  the case of a subject the flow has not produced yet: an item reported *not applicable at this
  stage* leaves the verdict of the parts that did run standing, and the flow holds the gate instead.
- **Findings are actionable.** Each one names the location in the document, what is wrong under the
  spec, and the edit required. The reviewer does not perform the edit.
- **Isolation.** Only this run's artifacts, the knowledge bank and the repository definitions are
  read. Another run's outputs are never read as precedent.
- **Report, then hand back.** The capability ends with a written report; deciding what happens next
  (edit loop, re-run, escalation) belongs to the flow.

## Failure and skip conditions

- **SKIPPED** — a dependency the spec declares as required is not bound in this environment. Write a
  report with status `skipped` that states: which dependency is missing, which part of the check it
  serves, what the user must do to bind it, and the manual procedure the spec documents, if it
  declares one. A SKIPPED entry is a recorded outcome, never a failure, and never a `Fail` verdict.
- **Blocked** — a required input is missing, unreadable, or written against an incompatible major
  contract version; or the spec itself is missing or unreadable. Report `blocked` with the exact
  gap and stop.
- **Spec/invariant conflict** — do not execute the conflicting instruction; report the conflict and
  escalate to the user through the flow. The rest of the spec still runs if it can run honestly.
- **Tooling failure during execution** (a shipped script crashes, a subject cannot be parsed) — report
  what was attempted, the raw error, and which part of the check is therefore unverified; the verdict
  reflects only what was actually checked.
- `Fail` is a normal outcome: it returns the document to the writer's edit step and does not end the
  flow.
