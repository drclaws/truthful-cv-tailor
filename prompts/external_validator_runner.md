# External Validator Runner

Task:
Run or prepare configured external resume validators.

Inputs:
- Final CV PDF/DOCX
- Job description
- External validator registry
- Specific validator config

For each enabled validator:
1. Identify required input files.
2. Check whether required resume formats exist.
3. Confirm local validation gates have already run for the final CV.
4. If files are missing, request or create export commands.
5. If the validator supports browser automation, prepare browser steps.
6. If the validator requires manual use, prepare a clear checklist.
7. Save the resulting external report to the expected output path.

Default requirement:
- Unless the user explicitly says not to use external validators, run or prepare
  every enabled validator registered in `validators/external/registry.yaml`.
- External validators are the final advisory step. Run them only after local
  fact validation, ATS validation, position match validation, LaTeX/PDF sanity
  checks, and PDF text extraction checks.
- Prefer final delivery files from `exports/` named with the
  `FirstNameSurname\..*` pattern. Do not require `exports/final_cv.*` except as
  a temporary compatibility artifact.

Enhancv-specific rule:
- Run only after local fact validation, ATS validation, position match
  validation, and PDF text extraction checks.
- Use browser automation for the upload and report capture; do not replace it
  with a plain HTTP request because the page performs JavaScript loading and
  processing after opening and after each upload.

Rules:
- Do not modify the CV.
- Do not accept validator recommendations as true.
- Do not add missing keywords to the CV.
- Do not invent facts.
- Only produce or normalize reports.
