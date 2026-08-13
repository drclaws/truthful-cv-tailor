# Capability: setup-master.bootstrap

## Purpose

First-run setup. Determines which local rules file the harness in use auto-loads, then creates or
merges that file from the section template kept in the `user-context` contract, so that every flow
finds the user's context simply present at preflight. It closes by triggering `check-environment`, by
**offering** the two capabilities that can act on what the matrix showed, and by **recommending** the
flows to run next — which it never runs itself.

One setup pass should be able to close setup. Bootstrap therefore offers, but bootstrap itself
changes nothing on the machine beyond the file below: what it offers is carried out by the capability
that owns it, and only on what the user agreed to.

This is the only capability that may create the local rules file. It is invoked directly by the user,
typically once per environment.

## Inputs

- `package_root` — the resolved root of this package — required. Two things inside it are read:
  contract `user-context`, the authority on what flows need and on the resolution order, and the home
  of the **section template**, which this file deliberately does not duplicate; and the tools
  directory, to enumerate the `validate-cv-*` tools that can be offered for the active set.
- `project_root` — the user's working project, or none — required as an answer even when the answer
  is *none*, to verify the local rules file is ignored by version control.
- `local_rules_file` — path and name of the target file — optional on this capability: when it is not
  given, it is determined with the user in step 1 and confirmed before any write.

## Outputs

- `local_rules_file` — an instance of the `user-context` contract, created or merged. This contract
  carries no envelope: the file is the user's own free-form, harness-native rules file.
- An **interactive report** — what was written per section, what is `planned`, the dependency matrix
  obtained from `check-environment`, what was offered and what the user decided about it, and the
  recommended next steps. Bootstrap writes nothing to disk besides the local rules file; anything an
  accepted offer creates is written by the capability that owns it and recorded by that capability.

## Procedure

1. **Identify the harness and its local rules file.**
   Detect if the environment allows it (the harness names itself; a harness configuration directory
   or an existing `*.local.md` file is present in `repo_root`); otherwise **ask** which agent
   application will run these toolchains. From the harness, determine the name, location and format
   of the local rules file it auto-loads — from the harness's own documentation where the session can
   read it, otherwise by asking the user. Every harness has its own; this repository names none of
   them and assumes none. State the resolved file to the user and get confirmation before touching
   it. If the harness cannot be identified, or has no auto-loaded local rules file, stop and ask
   (see *Failure and skip conditions*).

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
   - **Toolchain directories.** Record where the contracts, the roles and the skills of the
     repository being connected live, so that a name used in the rules can later be resolved to a
     file. `skills_root` is one of the three; **propose** the other two from what stands beside it in
     `repo_root`, show the exact locations, and record only what the user confirms — a proposal the
     user does not confirm is not recorded. Do not list what those directories hold: each carries its
     own index, and this section records locations, not a catalogue.

6. **Mark what is not built yet as `planned`.**
   When the user wants a section entry for something this repository does not ship yet — a flow, a
   validator, a template — record it with a `planned` marker and say plainly in the report that a
   planned entry is inert: no flow will run it until it exists and is registered as active.

7. **Write the file** — create it, or apply the agreed merge. Leave no literal template placeholder
   behind: every `<…>` is either replaced by a real value or the whole line is removed and the
   section carries an explicit "none recorded yet" line. Write nothing else, anywhere — bootstrap's
   own writing ends here.

8. **Trigger `check-environment`** and include its dependency matrix in the report. It is invoked as
   the next step of this same role; its rules live in its own capability file and are not restated
   here. If it cannot run, continue: report the environment as unknown and say how to obtain the
   matrix later.

9. **Offer what can act on the matrix — and change nothing until the user agrees.** Two offers, both
   optional, both refusable, each carried out by the capability that owns it:
   - `prepare-environment`, for the gaps the matrix reported. The user chooses which gaps, if any;
     the goal of each comes from the skill that declared it and the means from this environment.
   - `register-with-harness`, to make the shipped skills and roles discoverable in the harness
     identified in step 1.

   Present each offer as the plan its own capability writes, hand over to that capability, and let it
   act only on the items the user agreed to. Bootstrap performs neither itself. Declining one or both
   is a **normal outcome**, not a broken setup: record what was declined, and report what runs
   SKIPPED/manual and what still works meanwhile — invoking a flow by path is valid regardless of
   registration.

10. **Report and recommend the rest — do not run it.** The report states: the file that was written
    and where; each section with what it now holds; anything marked `planned`; the dependency matrix
    summary with the steps that would run SKIPPED/manual; what was offered and what the user decided;
    and the recommended next steps — typically "run the knowledge-bank refresh flow before the first
    CV run". Name the flow and how to invoke it. **Do not run it**, even if the user's original
    request sounded like it included it; ask instead.

## Rules

- **The template is quoted from the contract, never from this file.** If the contract's template
  changes, this capability follows automatically. Section names and their meaning are preserved.
- **Format follows the harness.** If the harness's rules file is not markdown, or nests differently,
  keep the *semantics* and the section names, and express them in the harness's native format.
- **Merge is additive by default.** Adding a missing section needs no confirmation beyond the plan of
  step 4. Changing or removing existing content always needs a specific confirmation of that change.
- **One file, one write.** `local_rules_file` is the only file bootstrap writes. Repository files,
  harness configuration and outputs are read-only here.
- **Nothing changes unasked.** Bootstrap records what the user has and changes nothing on the machine
  on its own initiative. What it offers in step 9 runs as an item of the assented plan defined in
  `ROLE.md`'s `## Authority`, carried out by the capability that owns it. A gap nobody closes is
  reported, with instructions from the declaring skill's own runbook — never invented, never
  OS-specific.
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
| The user declines an offered item, or both offers entirely | Record it as declined, report which steps run SKIPPED/manual and that invocation by path still works. Do not offer it again in the same pass, and do not reach the same end by another route. Setup succeeded. |
| A gap cannot be closed in this environment — no network, a shell that may not reach out, a policy | The owning capability records the gap with its reason; bootstrap reports it with the declaring skill's manual instructions. Not an error. |
| Registration cannot complete for a kind the harness holds only inside a configuration file the user owns | Nothing is written. Report which kind, why, the manual steps the user would take, and that invocation by path works meanwhile. Never edit that file. |
| The contracts or roles directory cannot be resolved beside `skills_root` | Record what was confirmed and ask for the rest. An unconfirmed directory is left unrecorded and reported as still needed — never guessed. |
