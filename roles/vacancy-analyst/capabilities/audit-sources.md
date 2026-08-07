# Capability: vacancy-analyst.audit-sources

## Purpose

Build the audit trail of the run's **inputs before any analysis is drafted**: what was provided,
where each item came from, what kind of input it is, how much it can be trusted, and where the
inputs disagree. The job-side material is inventoried and classified here in full; the knowledge
bank the candidate evidence comes from is recorded by version and freshness, transcribed from the
check the flow already ran. The result is a `source-audit` instance — the artifact later steps and
the reviewer use to check that every targeting decision traces back to something that was actually
supplied for this run.

An unsaved summary is not a source. If an input cannot be stored in the run, this capability records
enough metadata and enough verbatim factual snippets that a later step can still validate against
it.

## Inputs

| Parameter | Contract / description | Required |
|---|---|---|
| `run_id` | Identifier written into the envelope. | required |
| `job_dossier_path` | Directory of job-side inputs — contract `job-dossier` (job description, recruiter notes, company notes). | required |
| `additional_inputs` | Any further job-side material provided for this run: pasted text, exported pages, connector-provided content, notes about interviewers or team members. Each entry as `path-or-description — what it is`. | optional |
| `transcript_paths` | Meeting transcripts a recruiter note points at — contract `transcript`. | optional |
| `run_manifest_path` | The run manifest — contract `run-manifest`; read to record the user-context resolution the run used, and read again for `## Bank freshness` — the verdict with its per-source and per-index statuses that this capability transcribes into `## Bank stanza`. | optional |
| `constraints_ledger_path` | Contract `constraints-ledger`; read so that known guardrails are honoured while summarising. | optional |
| `output_path` | Where to write the audit. | required |

## Outputs

| Parameter | Contract | Status values |
|---|---|---|
| `output_path` | `source-audit` | `complete` — every provided input inventoried; `blocked` — a required input is unreachable and the run cannot proceed without it. |

**One file, one writer — this capability writes the whole artifact, `## Bank stanza` included.** That
stanza records which knowledge-bank version the run's candidate evidence came from and how fresh it
was. The verdict behind it is not decided here: it is *produced* by
`knowledge-bank-curator.check-freshness` and returned to its caller, the flow records it in the run
manifest under `## Bank freshness`, and this capability **transcribes** it into the stanza,
attributed to that check. The curator does not write into this file — two roles editing one artifact
is exactly the ambiguity contracts exist to remove, so the produce/transcribe split is the mechanism
that keeps one writer here, not a formality.

What stays out of reach is *deciding* bank facts rather than recording them. A bank version or a
freshness verdict is copied from the recorded check with its attribution; it is never re-derived
from the bank itself, and no candidate claim is drawn out of bank content here.

## Procedure

1. **Enumerate.** List every job-side input available to the run: each file in the job dossier, each
   entry of `additional_inputs`, each transcript. Enumerate before reading, so that an item that
   turns out to be empty is still visible as "provided but empty".
2. **Identify each item.** For every input record: an identifier, its origin (project file, provided
   during the run, pasted text, exported page, connector output, transcript), its date or version if
   the item states one, and whether the original content is stored inside the run.
3. **Classify by role in the run.** Exactly one primary kind per item: `job targeting` (the vacancy
   itself), `company context`, `recruiter signal`, `people/team context`, or `other`. Candidate
   evidence is not summarised here — if candidate material appears among the job-side inputs, list
   it as `candidate evidence (not summarised here)` and leave its content alone. The run's candidate
   evidence comes from the knowledge bank, whose state `## Bank stanza` records at step 8.
4. **Classify by trust.** Mark each item `canonical` or `self-report` per the rules below, and state
   in one clause why.
5. **Extract anchor snippets.** For each item that is not stored verbatim inside the run, copy the
   short factual snippets that later steps will rely on — requirement lines, seniority statements,
   location and employment terms, salary or process statements — as quotations attributed to the
   item.
