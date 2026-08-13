# Capability: setup-master.update-settings

## Purpose

Revisits or modifies a setting that is already recorded in the user's local rules file: an experience
source, an entry of the active validation set, a per-package setting, or a free-text rule. It is the
maintenance counterpart of a setup pass — the environment already exists, and one recorded value has
to change.

It changes the record only. It never installs, binds, or migrates anything, and it never runs a flow
to check the effect of a change.

## Inputs

- `local_rules_file` — path to the existing harness-native local rules file — required.
- `request` — what the user wants changed: which section, which entry, and the new value (or the
  request to review a section before deciding) — required.
- `package_root` — the resolved root of this package — required. Contract `user-context` is read from
  it, as the authority on what each section means and which sections exist; and when the change
  touches a validation-set entry or a per-package setting, the declaring package's own definition
  file is read from it for the keys that package recognizes.

## Outputs

- `local_rules_file` — updated in place, with the agreed change and nothing else.
- An **interactive before/after summary** of every line that changed. Nothing is written to disk
  besides the local rules file.

## Procedure

1. **Read the current state.** Open `local_rules_file` and locate the section the request concerns.
   If the file does not exist, stop: there is nothing to update, and a setup pass is the correct
   entry point (`bootstrap`).
2. **Show before deciding.** Quote the current value of the setting back to the user — including
   entries adjacent to it when the request is vague ("change the template" → show the whole
   subsection). A change is agreed against what is actually recorded, not against memory.
3. **Validate the intended new value** against the authority that owns it:
   - a **per-package setting** — the declaring package's own definition file declares the recognized
     keys; an unrecognized key is reported and refused, never silently written;
   - a **validation-set entry** — name plus kind (`internal` or `external`), plus a location for a
     check kept outside this package; a change of kind moves when the validator runs, so state that
     consequence;
   - an **experience source** — free form; nothing is prescribed, but check readability where the
     environment allows and report a source that cannot be read;
   - **additional rules** — free text; it is honoured by flows but never overrides the repository's
     hard invariants, and a rule that tries to must be refused with an explanation.
4. **Apply the minimal edit.** Touch only the lines the change requires. Section order, comments,
   formatting and every unrelated line — including content this role does not own — stay exactly as
   they were.
5. **Handle removals explicitly.** Removing an entry (a source, a validator, a settings key) is a
   deletion of user content: confirm that specific removal, then state what it changes — a removed
   validator simply stops running; a removed source stops feeding the next bank refresh; a removed
   key that its declaring package marks **required with no default** leaves that package unable to
   run and reappears in the dependency matrix as a `setting` row that is not recorded.
6. **Report the diff** and, when the change could affect which dependencies matter — a validator
   added or removed, a template or a dependency binding changed — **recommend** running
   `check-environment` to refresh the dependency matrix. Recommend it; do not run it as part of this
   capability, and do not run any flow to observe the effect.

## Rules

- **Recorded settings only.** This capability edits what is already there and adds values to sections
  that already exist. Adding a *new check* to the active set is `register-skill`; creating the file
  for the first time is `bootstrap`. Point the user at the right one rather than improvising.
- **Never guess.** If the request does not identify the setting unambiguously, ask which one is meant.
- **Never normalize the user's free form.** Reformatting entries that were not part of the request —
  reordering sources, rewording rules, "tidying" the file — is a defect.
- **One file.** Only `local_rules_file` is written. This package's own files and the harness's
  configuration are read-only.
- **No side effects on the machine.** Recording that a package uses a given tool does not install or
  configure that tool; say so when the user expects otherwise.
- **The setup records are not settings.** The environment record and the harness-registration record
  say what was already done and how it was verified; they are dated evidence, not configuration, and
  the capabilities that wrote them are the only ones that change them. An entry that has gone stale
  is reported here, never edited into looking current.
- **Planned stays inert.** An entry marked `planned` may be edited like any other, but it remains
  something no flow will run until the thing exists.
- **Real paths stay local.** The values handled here are the user's own; they are never echoed into a
  repository file, only into `local_rules_file` and the interactive report.

## Failure and skip conditions

| Situation | Behaviour |
|---|---|
| `local_rules_file` does not exist | Stop. Report that there is no recorded context yet and name `bootstrap` as the entry point. |
| The requested section or entry is absent | Do not create it silently. Report what the file actually holds and ask what to do. |
| The new value uses a key the declaring package does not declare | Refuse the write, report the key and the keys that package does recognize. |
| The declaring package cannot be found or read | Record nothing. Report the entry as unresolved; a setting for a package that cannot be identified is a guess. |
| The request is to change the environment record or the harness-registration record | Write nothing. Those are records of what was done, not settings: name the capability that owns the entry, and say what would have to be prepared or registered again for the fact behind it to change. |
| The change would delete or rewrite content the user did not name | Stop at that line, show it, and ask for confirmation of that specific change. |
| A requested rule contradicts a hard invariant | Refuse, explain which invariant, and offer the closest formulation that does not. |
| The user abandons the change midway | Leave the file exactly as it was, and say that nothing was written. |
