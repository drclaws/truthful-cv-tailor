# Full CV Tailoring Pipeline

Run for a given job. The job may be represented by `data/jobs/<job>` project
files, by external inputs provided during the run, or by both.

Inputs:
- Canonical candidate inputs provided for the run, such as original CV/resume,
  LinkedIn export, portfolio/project notes, GitHub/publication notes, or other
  user-provided evidence.
- Canonical job inputs provided for the run, such as job description, recruiter
  notes, screening signals, company notes, or LinkedIn/public notes about
  interviewers, hiring managers, and team members.
- Project candidate files, when present:
  - `data/master/experience_bank.md`
  - `data/master/projects.md`
  - `data/master/skills_matrix.md`
  - `data/master/constraints.md`
- Project job files, when present:
  - `data/jobs/<job>/job_description.md`
  - `data/jobs/<job>/recruiter_notes.md`
  - `data/jobs/<job>/company_notes.md`

If external, pasted, connector, or otherwise non-project inputs are used, first
create `outputs/<job>/00_source_audit.md` with the input inventory, source role,
and any necessary factual snippets or metadata needed for later validation.

Before evidence mapping, check source metadata in `experience_bank.md`,
`projects.md`, and `skills_matrix.md`. If canonical inputs changed or file
modification times no longer match the metadata, refresh the affected derived
index from canonical inputs. For file-based sources, use
`scripts/source_freshness_check.py` or equivalent mtime inspection when
possible. Do not create or rely on `data/master/master_cv.md`.

Update `constraints.md` when new conservative constraints become clear, such as
unsupported recurring keyword suggestions, wording risks, external-validator
advice that should constrain future runs, or source conflicts.

Outputs:
0. `00_source_audit.md`, when non-project inputs are used
1. `01_job_analysis.md`
2. `02_recruiter_signals.md`
3. `03_evidence_map.md`
4. `04_targeted_cv.md`
5. `05_fact_validation.md`
6. `06_ats_validation.md`
7. `07_position_match.md`
8. `08_final_cv.md`
9. `09_gap_report.md`
10. rendered LaTeX and exports when validations pass.

Export naming:
- Keep the rendered LaTeX source as `render/final_cv.tex`.
- Save final delivery files in `exports/` using the candidate-name pattern
  `FirstNameSurname\..*`, for example `JaneDoe.pdf` and `JaneDoe.docx`.
- Concatenate first name and surname without spaces or punctuation.
- `exports/final_cv.*` may exist only as a temporary compatibility artifact;
  do not treat it as the final exported result.

External validator ordering:
- Unless the user explicitly disables external validators, run every enabled
  validator registered in `validators/external/registry.yaml`.
- Run external validators last, only after local validation gates and local PDF
  extraction checks are complete.
- For Enhancv, upload the rendered PDF after `05_fact_validation.md`,
  `06_ats_validation.md`, `07_position_match.md`, `08_final_cv.md`, and
  `pdf_text_check.md` exist for the job output.
- Enhancv must use a browser-driven runner because the upload and processing
  flow performs client-side JavaScript work after each page open and each
  resume upload.
- External recommendations may drive final edits only through
  `prompts/external_validation_gate.md`, and all previous rules still apply:
  truth, ATS readability, template style immutability for fit, moderate
  Experience compression for one-page CVs, and reuse of extra space only for
  supported target-relevant Experience evidence.

Tag-signal handoff:
- Job and recruiter analysis may preserve short hiring scan signals for possible
  render tags.
- Evidence mapping must verify which signals are supported by canonical
  candidate inputs or refreshed derived evidence indexes.
- The Markdown CV stays plain and linear; render tag candidates live in writer
  notes and validation reports until the template renderer chooses a small
  supported set.
- Header tags are disabled by default. They are optional exceptions, not default
  header content, and cannot carry unsupported keywords or the only copy of
  critical CV facts.

Header-title handoff:
- The CV Writer chooses a short market-facing title from supported identity,
  seniority, and target-relevant specialization.
- Fact Validation checks that the title does not imply unsupported vacancy
  domain claims and that Experience titles stay source-backed.
- The Template Renderer must use the validated CV header title instead of
  mechanically copying the vacancy title into `\PersonRole`.

Do not produce final CV until Fact Validation, ATS Validation, and Position Match are complete.
