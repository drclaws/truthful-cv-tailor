# Capability: vacancy-analyst.score-fit

## Purpose

Measure how well a candidate matches a vacancy, on fixed weights, and say what that means for
positioning. The result is a `fit-report` instance: a weighted score, strong and partial matches,
gaps, risks, positioning advice, and a should-apply verdict.

The report is **INFORMATIONAL**. It sets no Pass/Fail state, blocks nothing, and gates nothing. A
calling flow that wants to act on a low score declares its own escalation rule and threshold in its
own skill definition; this capability neither knows nor invents one.

The capability is **input-format-agnostic** by design: candidate data may arrive as a knowledge
bank, as an evidence map, or as an arbitrary CV document. Which one was used is declared in the
report header, because it changes how much the score can be trusted.

## Inputs

| Parameter | Contract / description | Required |
|---|---|---|
| `run_id` | Identifier written into the envelope. Use `n/a` when scoring outside a run. | required |
| `requirements_profile_path` | Contract `requirements-profile` — what the vacancy asks for. | required |
| `candidate_data_path` | The candidate-side input to score. | required |
| `candidate_data_format` | Declares what `candidate_data_path` is: `knowledge-bank`, `evidence-map`, `cv-document`, or `external-cv` (a CV supplied by the user, obeying no contract). | required |
| `recruiter_signals_path` | Contract `recruiter-signals` — drives the recruiter component. | optional |
| `job_dossier_path` | Contract `job-dossier`; consulted for wording when the profile paraphrases. | optional |
| `constraints_ledger_path` | Contract `constraints-ledger`; recorded guardrails cap what may be counted as coverage. | optional |
| `tag_candidates_source` | Where validated or proposed tag signals may be read from, when the flow tracks them. | optional |
| `output_path` | Where to write the report. | required |

## Outputs

| Parameter | Contract | Status values |
|---|---|---|
| `output_path` | `fit-report` | `informational` — always. This contract has no pass/fail state. |

The report header declares `candidate_data_format` and the confidence caveat that goes with it (see
Rules). A fit report without that declaration is invalid.

## Procedure

1. **Confirm the format.** Open `candidate_data_path` and check it is what `candidate_data_format`
   claims. On a mismatch, stop and ask (see Failure conditions) — scoring a CV as if it were an
   evidence map silently inflates confidence.
2. **Load the requirements** from the requirements profile: must-haves, nice-to-haves,
   responsibilities, keyword sets, hidden priorities, screening filters.
3. **Load the recruiter signals** when provided: emphasis, pain points, do-NOT-include list.
4. **Match each requirement against the candidate data**, recording for each: the requirement, the
   candidate evidence found, its location in the candidate input, and a strength of `Strong`,
   `Medium`, `Weak`, or `None`.
5. **Score the six components** on the fixed weights below, showing the reasoning for each
   component's number — not just the number.
6. **Total the score**, stating the denominator explicitly (see the recruiter-component rule).
7. **Write the report sections:** overall score with the per-component breakdown; strong matches;
   partial matches; gaps; risks; suggested positioning; tag-signal fit (when tags are in play);
   should-apply verdict.
8. **Write the artifact** to `output_path` with the common envelope, then add
   `## Constraint proposals`.

## Rules

### Weights (fixed)

| Component | Max | What it measures |
|---|---|---|
| Must-have coverage | 40 | How many must-have requirements have real supporting evidence, weighted by strength. A must-have with `None` scores zero — it is never partially credited for adjacency. |
| Responsibilities alignment | 20 | Whether the candidate has actually done work of this kind and at this scope, not whether they could. |
| Seniority alignment | 15 | Scope of ownership, autonomy, and impact versus what the vacancy describes. Years alone are not seniority. |
| Domain alignment | 10 | Business/technical domain overlap, including genuinely transferable adjacent domains — marked as adjacent. |
| Keyword alignment | 10 | Presence of the vacancy's vocabulary in supported candidate material. This is the only component where presence counts, and it is capped at 10 for exactly that reason. |
| Recruiter signal alignment | 5 | How well the candidate answers the emphasis and pain points the people-side inputs revealed. |

**Total 100.** When no recruiter signals are available, the recruiter component is `n/a` — never
zero and never assumed full — and the overall score is reported out of **95** with the denominator
stated in the header and beside the total. Silently rescaling to 100 is a defect.

### Candidate-data formats and their confidence caveats

The header declares which format was used and carries the matching caveat verbatim in substance:

