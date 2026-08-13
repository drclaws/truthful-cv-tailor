# Capability: setup-master.register-skill

## Purpose

Records a check in the local rules file so that flows will actually use it. A check that exists but
is not recorded stays **inactive** — this is the supported way to activate one, whether it is a tool
shipped in this package or something the user keeps anywhere in their own environment.

The typical case is a validator: it is appended to the active validation set with its kind
(`internal` or `external`) and, when it lives outside this package, its location. Registering does
not install anything, does not bind any dependency, and never runs the check.

## Inputs

- `local_rules_file` — path to the existing harness-native local rules file — required.
- `skill_identity` — required: the check's **name**; **where it lives** (a tool package inside this
  package, or a path/description in the user's environment); and, when the check itself does not
  declare it, its **kind** — `internal` (runs in the pre-render check group) or `external` (runs only
  after the internal and render gates pass).
- `package_root` — the resolved root of this package — required. Contract `user-context` is read from
  it, as the authority on what a validation-set entry must carry; and a check that ships here is read
  from the tools directory inside it.

## Outputs

- `local_rules_file` — updated with the new entry, and with a per-skill settings subsection when the
  check declares recognized keys and the user supplies values.
- An **interactive report**: the entry as recorded, what it will change at run time, and the
  dependencies the check declares. Nothing else is written to disk.

## Procedure

1. **Locate the check.** Resolve `skill_identity` to a real check: a directory under this package's
   tools directory holding a `TOOL.md` with `name` and `description` frontmatter, or — for a check
   the user keeps in their own environment — whatever file the location they stated resolves to.
2. **Read what the check declares** — its name, its purpose, its kind if stated, the settings keys it
   recognizes, and its `## Dependencies` section. Nothing about the check is assumed; everything
   recorded comes from the check itself or from an explicit statement by the user.
3. **Confirm the kind.** `internal` and `external` place the check at different points of a flow and
   under different gates. If the check does not state its kind, **ask** — never infer it from the
   name. Mention the consequence: an external check runs only after the internal and render gates are
   green, and its findings are advisory.
4. **Check for an existing entry** with the same name. If one exists, update it rather than adding a
   duplicate, and confirm the change; if two entries would collide under different locations, ask
   which one is meant.
5. **Record the entry** in the active-validation-set section, preserving the section's existing
   order, comments and formatting:
   - name and kind — always;
   - location — only for a check kept outside this package, written as the user stated it;
   - a note when the check could not be read directly (one kept elsewhere that this environment
     cannot reach): the entry is recorded as **unverified**, on the user's statement.
6. **Offer settings, do not invent them — and ask for the ones the check cannot run without.** If the
   check declares recognized keys, offer a per-skill settings subsection and record only values the
   user states. Machine-specific bindings of that check's external dependencies belong in its own
   subsection, never in a shared lump.

   A key the check declares **required with no default** is different in kind from the rest, and it
   is **asked for** here rather than merely offered. Registration is the one moment at which such a
   key can still be caught: this package pins no value for it, so nothing can supply a default, and
   no flow reaches the check until it is registered, so run time is too late to be the first warning.
   Ask, say what the check does without it, and record the answer. If the user has no value yet,
   register the check all the same and **report the key as not recorded**: it becomes a `setting` row
   of the dependency matrix and stays visible there until it is filled. Never invent a value, and
   never record the check as though the key had been answered.
7. **Report and recommend.** State the recorded entry, when it will run, and which dependencies it
   declares — including any required key still not recorded, which enters the matrix as a `setting`
   row. Recommend running `check-environment` so the new check's dependencies enter the dependency
   matrix — recommend it; do not run the check itself, and do not run a flow to try it.

## Rules

- **The active set holds optional validators only.** The mandatory truthfulness check is a reviewer
  capability that every CV flow invokes regardless of this list; it is never registered here, and a
  request to add it is answered by saying it already always runs.
- **Registering is not installing.** No dependency is bound, nothing is downloaded, no environment is
  created. A registered check whose dependencies are unbound runs SKIPPED with instructions — a
  recorded outcome, never a flow failure.
- **A non-existent check is not registered as active.** If the check has not been built yet, record
  it — if the user wants a reminder — with a `planned` marker and state plainly that no flow will run
  it until it exists.
- **A check shipped here and a check of the user's own have identical rights.** The only difference
  in the record is the location field. This package prescribes no private-overlay mechanism: a check
  the user keeps elsewhere is a first-class citizen once registered.
- **Something that is not a check.** A package that is not a check is not added to the validation
  set. Record what it needs where it belongs — a per-skill settings subsection, for example the
  template a render tool should use — and say which flow step will pick it up.
- **Never rewrite the check.** This capability edits `local_rules_file` and nothing else; the check's
  own files, wherever they live, are read-only here.
- **Real paths stay local.** A location outside this package is written into the user's local file
  only, never into a file tracked by this repository.

## Adding a new check, end to end

The user-facing path from "I want another check" to "it runs":

1. **Write the check.** Kept in this package it is a tool: a folder with a `TOOL.md` — frontmatter
   (`name`, `description`), what it is and is not, expected inputs and outputs by contract, a runbook
   section (environment preparation, service interaction, manual fallback, troubleshooting — rules
   never live only in script code), and the standardized `## Dependencies` section. Or keep it in
   whatever form your own environment holds a check; both work, and both have the same rights here.
2. **Decide the kind** — `internal` or `external` — and state it in the check.
3. **Register it here.** Until it is recorded in the local rules file, it will not run.
4. **Refresh the dependency matrix** with `check-environment`, so any unbound dependency is visible
   before the next run rather than during it.

A check never edits the document it examines, and the scores of an external service are advisory,
never truth — those rules belong to the reviewer that executes the check and apply no matter who
wrote it.

## Failure and skip conditions

| Situation | Behaviour |
|---|---|
| `local_rules_file` does not exist | Stop. There is no recorded context yet; name `bootstrap` as the entry point. |
| The check cannot be found at the stated location | Record nothing. Report what was looked for and ask for the correct location. |
| The check exists but has no frontmatter naming it | Report it as not a valid check and stop; ask whether it should be built properly first. |
| The check's kind is neither stated nor confirmed | Do not record. Ask; a guessed kind puts the check in the wrong gate. |
| A check kept outside this package cannot be read from this environment | Record the entry on the user's statement, marked **unverified**, and say its dependencies could not be read. |
| The check declares a settings key **required with no default** and the user has no value yet | Register the check; report the key as **not recorded**, with what the check does without it. The gap stays visible as a `setting` row in the dependency matrix until it is filled — never invented here, never passed over in silence. |
| An entry with the same name already exists | Do not duplicate. Show both, confirm which one survives. |
| The check is not built yet | Record as `planned` if the user wants the reminder, and state that it is inert. |
