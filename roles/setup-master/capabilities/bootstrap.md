# Capability: setup-master.bootstrap

## Purpose

First-run setup. Determines which local rules file the harness in use auto-loads, then creates or
merges that file from the section template kept in the `user-context` contract, so that every flow
finds the user's context simply present at preflight. It closes by triggering `check-environment` and
by **recommending** the next steps — it never runs them.

This is the only capability that may create the local rules file. It is invoked directly by the user,
typically once per environment.

## Inputs

- `user_context_contract` — path to the `user-context` contract file — required. It is the authority
  on what flows need, on the resolution order, and it holds the **section template**, which this file
  deliberately does not duplicate.
- `skills_root` — path to the directory holding this repository's shipped skills — required, to
  enumerate the `validate-cv-*` skills that can be offered for the active set.
- `repo_root` — path to the repository being connected — required, to verify the local rules file is
  ignored by version control.
- `local_rules_file` — path and name of the target file — optional on this capability: when it is not
  given, it is determined with the user in step 1 and confirmed before any write.

## Outputs

- `local_rules_file` — an instance of the `user-context` contract, created or merged. This contract
  carries no envelope: the file is the user's own free-form, harness-native rules file.
- An **interactive report** — what was written per section, what is `planned`, the dependency matrix
  obtained from `check-environment`, and the recommended next steps. Nothing is written to disk
  besides the local rules file.

## Procedure

1. **Identify the harness and its local rules file.**
   Detect if the environment allows it (the harness names itself; a harness configuration directory
   or an existing `*.local.md` file is present in `repo_root`); otherwise **ask** which agent
   application will run these toolchains. From the harness, determine the name, location and format
   of the local rules file it auto-loads — for example `CLAUDE.local.md` at the repository root for
   Claude Code; other harnesses have their own native equivalent. State the resolved file to the
   user and get confirmation before touching it. If the harness cannot be identified, or has no
   auto-loaded local rules file, stop and ask (see *Failure and skip conditions*).

2. **Verify the file is ignored by version control.**
   Check the ignore rules that apply in `repo_root` to the resolved file name. If it is not ignored,
   **stop** and ask the user to add it (the repository ignores `*.local.md`; a harness whose native
   file has a different name needs its own entry). Nothing personal is written into a file that
   could be committed.

3. **Read the section template.**
   Open `user_context_contract` and take the template from its `## Section template` section, and the
   meaning of each section from the sections above it. The template lives there and only there —
   never retype it from memory, and never copy it into this repository's files.

4. **Plan the merge before writing anything.**
   If the file does not exist, the plan is "create with the template sections". If it exists, read it
   and classify every template section:
   - **missing** → will be added;
   - **present and complete** → left as it is; its current values are shown to the user, who may
     choose to revise them;
   - **present but partial or in conflict** with what the user now states → the difference is shown
     and the user decides, item by item.
   Content the role does not own — personal rules, notes, anything else the user keeps in this file —
   is never touched. Present the plan as a short summary and get agreement before the first write.

5. **Fill the sections interactively**, in template order:
   - **Experience sources.** Ask for the sources of the candidate's experience as a free-form list:
     paths, URLs, or plain descriptions, any number, no prescribed kinds. Do not propose a path
     found on the machine as if it were the answer, and do not add sources the user did not name.
     Candidate identity is *not* asked for — it is derived from these sources by the curator. Where
     the environment allows, check each listed source is reachable and readable, and report the ones
     that are not as a warning next to the entry; an unreadable source is recorded, not dropped.
   - **Validation skills (the active set).** Enumerate the `validate-cv-*` skills under
     `skills_root`, reading each one's declared kind (`internal` or `external`) from its `SKILL.md`.
     Present them and let the user choose which to activate — every entry is the user's choice,
     including any ATS validator, and an empty set is legitimate. Record each chosen entry with its
     name and kind. Skills that live outside this repository are not enumerated here; point the user
     at `register-skill` for those. The set holds **optional validators only** — the mandatory
     truthfulness check is a reviewer capability that every CV flow invokes anyway and is never
     listed.
   - **Skill settings.** For each skill that is now recorded, offer only the keys that skill's own
     `SKILL.md` declares, and record only values the user states. Never invent a value, never carry a
     key a skill does not declare. Machine-specific bindings of a skill's external dependencies
     belong in that skill's subsection, never in a shared lump.
   - **Additional rules.** Offer the optional free-text section. If the user has nothing to add,
     leave it with an explicit empty marker rather than a template placeholder.

6. **Mark what is not built yet as `planned`.**
   When the user wants a section entry for something this repository does not ship yet — a flow, a
   validator, a template — record it with a `planned` marker and say plainly in the report that a
   planned entry is inert: no flow will run it until it exists and is registered as active.

7. **Write the file** — create it, or apply the agreed merge. Leave no literal template placeholder
   behind: every `<…>` is either replaced by a real value or the whole line is removed and the
   section carries an explicit "none recorded yet" line. Write nothing else, anywhere.

8. **Trigger `check-environment`** and include its dependency matrix in the report. It is invoked as
   the next step of this same role; its rules live in its own capability file and are not restated
   here. If it cannot run, continue: report the environment as unknown and say how to obtain the
   matrix later.

9. **Report and recommend — do not act.** The report states: the file that was written and where;
   each section with what it now holds; anything marked `planned`; the dependency matrix summary with
   the steps that would run SKIPPED/manual; and the recommended next steps — typically "run the
   knowledge-bank refresh flow before the first CV run". Name the flow and how to invoke it. **Do
   not run it**, even if the user's original request sounded like it included it; ask instead.

## Rules

- **The template is quoted from the contract, never from this file.** If the contract's template
  changes, this capability follows automatically. Section names and their meaning are preserved.
- **Format follows the harness.** If the harness's rules file is not markdown, or nests differently,
  keep the *semantics* and the section names, and express them in the harness's native format.
- **Merge is additive by default.** Adding a missing section needs no confirmation beyond the plan of
  step 4. Changing or removing existing content always needs a specific confirmation of that change.
- **One file, one write.** Repository files, harness configuration and outputs are read-only here.
- **No installation, no binding.** Bootstrap records what the user has; it never installs a tool,
  creates an environment, or changes a machine. Missing dependencies are reported, and the
  instructions come from the declaring skill's own runbook — never invented, never OS-specific.
- **Ask rather than infer.** A plausible default is not an answer. Unknown values stay unrecorded and
  are reported as still needed.
- **Idempotent.** Running bootstrap again on a prepared environment must converge on the same file:
  it re-reads, shows what exists, and changes only what the user asks to change.

## Failure and skip conditions

| Situation | Behaviour |
|---|---|
| Harness cannot be identified | Stop before writing. Ask the user which harness they use, or which file they want to hold the context; a user-chosen file is acceptable if it is auto-loaded or the user accepts pointing flows at it. |
| The target file is not ignored by version control | Stop before writing. Report exactly which ignore entry is missing and ask the user to add it. |
| The file exists and the merge would alter user content | Stop at that item, show the difference, ask. Never resolve a conflict silently. |
| A source, skill or settings key is ambiguous or not found | Record nothing for it. Report it as unresolved with the question that would settle it. |
| `skills_root` holds no `validate-cv-*` skill yet | Write the section with an explicit empty set and note that validators can be added later via `register-skill`. Not an error. |
| `check-environment` cannot run | Write the file, report the environment as unknown, and say how to obtain the matrix later. Bootstrap still succeeds. |
| The user declines to record anything | Write nothing, report the no-op, and state which flows cannot run until the context exists. |
