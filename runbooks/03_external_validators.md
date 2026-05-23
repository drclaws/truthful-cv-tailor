# External Validators Runbook

Resumly and Enhancv are configured external validators. Unless explicitly
disabled for a run, use every enabled validator registered in
`validators/external/registry.yaml` after all local gates pass. Enhancv must be
run through a browser because its resume upload and report generation rely on
client-side JavaScript.

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

## Browser mode

If Playwright is available, Codex can attempt browser automation. Treat it as
best-effort because external site login, file upload, paywalls, captcha, email
collection, or UI changes can break it.

Run browser validators only after local validation is complete:

```text
outputs/<job>/05_fact_validation.md
outputs/<job>/06_ats_validation.md
outputs/<job>/07_position_match.md
outputs/<job>/08_final_cv.md
outputs/<job>/pdf_text_check.md
```

Enhancv PDF runner:

```bash
python3 scripts/run_enhancv_validator.py --job <job> --headed
```

The runner uploads:

```text
outputs/<job>/exports/FirstNameSurname.pdf
```

If multiple PDF exports exist, pass the intended candidate-named file with
`--pdf`.

and writes:

```text
outputs/<job>/external_validators/enhancv_raw.md
outputs/<job>/external_validators/enhancv_raw.html
outputs/<job>/external_validators/enhancv_raw.png
```

If the site asks for manual interaction, rerun with a wait window:

```bash
python3 scripts/run_enhancv_validator.py --job <job> --headed --manual-wait-seconds 120
```
