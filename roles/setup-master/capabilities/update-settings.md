# Capability: setup-master.update-settings

## Purpose

Revisits or modifies a setting that is already recorded in the user's local rules file: an experience
source, an entry of the active validation set, a per-skill setting, or a free-text rule. It is the
maintenance counterpart of first-run setup — the environment already exists, and one recorded value
has to change.

It changes the record only. It never installs, binds, or migrates anything, and it never runs a flow
to check the effect of a change.

## Inputs

- `local_rules_file` — path to the existing harness-native local rules file — required.
- `request` — what the user wants changed: which section, which entry, and the new value (or the
  request to review a section before deciding) — required.
- `user_context_contract` — path to the `user-context` contract file — required, as the authority on
  what each section means and which sections exist.
- `skills_root` — path to this repository's shipped skills — required when the change touches a skill
  entry or a per-skill setting, to read that skill's `SKILL.md` for the keys it recognizes.

## Outputs

- `local_rules_file` — updated in place, with the agreed change and nothing else.
- An **interactive before/after summary** of every line that changed. Nothing is written to disk
  besides the local rules file.

## Procedure

1. **Read the current state.** Open `local_rules_file` and locate the section the request concerns.
   If the file does not exist, stop: there is nothing to update, and first-run setup is the correct
   entry point (`bootstrap`).
2. **Show before deciding.** Quote the current value of the setting back to the user — including
   entries adjacent to it when the request is vague ("change the template" → show the whole
   subsection). A change is agreed against what is actually recorded, not against memory.
3. **Validate the intended new value** against the authority that owns it:
   - a **per-skill setting** — the owning skill's `SKILL.md` declares the recognized keys; an
     unrecognized key is reported and refused, never silently written;
   - a **validation-set entry** — name plus kind (`internal` or `external`), plus a location for a
     skill kept outside this repository; a change of kind moves when the validator runs, so state
     that consequence;
   - an **experience source** — free form; nothing is prescribed, but check readability where the
     environment allows and report a source that cannot be read;
   - **additional rules** — free text; it is honoured by flows but never overrides the repository's
     hard invariants, and a rule that tries to must be refused with an explanation.
4. **Apply the minimal edit.** Touch only the lines the change requires. Section order, comments,
   formatting and every unrelated line — including content this role does not own — stay exactly as
   they were.
5. **Handle removals explicitly.** Removing an entry (a source, a validator, a settings key) is a
   deletion of user content: confirm that specific removal, then state what it changes — a removed
   validator simply stops running; a removed source stops feeding the next bank refresh.
6. **Report the diff** and, when the change could affect which dependencies matter — a validator
   added or removed, a template or a dependency binding changed — **recommend** running
   `check-environment` to refresh the dependency matrix. Recommend it; do not run it as part of this
   capability, and do not run any flow to observe the effect.

## Rules

- **Recorded settings only.** This capability edits what is already there and adds values to sections
  that already exist. Adding a *new skill* to the active set is `register-skill`; creating the file
  for the first time is `bootstrap`. Point the user at the right one rather than improvising.
- **Never guess.** If the request does not identify the setting unambiguously, ask which one is meant.
- **Never normalize the user's free form.** Reformatting entries that were not part of the request —
  reordering sources, rewording rules, "tidying" the file — is a defect.
- **One file.** Only `local_rules_file` is written. Repository files, skills and harness
  configuration are read-only.
- **No side effects on the machine.** Recording that a skill uses a given tool does not install or
  configure that tool; say so when the user expects otherwise.
- **Planned stays inert.** An entry marked `planned` may be edited like any other, but it remains
  something no flow will run until the thing exists.
- **Real paths stay local.** The values handled here are the user's own; they are never echoed into a
  repository file, only into `local_rules_file` and the interactive report.

## Failure and skip conditions

| Situation | Behaviour |
|---|---|
| `local_rules_file` does not exist | Stop. Report that there is no recorded context yet and name `bootstrap` as the entry point. |
| The requested section or entry is absent | Do not create it silently. Report what the file actually holds and ask what to do. |
| The new value uses a key the owning skill does not declare | Refuse the write, report the key and the keys that skill does recognize. |
| The owning skill cannot be found or read | Record nothing. Report the entry as unresolved; a setting for a skill that cannot be identified is a guess. |
| The change would delete or rewrite content the user did not name | Stop at that line, show it, and ask for confirmation of that specific change. |
| A requested rule contradicts a hard invariant | Refuse, explain which invariant, and offer the closest formulation that does not. |
| The user abandons the change midway | Leave the file exactly as it was, and say that nothing was written. |
