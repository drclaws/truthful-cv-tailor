# External Validators Runbook

Unless explicitly disabled for a run, the agent should use every enabled
validator registered in `validators/external/registry.yaml` after all local
gates pass.

Ask the agent to run external validation with
`prompts/external_validator_runner.md`. Runner commands and policies live in
each validator config, for example `validators/external/enhancv.yaml`.

## Manual fallback

Use this only when browser automation fails or a site requires fully manual
upload:

1. Export final CV to DOCX/PDF using the candidate-name pattern
   `FirstNameSurname\..*`, such as `JaneDoe.pdf` and `JaneDoe.docx`.
2. Upload to Resumly or Enhancv.
3. Paste the job description if required.
4. Copy the report/suggestions into the matching raw report path:

```text
outputs/<job>/external_validators/resumly_raw.md
outputs/<job>/external_validators/enhancv_raw.md
```

5. Ask the agent to normalize and gate the imported raw reports using
   `prompts/external_report_normalizer.md` and
   `prompts/external_validation_gate.md`.
6. Apply only accepted changes and re-run Fact Validator.