| Format | What it gives | Caveat to declare |
|---|---|---|
| `knowledge-bank` | The candidate's full documented experience, with citations. | Broadest coverage; nothing is tailored to this vacancy, so wording overlap is understated and keyword alignment is measured against source facts rather than a targeted document. |
| `evidence-map` | Requirement-by-requirement evidence with strength already assessed. | Highest confidence: strengths are pre-assessed against the bank. Coverage is limited to the requirements the map was built for — requirements outside it are scored `not assessed`, never assumed absent. |
| `cv-document` | A CV produced within this run. | Reflects tailoring and wording as they will be read, but it is a derived document: a claim it makes is only as good as the evidence behind it. |
| `external-cv` | A CV supplied by the user, obeying no contract. | **Self-report.** Every claim is treated as a claim, not as verified evidence; strengths are capped at `Medium` unless the claim is specific, dated, and internally corroborated. The report states plainly that no canonical verification was performed. |

The score is comparable across runs only within the same format. Say so in the header when the flow
compares vacancies.

### Scoring discipline

- **Be critical.** The default posture is scepticism; a generous score is a disservice.
- **No credit for unsupported claims.** A requirement with no evidence is a gap and scores zero in
  its component, regardless of how adjacent the candidate's background looks.
- **Distinguish real experience from keyword presence.** "Used once in a side project" and "owned in
  production for three years" are not the same evidence, and the report says which one it found.
- **Weak stays weak.** Never round a strength up to make a component look better.
- **Recency and depth are part of strength**, not separate credits: evidence that is real but years
  old is `Medium` at best, and the report names the recency concern in Risks.
- **Constraints cap coverage.** A requirement whose supporting claim the constraints ledger forbids
  is scored as if the claim did not exist, and the constraint is named in the entry.
- **Tag signals never raise the score.** A proposed tag improves the score only when its evidence is
  real and already present in the candidate data being scored. A tag whose support is not in that
  input is listed in the tag-signal section as unsupported and is scored as nothing.
- **The do-NOT-include list is honoured**: positioning advice never recommends something the
  recruiter signals excluded.
- **Every component's reasoning is written down.** A bare number is not a fit report.

### Report content beyond the score

- **Strong matches** — where the candidate genuinely exceeds or meets the bar, with the evidence.
- **Partial matches** — real but insufficient evidence, with what is missing to make it strong.
- **Gaps** — requirements with no support, stated plainly. Never accompanied by a suggestion to
  claim them.
- **Risks** — what could sink the application even where the score is decent: recency, seniority
  scope mismatch, a screening filter the candidate fails, an unexplained gap, a domain the candidate
  cannot speak to at interview depth.
- **Suggested positioning** — what to foreground, what to compress, which honest framing best serves
  this vacancy. Positioning never means asserting something unsupported.
- **Tag-signal fit** — when tags are proposed: which supported signals help hiring-manager scan fit
  and which should be omitted because they are weak, misleading, redundant, or unsupported.
- **Should apply?** — one of `Strong yes`, `Yes, with positioning`, `Maybe`, `Low ROI`, with the
  reasoning. It is an opinion for the user, not a gate: this capability never decides whether the
  run continues.

**Run isolation.** Scores, verdicts and phrasing from another run are neither benchmark nor
precedent. Only this invocation's inputs, the shared knowledge bank, and the shared repository
definitions are read.

**Constraint proposals.** Propose a guardrail when scoring exposes a durable claim risk — for
example a keyword the candidate would be tempted to claim on adjacency alone. `None.` when there are
none.

## Failure and skip conditions

- **Format mismatch** between `candidate_data_format` and the file's actual content: stop, do not
  score, and ask the user. Guessing the format invalidates the report's confidence declaration.
- **Missing requirements profile:** the capability cannot run. Report to the flow; there is nothing
  to score against.
- **Missing recruiter signals:** not a failure — the recruiter component is `n/a` and the
  denominator becomes 95, as above.
- **Evidence map that does not cover all must-haves:** score the covered ones, mark the rest
  `not assessed` with the reason, and state in the header that coverage was partial. Never treat
  `not assessed` as `None`.
- **Empty or unreadable candidate data:** stop and report. A report scored against nothing is
  misleading even when labelled.
- **Contract version mismatch** on an input artifact: record it as a finding and report it rather
  than reinterpreting the artifact.
- This capability has **no failing state of its own**: when it runs, it produces an informational
  report. When it cannot run, it produces no report and says why.
