# External Validators Runbook

Unless explicitly disabled for a run, use every enabled validator registered in
`validators/external/registry.yaml` after all local gates pass.

## Manual mode

1. Export final CV to DOCX/PDF using the candidate-name pattern
   `FirstNameSurname\..*`, such as `JaneDoe.pdf` and `JaneDoe.docx`.
2. Upload to Resumly or Enhancv.
3. Paste the job description if required.
4. Copy the report/suggestions into the matching raw report path:

```text
outputs/<job>/external_validators/resumly_raw.md
outputs/<job>/external_validators/enhancv_raw.md
```

5. Normalize:

```bash
make external-normalize JOB=<job>
```

6. Gate recommendations:

```bash
make external-gate JOB=<job>
```

7. Apply only accepted changes and re-run Fact Validator.
