# Capability: setup-master.check-environment

## Purpose

Answers one question: *what will actually run on this machine, and what will not?* It aggregates the
`## Dependencies` sections of the shipped and registered skills — transitively — checks each
dependency, and reports the **dependency matrix**: dependency → status → the evidence that produced
that status → the skills and steps it affects. An unbound dependency is not a defect; it means those
steps will run SKIPPED or manual, and the report says exactly which ones.

It reports and writes nothing: no file, no run folder, no installation, no binding.

**Two runs of this capability on one machine must produce the same matrix.** Everything below that
reads like pedantry — the declared version argument, the declared component check, the named evidence
rung, the derived step — is there for that reason: every place where the auditor would otherwise have
to decide something for itself is a place where two matrices diverge.

## Inputs

- `skills_root` — path to the directory holding this repository's shipped skills (workflows and
  tools) — required.
- `local_rules_file` — path to the harness-native local rules file — optional, and it carries three
  distinct things this capability reads: the **active validation set** (including skills kept outside
  this repository, with their locations), the **per-skill bindings** the user recorded, and the
  **environment record** — dated evidence of what setup already prepared and how it was verified.
  Without it only the shipped skills are covered, nothing is instantiated, and the report says so.
- `user_context_contract` — path to the `user-context` contract file — optional; the authority on
  what the environment record is and is not, when the record has to be interpreted.
- `scripts/check_environment.py` — this role's bundled probe script, resolved beside `ROLE.md`.

## Outputs

- An **interactive dependency matrix** plus a short verdict per flow. No artifact, no file, no
  change to the local rules file.

## Procedure

1. **Assemble the entity set, and keep coverage and instantiation apart.** They are two different
   questions and the matrix answers both:
   - **Covered** — every skill under `skills_root`, workflows and tools alike, *plus* every skill
     recorded in `local_rules_file` wherever it lives; an out-of-repo skill is read at its recorded
     location. Coverage exists so that the user can see what the repository holds, whether or not
     they use it.
   - **Instantiated** — of those, the ones a workflow step will actually run: the tool skills the
     step tables name, and the members of the recorded validation set for the steps that run that
     set. **Registered-set membership decides instantiation and never coverage.**

   A covered skill that is not instantiated still contributes its rows, and their `Affects` cell
   reads *"no step instantiated — skill not in the registered set"*. Such a row is a note, not a gap:
   it can never make a flow unrunnable, and the consequences section says so in those words. Report
   the set you assembled, split into those two groups, before the matrix. If a shipped
   `validate-cv-*` skill is absent from the recorded set, warn — it exists but will not run until it
   is registered.

2. **Read each `## Dependencies` section.** What a declaration must *contain* — the columns, the
   entry kinds, and what each kind states beyond them — is owned by `skill-conventions`. Read it
   there; it is not restated here. This file owns the other half: how a declaration is **probed**,
   and what counts as evidence for the status it gets.

   An entry with missing or contradictory fields is reported as **malformed** and carried into the
   matrix with status `unknown`. Never repair it by guessing, and never invent an entry that no skill
   declared.

3. **Resolve transitively, and derive every step from the workflow's own step table.** A workflow
   declares only its *direct* dependencies and inherits the rest from what it invokes. Walk its step
   table: for each step take the tool skill or the `role.capability` its executor names, and add that
   entity's dependencies to the workflow's effective set. Keep the chain
   `workflow → step → skill → dependency` for the *Affects* column.

   **Where the step comes from, and it is only ever one place.** The step is the **row of the
   workflow's own step table whose executor names that tool skill or that `role.capability`**. A tool
   skill never names a calling step — its *needed for* field names the task the dependency serves, a
   gate or a check item, not a caller — and it must never be asked to: a tool is invocable standalone,
   and making it name a workflow step would couple tools to flows, which the interaction model
   forbids. The workflow knows both halves; the tool knows neither. So the mapping is derived
   **downward from the workflow**, never read upward out of the tool.

   - For a step that runs the **registered validation set**, that single step row is the step, and
     the matrix row names the instance — `<step> (registered set) → <validator>`. One step therefore
     appears against as many rows as the set has members.
   - A dependency that attaches to **no** step of any workflow is an **unattached row**: its
     `Affects` cell says exactly that and names the skill that declared it. Never give a row an
     invented step, and never drop a row for want of one.

   Rules while walking:
   - visit each entity once; a repeated reference is folded into the same row, and that row lists
     every step it affects;
   - a required dependency of an inherited step stays required for the inheriting workflow; a
     dependency inherited only through optional steps stays optional;
   - a step referencing a skill that cannot be found is reported as an **unresolved reference**, not
     silently dropped;
   - **role cards carry no dependencies.** Their `## Tool requirements` are abstract by design; never
     mint a matrix row from one. If a role's abstract need has no corresponding dependency entry in
     any skill that invokes it, report that as a documentation gap.

