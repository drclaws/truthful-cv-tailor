# Full CV Tailoring Pipeline

Run for a given job. The job may be represented by `data/jobs/<job>` project
files, by external inputs provided during the run, or by both.

Source priority, source audit rules, derived index freshness checks,
constraints update policy, required outputs, and export naming are defined in
`AGENTS.md` and apply here without repetition.

## Step ordering

1. `00_source_audit.md` — when non-project inputs are used
2. `01_job_analysis.md`
3. `02_recruiter_signals.md`
4. `03_evidence_map.md`
5. `04_targeted_cv.md`
6. `05_fact_validation.md`
7. `06_ats_validation.md`
8. `07_position_match.md`
9. `08_final_cv.md`
10. `09_gap_report.md` — after external validators complete; see `prompts/gap_report.md`
11. rendered LaTeX and exports — after internal validation gates pass
12. external validators — after render and PDF extraction checks pass
13. `10_master_cv_review.md` — last, after all validators and render checks

Do not produce `08_final_cv.md` until steps 6, 7, and 8 pass.

## External validator ordering

- Run every enabled validator in `validators/external/registry.yaml` unless the
  user explicitly disables them.
- Run external validators after local validation gates and PDF extraction checks
  are complete.
- Execute with `prompts/external_validator_runner.md`.
- Apply recommendations only through `prompts/external_validation_gate.md`.

## Tag-signal handoff

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

## Header-title handoff

- The CV Writer chooses a short market-facing title from supported identity,
  seniority, and target-relevant specialization.
- Fact Validation checks that the title does not imply unsupported vacancy
  domain claims and that Experience titles stay source-backed.
- The Template Renderer must use the validated CV header title instead of
  mechanically copying the vacancy title into `\PersonRole`.

## Master CV review ordering

- Run `prompts/master_cv_review.md` last, after all validators, render checks,
  and external validation steps are complete.
- The master CV review reads all outputs from the current run (`01` through `09`
  plus any external validator reports) and the current master data files.
- Write the result to `outputs/<job>/10_master_cv_review.md`.
- The master CV review does not modify master data files directly; it produces
  questions and conditional update suggestions for the candidate to act on.
