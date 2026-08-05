# Capability: knowledge-bank-curator.query-bank

## Purpose

Answer questions of the form "what evidence does the candidate have for X?" out of the knowledge
bank, returning cited extracts with an honest strength label. Two modes: a **single query** (tags,
topics, phrases, or facts — answered inline, no artifact) and **batch mode** over a requirements
profile, which produces the run's `evidence-map` artifact.

This capability performs **retrieval only**. It decides what evidence exists and how strong it is.
It never decides how the evidence should be used in a document: placement, section, wording for the
CV, and tag selection are the business of the document contract, the writer, and the analyst.

## Inputs

| Input | Contract / description | Required |
|---|---|---|
| `bank_dir` | The knowledge bank directory to query. | required |
| `queries` | Single-query mode: the list of tags, topics, phrases, or facts to look up. | one of the two |
| `requirements_profile` | Batch mode: the `requirements-profile` artifact — every requirement becomes one query. | one of the two |
| `constraints_ledger` | The constraints ledger, read-only. Every extract is checked against it. | required |
| `recruiter_signals` | The `recruiter-signals` artifact: its do-NOT-include list suppresses extracts. Signals never create evidence. | optional |
| `in_run_proposals` | Constraint proposals raised by earlier steps of the same run, not yet ingested into the ledger. Honoured exactly as ledger entries. | optional |
| `output_path` | Batch mode: where the evidence map is written. | batch only |
| `run_id` | Run identifier for the envelope. | batch only |

## Outputs

| Output | Contract | Status values |
|---|---|---|
| Batch mode: the evidence map at `output_path` | `evidence-map` | `complete`, `blocked` |
| Single-query mode: the extracts, returned inline to the caller | — | — |

The evidence map is a report-type artifact: it carries the common envelope and a `## Constraint
proposals` section (`None.` when there is nothing to propose).

## Procedure

1. **Check the bank is usable.** It must exist and carry its source-metadata block. A bank that is
   missing, empty, or metadata-less is reported to the caller rather than queried around; freshness
   itself was decided by the flow before this step.
2. **Read the constraints ledger** and any in-run proposals, in full, before retrieving anything. A
   guardrail that arrives after the extracts have been written is a guardrail that gets rationalised
   away.
3. **Normalise each query.** One requirement or one asked-about topic = one query. Expand it into
   the vocabulary the bank might actually use: synonyms, the public-facing description of an internal
   name, the concept behind a tool name (a named queue product also means the messaging/streaming
   capability), the practice behind an outcome. Retrieval failures are usually vocabulary failures.
4. **Search the whole bank per query** — thematic bullets, the position records, education and
   certifications, the project index, and the skills matrix. A requirement is often evidenced in a
   project narrative while being absent from the skills list, or vice versa.
5. **Extract the evidence.** For each hit record: the bank citation (file, section, and enough of the
   entry to identify it), the supporting fact in the bank's own conservative wording, the employer or
   project context, and the date or period when the bank states one.
6. **Assign a strength label** per the scale below, and only that scale.
7. **Apply the constraints.** Flag every extract touched by a ledger entry or in-run proposal with
   the constraint and what it forbids. An extract the ledger forbids outright is dropped, and the
   requirement is treated as having no evidence from that direction.
8. **Mark the gaps.** A requirement with no supporting entry anywhere in the bank is recorded as
   `GAP` with strength `None`. Never leave a requirement out because nothing was found — an absent
   row is indistinguishable from an oversight.
9. **Batch mode only:** write the evidence map to `output_path` per the `evidence-map` contract, with
   one entry per requirement in the profile's own order and identifiers, and set the status.
10. **Report retrieval problems** as findings inside the artifact: entries whose citation could not
    be resolved, requirements too vague to query, contradictions found inside the bank.

## Rules

### Strength scale

| Label | Means |
|---|---|
| `Strong` | Direct, specific, production evidence in the bank, with context and (where the bank has them) numbers. Sustained or repeated, not a single incident. |
| `Medium` | Real evidence, but narrower than the requirement: shorter exposure, a supporting rather than an owning role, an adjacent technology, or context the bank does not fully state. |
| `Weak` | Peripheral, one-off, inferred, or self-education/personal-project evidence; enough to mention honestly, not enough to claim capability. |
| `None` | Nothing in the bank supports it. Record as `GAP`. |

- **Never round a label up.** Ambiguity resolves downward. The word "Strong" is a promise the
  candidate has to keep in an interview.
- An entry tagged `(inferred from …)` in the bank can never be labelled `Strong`, and its inferred
  status is carried into the extract.
- An entry marked `unverified name` in the bank keeps that marker in the extract.
- Personal projects, courses and self-education are labelled as such in the extract and never
  presented as professional experience.

### Retrieval integrity

- **Only the bank is quoted.** If the bank cites a canonical source, that citation is carried
  through; a canonical source may be consulted to resolve an ambiguous bank entry, but evidence that
  exists only in a source and not in the bank is a **bank completeness defect** — report it, do not
  quietly promote it into the map. The bank is the shared, audited view.
- **Every extract carries a citation.** An uncitable extract does not go in.
- **Never invent or interpolate a metric**, a date, a scale number, or an ownership level, and never
  strengthen the bank's wording. If the bank says "contributed to", the extract says "contributed
  to".
- **Never merge two entries** into one stronger-sounding extract. Two facts are two extracts.
- **Internal names** are reported with the public-facing description the bank records, plus whatever
  constraint the bank attaches to the equivalence.
- **Breadth is part of retrieval.** Look past languages and tools: system and problem domains,
  reliability and delivery practices, security practices, collaboration and working modes, and
  language skills are all legitimate evidence for the right requirement.
- **Do not manufacture soft-skill evidence.** A behavioural requirement is supported only by a
  concrete behaviour recorded in the bank, never by a generic label.
- **Run isolation.** The bank, the run's own artifacts, and the repository definitions are the only
  admissible inputs. Another run's outputs are never evidence, never a wording source, never a
  precedent.

### Out of scope — deliberately

This capability does **not** emit: "include in summary / skills / experience" decisions, section
assignments, suggested CV wording, or header-tag proposals. That advice lives with the document
contract and the roles that own it. Producing it here would let retrieval quietly become authoring,
which is exactly the boundary the role split exists to protect. The one adjacent thing that *is* in
scope is a safety note attached to an extract — "this may only be described as a supporting role" —
because it constrains use rather than directing it.

## Failure and skip conditions

- **Bank missing, empty, or without a source-metadata block** — do not produce a map. Report it to
  the caller and stop; the flow decides whether to refresh first. Status `blocked`.
- **A requirement is too vague to query** — record the entry with strength `None`, the reason
  "requirement not specific enough to retrieve against", and a question for the analyst or the user.
  Do not guess what was meant.
- **The requirements profile is missing in batch mode** — stop and report; batch mode has no default
  input.
- **The ledger cannot be read** — stop and report. Retrieving without the guardrails risks producing
  extracts that were explicitly forbidden; that is worse than producing nothing.
- **Contradictions inside the bank** — report both entries with their citations as a finding, label
  the strength by the weaker of the two, and propose a constraint.
