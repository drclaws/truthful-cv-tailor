# Capability: vacancy-analyst.gap-analysis

## Purpose

Report, at the end of a run, where the candidate genuinely does not meet the vacancy — and what was
done about it honestly. The result is a `gap-report` instance: truth-based gaps, how the produced
document handles each one, honest interview follow-ups the candidate should prepare, the items an
external gate routed to the gap report instead of the document, and the recommendations that were
rejected with the reason for each.

This report is the run's honesty ledger. It exists so that nothing unsupported quietly ends up in a
document, and so that the candidate walks into an interview knowing exactly which questions are
coming.

## Inputs

| Parameter | Contract / description | Required |
|---|---|---|
| `run_id` | Identifier written into the envelope. | required |
| `requirements_profile_path` | Contract `requirements-profile` — the requirements a gap is measured against. | required |
| `evidence_map_path` | Contract `evidence-map` — per-requirement evidence, strength, and GAP markers. | required |
| `cv_document_path` | Contract `cv-document`, the final instance — how the document actually handles each gap. | required |
| `validation_report_paths` | Contract `validation-report` — the truthfulness check and any registered validator reports. | optional |
| `fit_report_path` | Contract `fit-report` — gaps, risks, and positioning already identified during scoring. | optional |
| `external_gate_decision_path` | Contract `external-gate-decision` — per-recommendation verdicts, including `GAP_ONLY` and `REJECT`. | optional |
| `recruiter_signals_path` | Contract `recruiter-signals` — emphasis and the do-NOT-include list, which shape the interview preparation. | optional |
| `constraints_ledger_path` | Contract `constraints-ledger` — recorded guardrails behind some rejections. | optional |
| `output_path` | Where to write the report. | required |

## Outputs

| Parameter | Contract | Status values |
|---|---|---|
| `output_path` | `gap-report` | `complete` — every identified gap is addressed; `blocked` — a required input is missing. |

## Procedure

1. **Collect the gaps** from every input that names one: `None`/GAP entries in the evidence map,
   the gaps section of the fit report, unsupported-requirement findings in validation reports.
   Deduplicate by requirement, keeping every source reference.
2. **Verify each candidate gap against the requirements profile and the evidence map** before
   listing it. A gap is genuine only when the vacancy asks for it and no supporting evidence exists.
   An item nobody asked for is not a gap; an item with weak-but-real evidence is a weakness, and is
   labelled as such rather than as a gap.
3. **Classify each gap** by what is missing: technology, domain, ownership level, seniority/scope,
   scale, credential, or working context.
4. **Read the final document** and record, per gap, how it is actually handled: which transferable
   evidence carries the weight, which unsupported keywords were deliberately omitted, and which
   wording decisions kept the claim honest while staying relevant.
5. **Draft an honest interview follow-up per significant gap** (see rules).
6. **Collect the external `GAP_ONLY` items** from the gate decision, when one exists: for each, the
   validator that raised it, the suggestion, and why it was routed here instead of applied.
7. **Collect the rejected recommendations** — from external validators, keyword tools, or any
   scoring hint — with the reason each was rejected.
8. **Write the artifact** to `output_path` with the common envelope, then add
   `## Constraint proposals`.

## Rules

**Only genuine gaps.** Every entry is backed by the evidence map and the run's findings. A gap
invented from an impression of the market is noise that damages the report's credibility.

**Never suggest adding unsupported claims.** Not to the document, not "if you can justify it", not
as a softened variant. The only honest responses to a gap are: transferable evidence, an
acknowledgement, or a plan to acquire the experience.

**Never suggest a dishonest interview answer.** Interview preparation states what the candidate does
own professionally, how it transfers, and — explicitly — where the experience is not held. An
answer that avoids the question by implying experience is a defect. Each follow-up contains:
1. the honest acknowledgement of what is not held;
2. the closest genuinely owned experience, with what it consisted of;
3. why it transfers, stated in mechanism rather than in adjectives;
4. what the candidate would do to close the gap, when it is reasonable to say so.

**Distinguish "not held" from "not documented".** When a gap may be an artifact of thin
documentation rather than of missing experience, say so and mark it as a question for the candidate.
This report does not resolve it and does not write the bank — it flags it, and the curator's
bank-facing step follows up.

**Rejections are explained, not just listed.** Every rejected recommendation names its origin, the
exact suggestion, and the reason: it would require claiming unsupported experience, inflating
ownership, rewriting a truthful job title, contradicting a recorded constraint, or weakening the
document's readability. Truth constraints override external advice without exception, and external
scores are never truth.

**Recruiter and people inputs are emphasis-and-positioning signals only.** They shape which gaps
matter most and how to talk about them; they never close a gap and never create a candidate fact.

**No gate verdict here.** This report renders no Pass/Fail and no go/no-go. It reports; the user and
the flow decide.

**Run isolation.** Only this run's artifacts, the shared knowledge bank, and the shared repository
definitions are read or cited. Another run's gap report is neither template nor authority.

**Constraint proposals.** This is the richest source of durable guardrails in a run: a keyword that
must not be claimed, an ownership level that must not be inflated, a domain label the candidate must
not carry unless a canonical source adds it. Propose them conservatively and anchored to what this
run actually showed; `None.` when there are none.

## Failure and skip conditions

- **Missing requirements profile, evidence map, or final document:** write the report with
  `status: blocked`, naming the missing input, and report to the flow. Gaps cannot be established
  without both the ask and the evidence.
- **No external gate decision** (no external validation ran, or all of it was skipped): the
  `GAP_ONLY` section states that no external validation contributed, and the report is still
  `complete`.
- **No fit report:** derive gaps from the evidence map and validation reports alone, and note the
  narrower basis in the report.
- **A validation report is still `fail`:** produce the gap report against the document as it stands
  and state plainly that the document has unresolved findings — do not wait, and do not describe
  handling that has not happened.
- **No gaps found:** unlikely but legitimate. State it explicitly, list the requirements checked so
  the claim is verifiable, and still produce the interview-preparation section for the weakest
  supported areas.
- **Contract version mismatch** on an input artifact: record it as a finding and report it rather
  than reinterpreting the artifact.
