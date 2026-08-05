# Capability: vacancy-analyst.extract-recruiter-signals

## Purpose

Extract, from the people side of a vacancy — recruiter notes, call transcripts, screening
conversations, notes about interviewers or team members — what the hiring side emphasises, what it
is worried about, what it wants to hear, and what it does not want to see. The result is a
`recruiter-signals` instance: positioning input for the writer, a scored component for fit, and a
checkable record for the reviewer.

**These inputs are emphasis-and-positioning signals only. They can never create candidate facts.**
A recruiter saying "they need deep experience in X" changes what is worth foregrounding if the
candidate has X; it never makes the candidate have X, and it never strengthens weak evidence.

## Inputs

| Parameter | Contract / description | Required |
|---|---|---|
| `run_id` | Identifier written into the envelope. | required |
| `job_dossier_path` | Directory of job-side inputs — contract `job-dossier`. The recruiter notes are the primary input; company notes give context. | required |
| `transcript_paths` | Conversation transcripts the notes point at — contract `transcript`. | optional |
| `people_notes` | Provided notes about interviewers, hiring managers, or team members, as `path-or-description — what it is`. | optional |
| `source_audit_path` | Contract `source-audit`; read for each input's trust classification and recorded conflicts. | optional |
| `constraints_ledger_path` | Contract `constraints-ledger`; read so recorded guardrails are honoured. | optional |
| `output_path` | Where to write the signals. | required |

## Outputs

| Parameter | Contract | Status values |
|---|---|---|
| `output_path` | `recruiter-signals` | `complete` — people-side inputs were present and extracted; `skipped` — the run has no people-side input at all. |

## Procedure

1. **Read every people-side input in full**, transcripts included, before extracting. Emphasis
   usually shows in repetition and in what a conversation returns to, not in a single sentence.
2. **Extract what the recruiter emphasised** — the points made first, made twice, or made with
   insistence. Quote or closely paraphrase, and attribute each to its input.
3. **Extract what the hiring manager likely cares about**, when the inputs support a reading of it.
   This is an inference and is tagged as one, with the wording it rests on.
4. **Extract team pain points** — what is broken, missing, or overloaded; what the new hire is
   expected to relieve. Pain points are the strongest positioning lever there is, so record them
   concretely and with their source.
5. **Extract business context** — funding stage, growth, deadlines, reorganisation, a product bet,
   the reason the role exists now.
6. **Extract candidate concerns and objections** raised or hinted at during the conversation:
   doubts about a background, seniority, location, notice period, compensation range, a technology
   the candidate has not used recently.
7. **Extract keywords and phrases worth mirroring** — the hiring side's own vocabulary, recorded
   verbatim. Mirroring wording is legitimate; mirroring claims is not.
8. **Split the positioning guidance in two, explicitly:**
   - what should influence the document's positioning (emphasis, ordering, framing);
   - the **do-NOT-include list** — what must stay out: compensation talk, internal politics, other
     candidates, anything the recruiter shared in confidence, anything unflattering about a former
     employer, and any topic the notes mark as a sensitivity.
9. **Propose scan-signal tag candidates** per the tag rules below.
10. **Write the artifact** to `output_path` with the common envelope, then add
    `## Constraint proposals`.

## Rules

**Signals never become facts.** Nothing extracted here is candidate evidence, and nothing here may
be written into a document as a candidate claim. Every entry is about what the hiring side wants,
fears, or values. If a note asserts something about the candidate, record it as *the note's
assertion* with its source — it remains subject to candidate-side verification elsewhere.

**Do not invent context.** No filling gaps with what a company of that kind usually wants. Absent is
`not stated in sources`. An inference is written as an inference, tagged `(inferred from <source>)`,
with the wording that supports it.

**Attribute everything.** Each signal names the input it came from, and — when several people spoke
— who said it. A signal with no attributable source does not belong in the artifact.

**Second-hand is labelled second-hand.** A recruiter's account of what the hiring manager thinks is
weaker than the hiring manager's own words. Carry the trust classification from the source audit
into each entry, and never present a paraphrase as a quotation.

**Conflicts.** When the notes contradict the posting — a different seniority, a different stack, a
different scope — record both readings with their sources and mark the conflict. Do not resolve it
here; the more canonical source and the escalation belong to the run, not to this artifact.

**The do-NOT-include list is binding downstream.** Write it as concrete items, each with the reason
it is excluded, so a later step can honour it without re-reading the raw notes.

**Tag-signal candidates.**

- Preserve short signals the notes support that may help a recruiter or hiring-manager scan even
  when they do not deserve a summary sentence or an experience bullet.
- Candidates are not limited to hard skills: system types, delivery context, and working modes
  qualify when they are concrete and relevant.
- Keep vague soft-skill labels out unless the notes provide concrete, job-relevant phrasing that
  candidate evidence could later support.
- Mark each candidate with its source and whether it came from an explicit statement or an inferred
  emphasis. Truth is not decided here — candidate support is verified elsewhere before any tag
  reaches a rendered document.

**Confidentiality.** Personal information about named individuals is recorded only to the extent it
bears on positioning. Anything else stays out of the artifact.

**Run isolation.** Only this run's people-side inputs and the shared repository definitions inform
the signals. Notes from another run are never sources here.

**Constraint proposals.** Propose a guardrail when the notes reveal a durable risk — for example a
phrase the hiring side reacts badly to, or a claim the candidate should never make without a
canonical source. Conservative and source-anchored only; `None.` when there are none.

## Failure and skip conditions

- **No people-side input at all.** Write the artifact with `status: skipped`, state that the run has
  no recruiter notes, no transcript, and no people notes, and record what would be needed. This is a
  recorded outcome, not a failure: downstream steps read the artifact and treat the recruiter
  component as absent.
- **Input present but unreadable:** record it as `unreadable` with the reason, continue with the
  rest, and lower the artifact's completeness note accordingly.
- **A transcript is referenced but not provided:** record the reference and the gap; do not
  reconstruct the conversation from the note that mentions it.
- **Contract version mismatch** on an input artifact: record it as a finding and report it rather
  than reinterpreting the artifact.
- **Unbound optional tool need** (professional-network lookup for a named interviewer): that entry
  is `SKIPPED` with instructions; the artifact still reaches `status: complete`.
