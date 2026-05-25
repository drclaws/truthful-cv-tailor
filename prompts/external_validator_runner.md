# External Validator Runner

Task:
Run or prepare configured external resume validators.

Inputs:
- Final CV PDF/DOCX
- Job description
- `validators/external/registry.yaml`
- Per-validator config files linked from the registry, such as
  `validators/external/enhancv.yaml`

For each enabled validator:
1. Read its config from `validators/external/registry.yaml`.
2. Identify required input files from that config.
3. Check whether required resume formats exist.
4. Confirm local validation gates have already run for the final CV.
5. If files are missing, request or create export commands.
6. If the config defines `runner.command`, execute it and follow
   `runner.browser_window`, `runner.captcha_policy`, and any documented
   `runner.troubleshooting` overrides. Use `runner.make` when present instead of
   reconstructing the command by hand.
7. If the validator requires manual use, prepare a clear checklist from the
   config inputs/outputs.
8. Save the resulting external report to the expected output path.

Default requirement:
- Unless the user explicitly says not to use external validators, run or prepare
  every enabled validator registered in `validators/external/registry.yaml`.
- External validators are the final advisory step. Run them only after local
  fact validation, ATS validation, position match validation, LaTeX/PDF sanity
  checks, and PDF text extraction checks.
- Prefer final delivery files from `exports/` named with the
  `FirstNameSurname\..*` pattern. Do not require `exports/final_cv.*` except as
  a temporary compatibility artifact.

Rules:
- Do not modify the CV.
- Do not accept validator recommendations as true.
- Do not add missing keywords to the CV.
- Do not invent facts.
- Only produce or normalize reports.
