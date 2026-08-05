# Capability: knowledge-bank-curator.maintain-constraints

## Purpose

Ingest the `## Constraint proposals` raised by a run's reports into the constraints ledger — the
negative-evidence guardrails that keep future documents from claiming what the sources do not
support ("do not claim X unless a canonical source adds it"). This is the **only** capability in the
entire system that writes the ledger, and flows invoke it as their closing step.

Its judgement call is narrow and fixed: a proposal that merely restricts what may be claimed is
applied without asking; anything else becomes a question to the user.

## Inputs

| Input | Contract / description | Required |
|---|---|---|
| `report_paths` | The run's report artifacts carrying `## Constraint proposals` sections — source audit, requirements profile, recruiter signals, evidence map, validation reports, gate decision, fit report, gap report, render manifest, bank update brief. | required |
| `constraints_ledger` | The ledger to write. Created if it does not exist. | required |
| `run_id` | The run whose proposals are being ingested; recorded as the origin of each entry. | required |
| `direct_proposals` | Proposals given directly by the user or by a role invoked outside a flow. | optional |
| `bank_dir` | The knowledge bank, read-only — used to check a proposal against what the bank actually contains. | optional |

## Outputs

| Output | Contract | Status values |
|---|---|---|
| The updated ledger at `constraints_ledger` | `constraints-ledger` | `complete` |
| An ingestion summary returned to the caller: applied, already present, pending user answer, rejected — each with its reason | — | — |

The ledger is a persistent artifact: `run_id: n/a` in its envelope, and `revision:` incremented on
every ingestion that changes it.

## Procedure

1. **Collect** every `## Constraint proposals` entry from each report path, plus any direct
   proposals. Record for each: the proposing role and capability, the artifact it came from, and the
   run id.
2. **Normalise** each proposal into one ledger-ready statement: a single restriction, in the negative
   form the ledger uses, specific enough to be checkable against a document. A proposal bundling
   several restrictions is split; a proposal too vague to check is not applied (see below).
3. **Deduplicate.** Compare against the existing ledger by meaning, not by wording. An entry that
   already says the same thing is *not* re-added: record the new run as an additional occurrence of
   the existing entry, which is how recurring signals become visible.
4. **Classify** each remaining proposal as *conservative* or *not* (rules below).
5. **Apply the conservative ones** without asking the user. Append each as a new entry with its
   fields (below).
6. **Turn everything else into a question**: record the proposal as `pending-user` with the question
   to ask, and report it to the caller. A pending entry never constrains a document — it is a
   record, not a rule.
7. **Update the envelope** — bump `revision:`, refresh `updated:` — only if something changed.
8. **Return the ingestion summary.** The flow reports it; unanswered questions are carried to the
   user, and they never block flow completion.

## Rules

### Entry fields

Every applied entry records: the **statement** (what may not be claimed, and under what condition it
could be); the **rationale** (what evidence or absence of evidence justifies it); the **origin**
(run id, producing role and capability, artifact); the **date**; and the **status** —
`active` / `superseded` / `pending-user`.

### What counts as conservative — applied without asking

A proposal is conservative when it can only ever *narrow* what the system claims. Concretely:

- it records an **absence** the run established ("no canonical source shows container-orchestration
  ownership");
- it **caps a claim** to what the evidence supports ("this may be described as contribution, never as
  ownership");
- it **forbids a keyword or category** that the sources do not support, including one an external
  validator suggested adding;
- it records a **wording risk** — a phrasing that reads as a stronger claim than the evidence carries;
- it records a **safe-use note for an equivalence** ("the public-equivalent mapping may be used for
  the capability class, not for the specific product's operational experience");
- it records a **factual limitation** established by fact-checking ("the period at <employer> is
  stated month-level in the sources; do not round it to full years").

Applying these needs no permission because the failure mode of a wrong conservative constraint is a
CV that says slightly less than it could — recoverable, and visible in the next gap report.

### What is never applied silently — always a question

- anything that would **widen** what may be claimed, or that asserts a new positive fact;
- any **deletion, weakening, or narrowing of scope** of an existing entry, including "this constraint
  no longer applies" — a constraint is retired only on an explicit user answer, and then by marking
  it `superseded` with the reason and date, never by erasing it;
- a proposal that **contradicts** an existing entry, the bank, or a canonical source;
- a proposal that encodes a **policy or stylistic preference** rather than a factual limitation
  ("always lead with the platform work") — that belongs in the user's own rules, not in the ledger;
- a proposal **too vague to check** against a document ("be careful with cloud claims") — ask for the
  specific restriction instead of guessing one;
- a proposal derived **only from an external validator's score or advice** with no factual basis:
  external advice is never truth, and it does not become truth by being written down.

### Writing discipline

- **The ledger is effectively append-only.** Entries are added, or marked `superseded` with a
  reason. Existing text is not rewritten and never deleted.
- **Idempotent.** Re-running the ingestion for the same run must change nothing: the deduplication
  in step 3 sees the entries it already wrote. A flow that reruns its closing step twice must not
  produce duplicates.
- **This capability writes only the ledger.** Not the bank, not the run's artifacts, not the reports
  it read.
- **No proposal is invented here.** Only proposals actually present in the inputs are ingested; the
  capability never adds guardrails of its own judgement.
- **Within the run, proposals already applied earlier as in-run guardrails are still ingested here** —
  earlier steps honour them provisionally, this step makes them durable.

## Failure and skip conditions

- **A report path is missing or unreadable** — ingest the rest, and report the skipped input by name.
  A missing report never blocks the flow's closing step.
- **A report has no `## Constraint proposals` section at all** — record it as a finding (every
  report-type contract requires the section, even if only to say `None.`), and continue.
- **The ledger does not exist** — create it per the `constraints-ledger` contract, with an envelope
  at `revision: 1`, and ingest into it.
- **The ledger is unreadable or malformed** — stop. Do not overwrite it and do not start a new one:
  losing accumulated guardrails is worse than a failed closing step. Report it and ask the user.
- **Nothing to ingest** — that is success. Leave the ledger untouched (no revision bump) and report
  "no proposals".
- **Questions remain unanswered** — report them as pending, both in the ledger entries and in the
  summary. The flow completes; the questions go to the user.