4. **Establish each row's status from the best evidence available.** The ladder is ordered best
   first, it applies to **every** entry kind, a rung is used only where the rungs above it cannot be
   reached, and **every row names the rung that produced it**.

   1. **Recorded binding.** A value in `local_rules_file`, under the declaring skill's own settings
      subsection, naming the concrete thing that skill will use — then verified the way its kind
      allows. This rung applies to `tool` entries every bit as much as to `capability` ones, and it
      settles the question a bare tool name cannot: **a row is probed against whatever would actually
      run.** Where the skill records an interpreter, an installation or a service for that tool, the
      probe runs *there* and the evidence names which one answered; where it records none, the probe
      runs against the executable search path. Where a recorded binding and a search-path entry both
      exist and differ, **report both**, and say which one the skill would use.
   2. **Direct probe.** The check that kind allows, run now: the bundled script for a `tool` row, the
      declaring skill's own declared check for a `component-set` row (step 5). The strongest evidence
      available for anything discoverable on this machine.
   3. **Harness probe** — and this is what one *is*, because an undefined rung is an invitation to
      invent. A harness probe is an **inspection of the executing session for a named facility**
      (browser automation, web search, file access beyond the shell): ask what the harness in use
      reports about itself, and read the answer. It **never exercises the facility** — no page is
      opened, no search is run, nothing is submitted, no user data is touched; exercising it would be
      execution, which this role does not do. It answers exactly one question — *is this facility
      available in this session, to this agent* — so its result is **session-scoped**, and the
      evidence string says so: what was asked, what answered, and that it holds for this session
      only. Where the harness offers no introspection, this rung is simply **unavailable**: say so
      and fall through to the next one. Never substitute a guess for it.
   4. **Recorded verification.** A dated entry in the local rules file's environment record, written
      by `prepare-environment` or by `register-with-harness`. It counts as `bound` **only while the
      thing it names still resolves at the recorded location**; the moment it does not, the row is
      `unknown — recorded verification is stale`, naming what no longer resolves. It always shows its
      date and the capability that wrote it, and it is **never stronger than a fresh probe**: where a
      rung above can be reached, that rung decides the status and the record is corroboration.
      **There is no expiry period, and none is to be invented** — nothing available here could
      justify a number, and a number would be a pin of a different kind. Free text elsewhere in the
      user's file is **not** a recorded verification, however plainly it says a thing was checked and
      worked: only the sanctioned section is read as evidence, which is why the capability that
      prepares something writes into that section and not into a note.
   5. **Ask the user.** The weakest rung. The answer is recorded as `user-confirmed`, and the report
      states that a user statement is weaker evidence than a probe and ages differently.

