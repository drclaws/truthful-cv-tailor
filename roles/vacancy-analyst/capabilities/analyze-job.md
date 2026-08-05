# Capability: vacancy-analyst.analyze-job

## Purpose

Turn the vacancy into a structured, machine-usable profile of what the hiring side is actually
asking for: role and seniority, company context, must-have and nice-to-have requirements,
responsibilities, keyword sets, the priorities the posting implies without stating, and short scan
signals worth testing as CV tags. The result is a `requirements-profile` instance — the artifact the
curator queries the knowledge bank against, the writer targets, and fit scoring measures against.

The profile describes the **vacancy**, never the candidate. It makes no claim about what the
candidate has and decides no tag's truth.

## Inputs

| Parameter | Contract / description | Required |
|---|---|---|
| `run_id` | Identifier written into the envelope. | required |
| `job_dossier_path` | Directory of job-side inputs — contract `job-dossier`. The job description is the primary input; company notes provide context. | required |
| `source_audit_path` | Contract `source-audit`; read to know each input's trust classification and the recorded conflicts. | optional |
| `constraints_ledger_path` | Contract `constraints-ledger`; read so recorded guardrails are honoured. | optional |
| `output_path` | Where to write the profile. | required |

## Outputs

| Parameter | Contract | Status values |
|---|---|---|
| `output_path` | `requirements-profile` | `complete` — the vacancy is fully parsed; `blocked` — no readable job description was provided. |

## Procedure

1. **Read the vacancy end to end before extracting.** Requirements stated once in a closing
   paragraph count as much as those in the bulleted list.
2. **Extract the frame:** role title as written, seniority level, company context (what the company
   does, size and stage if stated, team the role sits in, product area, working model, location and
   employment terms). Anything the posting does not state is `not stated in sources`.
3. **Split the requirements** into `must-have` and `nice-to-have`. Use the posting's own signalling
   — "required", "you have", "we expect" versus "bonus", "nice to have", "a plus". When the posting
   does not signal, classify by how the requirement is written and mark the classification
   `(inferred from <source>)`.
4. **List the responsibilities** as the work the role performs, separately from the requirements it
   asks the person to already hold. Responsibilities drive fit scoring differently from
   requirements, so do not merge the two lists.
5. **Build the keyword sets**, three of them, kept apart: technical keywords, soft-skill keywords,
   domain keywords. Record each keyword in the posting's own wording; add a normalised form beside
   it only when the posting's wording is an abbreviation or a variant spelling.
6. **Name the hidden priorities** — what the posting repeats, front-loads, or spends the most words
   on; what its responsibilities imply about the team's real problem. Each hidden priority is an
   inference and is tagged as one, with the wording that supports it.
7. **Record the screening filters** the posting states or implies: hard requirements likely to be
   used as a first-pass cut (authorisation, location or time-zone overlap, years in a technology, a
   degree, a language, a certification).
8. **Record red flags and unclear requirements**: internal contradictions, a title that does not
   match the described scope, a scope that does not match the seniority, undefined terms, a
   requirement so broad it cannot be evaluated.
9. **Propose scan-signal tag candidates** per the tag rules below.
10. **Write the artifact** to `output_path` with the common envelope, then add
    `## Constraint proposals`.

## Rules

**Do not infer unsupported requirements.** Every requirement in the profile traces to wording in a
job-side input. Something the industry usually asks for, but this posting does not, has no place in
the profile — not even as a nice-to-have.

**Explicit and inferred stay visibly separate.** Each entry carries its status: quoted or closely
paraphrased from the posting, or `(inferred from <source>)` with the wording the inference rests on.
A reader must be able to strip every inference and still have a valid profile.

**Preserve the posting's vocabulary.** Requirements and keywords are recorded in the hiring side's
own words. Silent normalisation destroys the keyword sets' value and misleads the writer. Where a
translation is genuinely needed, keep the original and add the normalised form beside it.

**A requirement is not a candidate fact.** Nothing here says whether the candidate has anything.
Coverage, strength, and gaps are decided elsewhere, against candidate evidence.

**Conflicts.** When job-side inputs disagree about a requirement or about seniority, record both
readings with their sources and mark the conflict; prefer the more canonical input when the source
audit classifies one as such, and say that you did. Never merge two conflicting statements into one
smooth requirement.

**Tag-signal candidates.**

- Candidates are not limited to hard skills. Technical themes, system or problem types, working
  context, delivery modes, and short recruiter scan signals all qualify when a hiring manager would
  care about them.
- Keep each candidate short and job-relevant.
- Mark each candidate as coming from an explicit requirement or from an inferred priority.
- **Truth is not decided here.** A tag candidate is a hypothesis about what would help a scan; it
  reaches a rendered document only after candidate evidence supports it. Never present tag
  candidates as things the candidate can claim.
- Keep vague soft-skill labels out unless the posting gives concrete, job-relevant phrasing.

**Company context is context, not flattery.** Record what the sources say about the company and the
team. Where enrichment was requested and its capability is unbound, record the gap as `SKIPPED` with
instructions instead of filling it from recollection.

**Run isolation.** Only this run's job-side inputs and the shared repository definitions inform the
profile. A similar vacancy analysed in another run is neither evidence nor precedent.

**Constraint proposals.** Propose a guardrail when the vacancy reveals a durable claim risk — for
example a domain term the candidate must not be described with unless a canonical source adds it, or
a title that must never be mirrored mechanically. `None.` when there is nothing to propose.

## Failure and skip conditions

- **No readable job description.** Write the profile with `status: blocked`, listing what was
  provided, and report to the flow. A profile built from company notes alone is not a profile.
- **Job description present but thin** (a title and two lines): produce the profile with the little
  it supports, mark every section that the source cannot fill as `not stated in sources`, and record
  the thinness as a red flag. Do not compensate with general industry knowledge.
- **Contradictory seniority or role between canonical inputs** with no more-canonical source: record
  both, mark `undecided`, and escalate to the user through the flow.
- **Contract version mismatch** on an input artifact: record it as a finding and report it rather
  than reinterpreting the artifact.
- **Unbound optional tool need** (web search for company context): the affected section is `SKIPPED`
  with instructions; the profile still reaches `status: complete`.