6. **Compare and mark conflicts.** Cross-read the items for disagreement on role title, seniority,
   scope, location, employment terms, technology stack, process, and dates. Record every conflict
   with both readings, both sources, and which one is more canonical — or `undecided` when neither
   is.
7. **Record gaps in the input set.** Note what a run of this kind normally has and this one does not
   (for example: no company notes, no recruiter notes, a job description with no seniority
   statement). Absence is a finding, not something to fill in.
8. **Transcribe the bank stanza.** Read `## Bank freshness` from the run manifest at
   `run_manifest_path`. List the bank files it names as inventory entries of kind `bank file`, then
   copy the verdict with its per-source and per-index statuses into `## Bank stanza`, attributed to
   `knowledge-bank-curator.check-freshness`, and say whether a refresh was performed before the run
   proceeded. Copy what was recorded — a freshness opinion formed here after the fact would not be
   the verdict the run actually acted on.
9. **Write the artifact** to `output_path` with the common envelope, then add
   `## Constraint proposals`.

## Rules

**Trust classification.**

- `canonical` — the material as published or written by the hiring side, or a stored verbatim copy
  of it: the job posting text, the employer's own written material, a stored export of a public
  page, a transcript of an actual conversation.
- `self-report` — someone's account of something rather than the thing itself: a recruiter's
  paraphrase of the role, a note written from memory after a call, a third party's opinion about the
  team, an undated summary whose original is not stored.
- A `self-report` item may still be the only source for a fact. That is fine — it is recorded with
  its classification, and every later step sees how strong the ground is.

**Conflicts.** Mark them explicitly instead of choosing silently. A conflict entry names the topic,
quotes both readings with their sources, and states the resolution: `canonical wins`, `undecided —
ask the user`, or `both true in different scopes` with the scopes spelled out. A silently harmonised
conflict is a defect.

**Recruiter and people inputs are emphasis-and-positioning signals only.** Nothing in this audit
turns them into candidate facts, and nothing recorded here creates a candidate claim.

**No invention, no smoothing.** Missing metadata is `unknown`. An input that cannot be read is
recorded as `unreadable` with the reason, not omitted and not guessed at. Any statement that is
derived rather than read is tagged `(inferred from <source>)`.

**Run isolation.** Only this run's inputs, the shared knowledge bank, and the shared repository
definitions may be cited. Another run's job dossier or outputs are never listed as sources here,
even when the vacancy looks similar.

**Optional enrichment.** If the flow asked for enrichment (public company material via web search,
public profile context for named interviewers via a professional-network lookup) and the capability
is unbound, add an entry with kind `people/team context` or `company context`, status `SKIPPED`, and
the instruction the user would need to supply it manually. Never fail the step over it, and never
substitute recalled knowledge for a lookup that did not happen.

**Constraint proposals.** Propose a guardrail when the inputs reveal a durable trap — for example a
company whose public name differs from the legal entity in the posting, or a recurring
misclassification risk between two similar role titles. Conservative, source-anchored proposals
only; `None.` when there are none.

## Failure and skip conditions

- **Required input unreachable.** If `job_dossier_path` does not exist or contains nothing readable,
  write the artifact with `status: blocked`, list what was attempted, and report to the flow. Do not
  proceed to produce a partial inventory of nothing.
- **Individual item unreadable.** Record the item with `unreadable` and its reason; continue with
  the rest. One bad item never blocks the audit.
- **Empty optional input.** Recorded as provided-but-empty, not dropped.
- **No freshness verdict to transcribe.** If no run manifest was passed, or the one passed carries
  no `## Bank freshness`, still write `## Bank stanza`: name the bank files the run used and record
  the verdict as `not recorded for this run`, with the reason, then report it to the flow. The
  stanza is written either way, because a consumer reading it needs to see that the check is missing
  rather than find no stanza at all — but the verdict itself is copied or it is absent, never
  reconstructed here.
- **Contract version mismatch** on an input artifact: record it as a finding in the audit and report
  it to the flow rather than reinterpreting the artifact.
- **Unbound optional tool need:** the affected entry is `SKIPPED` with instructions; the artifact
  still reaches `status: complete`.