5. **Check each kind with what that kind allows.**

   **`tool` — the bundled script.** Pass the concrete names, and any minimum versions, that you
   aggregated, as explicit arguments. The script checks exactly what it is told to check: it never
   reads a `SKILL.md`, a rules file, or any other file to discover work.

   ```text
   check_environment.py --tool <name> --tool <name>@<min-version> --path <location> --json
   ```

   Its statuses: `bound` (found, and any minimum version satisfied), `unbound` (not found),
   `version-mismatch` (found, older than the declared minimum), `version-unknown` (found, but the
   version could not be read while a minimum was required), `unreadable` (a path exists but cannot be
   read). It exits 0 even when everything is missing — a missing tool is a result, not an error. The
   names above are placeholders: this role requires no tool of its own, and every name passed in came
   from a skill's declaration.

   **The version argument is declared, never chosen here.** The script tries a fixed sequence of
   arguments and some tools answer to only one of them — so an auditor free to pick a flag is an
   auditor whose matrix disagrees with the next one's. A tool that does not answer to `--version` has
   the argument it *does* answer to **declared by the skill that needs it**; pass that argument
   through unchanged (`--version-arg <name>=<argument>`). A declared minimum with no working probe is
   `version-unknown` — never a pass, never a mismatch — and is reported as a documentation gap
   against the declaring skill. Trying arguments until one answers is not permitted, even when one
   plainly would.

   **`component-set` — the check the declaring skill states.** A `tool` row names one checkable
   thing. A requirement met by a set of components that are not individually discoverable as
   executables — a package set, a font set, a language pack — is its own row, and the **declaring
   skill states the exact check**, one command per component. Run that check **verbatim, as the skill
   wrote it**, and record its output as the evidence: the row is `bound` only when every component
   answers, and otherwise `unbound`, naming the ones that did not. Running it is not inventing a
   procedure — the skill authored the command, and this capability only runs what it was handed. A
   `component-set` row that declares **no** check is `unknown`, plus a documentation gap reported
   against that skill: never closed by composing a check here, and never quietly folded into the
   neighbouring `tool` row.

   **`capability` — the ladder, without the script.** An abstract capability cannot be found by
   looking for a binary: a recorded binding turns it into whatever probe its own kind allows;
   otherwise the harness probe of rung 3; otherwise the user, recorded as *user-confirmed*.

   **`setting` — recorded, or not recorded.** A settings key the declaring skill marks `required`
   with **no default** is a row of this kind. Its status is `recorded` or `not recorded` and nothing
   else, and the row states only *that* the key is recorded — never its value, which is the user's
   and is sometimes private. Its evidence rung is always rung 1: the local rules file is the only
   place a setting can be recorded, so nothing else can produce this row's status, and the key is
   never asked for here. `If unbound` is the behaviour the skill declares for the key's absence.
   This row kind exists because such a key otherwise has **no moment at which anyone is obliged to
   notice it is missing**: a setup pass would step over it as "not an environment binding", and run
   time cannot reach it until the skill is in the registered set. The row is that moment.
   `register-skill` asks for the key when the skill is registered; this matrix is where the gap stays
   visible until it is answered.

6. **Build the matrix.** One row per distinct dependency:

   | Dependency | Kind | Status | Evidence rung | Evidence | Required/optional | Affects (skill → step) | If unbound |
   |---|---|---|---|---|---|---|---|

   `Evidence rung` names which rung of step 4 produced the status. `Evidence` is what that rung
   actually returned: the resolved location and detected version, the component check's output, what
   the harness answered plus the note that it is session-scoped, the record's date and the capability
   that wrote it, `user-confirmed`, or the reason the status is unknown. `If unbound` is copied from
   the declaring entry's *when unbound* field — not rewritten.

7. **Report the consequences, in plain words.** After the matrix: which flows are fully runnable as
   things stand; which steps will run SKIPPED or manual and what that means for their output; which
   registered validators will not run; and what could be bound to close each gap — quoting the
   declaring skill's runbook. Never invent an installation procedure and never give OS-specific
   instructions of your own: if the skill's runbook does not say how, report that as a gap in the
   skill.

   Say plainly what an uninstantiated row costs, which is nothing: it belongs to a skill that no step
   runs, so it cannot make any flow unrunnable, and it is listed only so the user can see what
   registering that skill would require.

   **Then hand the gaps over.** Sort them in two: the ones `prepare-environment` could close on this
   machine with the user's assent, and the ones that are **structural** — no network in this session,
   no interactive desktop session, a policy that forbids the change, or a documentation gap in the
   declaring skill that has to be fixed before anything can be prepared at all. Name which is which,
   and name `prepare-environment` as where the first group is closed. This capability closes none of
   them itself.

