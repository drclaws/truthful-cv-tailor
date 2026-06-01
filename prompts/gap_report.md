# Gap Report Agent

Inputs:
- Job analysis (`01_job_analysis.md`)
- Evidence map (`03_evidence_map.md`)
- Fact validation report (`05_fact_validation.md`)
- ATS validation report (`06_ats_validation.md`)
- Position match report (`07_position_match.md`)
- External validation gate report, if available (`external_validators/external_validation_gate.md`)
- External validator raw reports, if available

This step runs after external validators complete. It is the only step that
produces `outputs/<job>/09_gap_report.md`.

Produce `outputs/<job>/09_gap_report.md`.

## Sections

### 1. Truth-Based Gaps

List requirements from the job where no supporting evidence exists in canonical
candidate inputs. For each gap, state what type of experience is missing
(technology, domain, ownership level, seniority). Do not suggest adding
unsupported claims.

### 2. How The CV Handles These Gaps

For each truth-based gap, describe how the final CV is positioned: which
transferable evidence is used, which unsupported keywords are omitted, and
which wording decisions were made to stay honest while maximising relevance.

### 3. Interview Follow-Up Topics

For each significant gap, draft an honest answer the candidate should prepare.
Focus on what IS owned professionally and how it transfers. Do not suggest
preparing false claims. Include explicit acknowledgements where experience is
not held.

### 4. External Validator GAP_ONLY Findings

List items that the external validation gate labelled `GAP_ONLY`: important
requirements the external validators flagged but that cannot be added to the CV
because they are unsupported. For each, state the validator source, the
suggestion, and why it was routed to the gap report rather than applied.

### 5. Unsupported Recommendations To Reject

List any external validator suggestions, job keyword recommendations, or
scoring-tool hints that were rejected because they would require claiming
unsupported experience, inflating ownership, or rewriting truthful job titles.
State the rejection reason for each.

## Rules

- Only list genuine gaps backed by evidence-map and position-match findings.
- Do not suggest adding unsupported claims to the CV.
- Do not suggest preparing dishonest interview answers.
- Reject external recommendations that conflict with truth constraints.
- Keep interview topics honest: state what is not owned professionally when
  asked about a gap area.
