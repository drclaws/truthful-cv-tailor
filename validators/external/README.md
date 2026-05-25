# External Validators

External validators are advisory. They can suggest keywords, format fixes, and
ATS/readability improvements, but they cannot directly edit the CV. Unless the
user explicitly disables them, run every enabled registered validator last,
after local validation and PDF extraction checks pass.

Final resume inputs should come from `outputs/<job>/exports/` and use the
`FirstNameSurname\..*` filename pattern, such as `JaneDoe.pdf` or
`JaneDoe.docx`.

## Config as source of truth

Each validator config owns its `runner.command`, input/output paths, browser
policy, and troubleshooting flags. Agents read the config from
`validators/external/registry.yaml`; prompts and runbooks should reference the
config instead of duplicating commands.

## Adding a new validator

1. Add a config file, e.g. `validators/external/mytool.yaml`, including
   `runner.command` and policy fields agents need.
2. Register it in `validators/external/registry.yaml`.
3. Save raw reports to `outputs/<job>/external_validators/<tool>_raw.md`.
4. Normalize with `prompts/external_report_normalizer.md`.
5. Gate with `prompts/external_validation_gate.md`.
6. Re-run Fact Validator after any accepted edit.