## Rules

- **Aggregate, never author.** The matrix contains exactly what skills declared, plus statuses. A
  dependency this role thinks would be nice is not a row.
- **Unbound is a status, not a failure.** The capability succeeds with a fully unbound environment;
  the report is then simply a list of what will be skipped.
- **Read-only.** Nothing is installed, bound, configured, downloaded or written — not the local rules
  file either. Changes to the record are made by the capabilities that own it.
- **Reading the record is not writing it.** The environment record is evidence here and nothing else:
  a stale entry is reported as stale, never corrected, never refreshed, and never deleted by this
  capability.
- **Bounded discovery.** This capability, and everything it invokes, looks only where the discovery
  boundary defined in this role's `## Authority` permits.
- **The script is told, not left to discover.** Every name it probes was aggregated by the agent and
  passed as an argument. If the script cannot be run at all, fall back to asking the user about each
  concrete tool, mark those rows as user-confirmed, and say the probe was unavailable.
- **Every status names its rung, and no row invents one.** A status with no rung behind it is not
  reported as a status: it is `unknown`, with what was tried and what was unavailable.
- **Version comparison is conservative.** Compare only what was detected against what was declared;
  an unparseable version is `version-unknown`, never a mismatch, and never a pass.
- **Evidence is dated by nature.** State that the matrix describes the machine at the moment it ran,
  and that it should be re-run after the validation set, the settings, or the installed tools change.
- **No private paths and no private values leave the report.** Resolved locations belong in the
  interactive report and in the user's local file only, never in a file tracked by this repository;
  the value behind a `setting` row is never quoted anywhere.

## Failure and skip conditions

| Situation | Behaviour |
|---|---|
| `skills_root` holds no skills yet | Report an empty matrix and say which entities were looked for. Not an error. |
| `local_rules_file` is absent or has no recorded set | Cover the shipped skills only; state the limitation, note that nothing is instantiated, and that a validator not recorded does not run. |
| A registered out-of-repo skill cannot be read | Row per that skill with status `unknown` and the reason; the rest of the matrix is still produced. |
| A `## Dependencies` entry is malformed | Status `unknown`, flagged as malformed, with the field that is missing. Never repaired by guessing. |
| A step references a skill that does not exist | Reported as an unresolved reference against that workflow. |
| A dependency attaches to no step of any workflow | Reported as an **unattached row**, naming the skill that declared it. Never given an invented step, never dropped. |
| The declaring skill is covered but not in the registered set | Rows are produced; `Affects` reads *"no step instantiated — skill not in the registered set"*. A note, not a gap. |
| The bundled script cannot be executed | Fall back to asking the user per concrete tool; mark those rows user-confirmed and say the probe was unavailable. |
| A version probe hangs or errors | The script reports it as `version-unknown` with the reason and moves on; the matrix is still complete. |
| A tool declares a minimum but answers to no argument the skill declared | `version-unknown`, plus a documentation gap against that skill. Never resolved by trying other arguments. |
| A `component-set` row declares no check | Status `unknown`, plus a documentation gap against that skill. Never folded into another row and never checked by an improvised command. |
| The harness offers no introspection | Rung 3 is unavailable for that row: say so and fall through to the next rung. Never guessed. |
| A recorded verification names something that no longer resolves | `unknown — recorded verification is stale`, naming what no longer resolves. Report it; correcting the record belongs to the capability that wrote it. |
| A `setting` row's key is not recorded | Status `not recorded`, with the behaviour the skill declares for its absence. Not an error, and the value is never asked for here — `register-skill` and `update-settings` own that. |
| A capability cannot be probed and the user cannot say | Status `unknown`; treat as unbound in the consequences section and say which steps that would skip. |
