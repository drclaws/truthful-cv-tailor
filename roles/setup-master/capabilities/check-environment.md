# Capability: setup-master.check-environment

## Purpose

Answers one question: *what will actually run on this machine, and what will not?* It aggregates the
`## Dependencies` sections of the shipped and registered skills — transitively — checks each
dependency, and reports the **dependency matrix**: dependency → status → the skills and steps it
affects. An unbound dependency is not a defect; it means those steps will run SKIPPED or manual, and
the report says exactly which ones.

It reports and writes nothing: no file, no run folder, no installation, no binding.

## Inputs

- `skills_root` — path to the directory holding this repository's shipped skills (workflows and
  tools) — required.
- `local_rules_file` — path to the harness-native local rules file — optional. It supplies the active
  validation set (including skills kept outside this repository, with their locations) and any
  per-skill dependency bindings the user recorded. Without it, only the shipped skills are covered
  and the report says so.
- `scripts/check_environment.py` — this role's bundled probe script, resolved beside `ROLE.md`.

## Outputs

- An **interactive dependency matrix** plus a short verdict per flow. No artifact, no file, no
  change to the local rules file.

## Procedure

1. **Assemble the entity set.**
   - every skill under `skills_root` — workflows and tools alike;
   - every skill recorded in `local_rules_file`, whether it lives in this repository or elsewhere;
     an out-of-repo skill is read at its recorded location.
   Report the set you assembled before the matrix: a reader must be able to see what was covered. If
   a shipped `validate-cv-*` skill is **absent** from the recorded set, warn — it exists but will not
   run until it is registered.

2. **Read each `## Dependencies` section.** Each entry carries exactly these fields:

   | Field | Meaning |
   |---|---|
   | name | what is needed |
   | kind | `capability` — some tool able to perform a stated task; or `tool` — a concrete instrument the implementation genuinely requires |
   | needed for | the task it serves |
   | required \| optional | whether the owning step can proceed without it |
   | when unbound | the declared behaviour, typically: the step runs SKIPPED/manual with instructions |

   An entry with missing or contradictory fields is reported as **malformed** and carried into the
   matrix with status `unknown`. Never repair it by guessing, and never invent an entry that no skill
   declared.

3. **Resolve transitively.** A workflow declares only its *direct* dependencies and inherits the rest
   from what it invokes. Follow its step table: for each step, take the tool skill it invokes and add
   that tool's dependencies to the workflow's effective set; for a step that runs the registered
   validation set, add the dependencies of every skill currently in that set — so the effective set
   is user-specific, and re-reading it after the set changes is the point of re-running this
   capability. Keep the chain (`workflow → step → skill → dependency`) for the *affected* column.
   Rules while walking:
   - visit each entity once; a repeated reference is folded into the same row;
   - a required dependency of an inherited step stays required for the inheriting workflow; a
     dependency inherited only through optional steps stays optional;
   - a step referencing a skill that cannot be found is reported as an **unresolved reference**, not
     silently dropped;
   - **role cards carry no dependencies.** Their `## Tool requirements` are abstract by design; never
     mint a matrix row from one. If a role's abstract need has no corresponding dependency entry in
     any skill that invokes it, report that as a documentation gap.

4. **Check every `tool` entry with the bundled script.** Pass the concrete names — and any minimum
   versions — that you just aggregated, as explicit arguments. The script checks exactly what it is
   told to check: it never reads a `SKILL.md`, a rules file, or any other file to discover work.

   ```text
   check_environment.py --tool <name> --tool <name>@<min-version> --path <location> --json
   ```

   Its statuses: `bound` (found, and any minimum version satisfied), `unbound` (not found),
   `version-mismatch` (found, older than the declared minimum), `version-unknown` (found, but the
   version could not be read while a minimum was required), `unreadable` (a path exists but cannot be
   read). It exits 0 even when everything is missing — a missing tool is a result, not an error. The
   names above are placeholders: this role requires no tool of its own, and every name passed in came
   from a skill's declaration.

5. **Check every `capability` entry without the script.** An abstract capability — browser
   automation, web search, access to a network service — cannot be discovered by looking for a
   binary. In order:
   - if the user recorded a **binding** for it in that skill's settings, take it as the declared
     binding and verify it the way its own kind allows (a bound concrete tool becomes a `tool` probe;
     a bound harness feature becomes a harness probe);
   - otherwise **probe the harness** where the harness allows introspection: is such a facility
     available in this session?
   - otherwise **ask the user** to confirm, and record the answer as *user-confirmed*.
   The report always states **how** each capability status was obtained — probe or user statement —
   because a user statement is weaker evidence and ages differently.

6. **Build the matrix.** One row per distinct dependency:

   | Dependency | Kind | Status | Evidence | Required/optional | Affects (skill → step) | If unbound |
   |---|---|---|---|---|---|---|

   `Evidence` is the resolved location and detected version, or "user-confirmed", or the reason the
   status is unknown. `If unbound` is copied from the declaring entry's *when unbound* field — not
   rewritten.

7. **Report the consequences, in plain words.** After the matrix: which flows are fully runnable as
   things stand; which steps will run SKIPPED or manual and what that means for their output; which
   registered validators will not run; and what could be bound to close each gap — quoting the
   declaring skill's runbook. Never invent an installation procedure and never give OS-specific
   instructions of your own: if the skill's runbook does not say how, report that as a gap in the
   skill.

## Rules

- **Aggregate, never author.** The matrix contains exactly what skills declared, plus statuses. A
  dependency this role thinks would be nice is not a row.
- **Unbound is a status, not a failure.** The capability succeeds with a fully unbound environment;
  the report is then simply a list of what will be skipped.
- **Read-only.** Nothing is installed, bound, configured, downloaded or written — not the local rules
  file either. Changes to the record are made by the capabilities that own it.
- **The script is told, not left to discover.** Every name it probes was aggregated by the agent and
  passed as an argument. If the script cannot be run at all, fall back to asking the user about each
  concrete tool, mark those rows as user-confirmed, and say the probe was unavailable.
- **Version comparison is conservative.** Compare only what was detected against what was declared;
  an unparseable version is `version-unknown`, never a mismatch, and never a pass.
- **Evidence is dated by nature.** State that the matrix describes the machine at the moment it ran,
  and that it should be re-run after the validation set, the settings, or the installed tools change.
- **No private paths leave the report.** Resolved locations belong in the interactive report and in
  the user's local file only, never in a file tracked by this repository.

## Failure and skip conditions

| Situation | Behaviour |
|---|---|
| `skills_root` holds no skills yet | Report an empty matrix and say which entities were looked for. Not an error. |
| `local_rules_file` is absent or has no recorded set | Cover the shipped skills only; state the limitation, and note that a validator not recorded does not run. |
| A registered out-of-repo skill cannot be read | Row per that skill with status `unknown` and the reason; the rest of the matrix is still produced. |
| A `## Dependencies` entry is malformed | Status `unknown`, flagged as malformed, with the field that is missing. Never repaired by guessing. |
| A step references a skill that does not exist | Reported as an unresolved reference against that workflow. |
| The bundled script cannot be executed | Fall back to asking the user per concrete tool; mark those rows user-confirmed and say the probe was unavailable. |
| A version probe hangs or errors | The script reports it as `version-unknown` with the reason and moves on; the matrix is still complete. |
| A capability cannot be probed and the user cannot say | Status `unknown`; treat as unbound in the consequences section and say which steps that would skip. |
