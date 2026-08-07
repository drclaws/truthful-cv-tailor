---
name: refresh-knowledge-bank
description: Rebuilds the candidate's knowledge bank from the canonical experience sources — resolves the sources from user context, checks freshness, runs the curator's build with its self-check and coverage gates, writes the source metadata, appends the refresh log, and closes by ingesting constraint proposals into the ledger.
---

# Workflow: refresh-knowledge-bank

Flow version: 1.0

## Purpose

The knowledge bank is the only thing every other flow reads about the candidate. Nothing else is
allowed to look at the canonical experience sources during a run, so a fact absent from the bank does
not exist for the rest of the system. This flow is how the bank comes into existence and how it stays
true to its sources.

It orchestrates one role — the `knowledge-bank-curator`, sole writer of the bank and of the
constraints ledger — and adds what a role must not do for itself: resolving the user's canonical
sources from user context, deciding the scope of the rebuild, recording the run, and closing the
ledger.

The flow **prepares evidence**. It never writes a CV, never reads a vacancy, and never judges
relevance: what is worth using is decided per run, downstream.

## When to run

Run this flow when:

- the bank does not exist yet (first run after `setup-master.bootstrap`);
- a canonical experience source changed since the bank was last built;
- new canonical sources were added to the user's context that the bank has never seen;
- another flow's preflight found the bank unusable — every CV flow settles the bank before evidence
  retrieval and routes here both when the verdict is `stale` and when the bank carries no
  `## Candidate` section, which the build derives;
- the user changed a fact at the source and wants the bank to catch up.

All bank indexes are built from the same source set, so **they are always checked together**, and
whichever of them the change touches is rebuilt in one invocation. A refresh always completes before
any evidence retrieval that depends on it — a stale bank silently produces a CV built on last
month's truth.

The flow is **not** the way to correct the bank by hand. The bank is derived: a wrong entry is fixed
by fixing the source and refreshing, or by recording the correction in the constraints ledger. The
derived indexes never override a canonical source.

## Run identifier and output layout

`run-id` is the refresh date, `YYYY-MM-DD`. A second refresh on the same day appends `-2`, `-3`, … —
runs are never overwritten.

```
outputs/refresh-knowledge-bank/<run-id>/     # the run report of THIS flow
outputs/knowledge-bank/                      # THE BANK — written by the curator, outlives runs
```

The bank directory is passed to the curator as an explicit parameter, like every other path. The
paths above are this flow's declaration of where it puts things; contracts fix no placement.

### Fixed artifacts

Steps that always run. Contract → default filename.

| Contract | Default filename | Where |
|---|---|---|
| `run-manifest` | `run.md` | `<run>/` |
| `knowledge-bank` | `experience_bank.md` | `<bank-dir>/` |
| `knowledge-bank` | `projects.md` | `<bank-dir>/` |
| `knowledge-bank` | `skills_matrix.md` | `<bank-dir>/` |
| `knowledge-bank` | `refresh_log.md` | `<bank-dir>/` — appended, never rewritten |
| `constraints-ledger` | `constraints.md` | `<bank-dir>/` — written only by `maintain-constraints` |

The bank files live **outside** the run directory: they outlive the run. The run's artifact index
records them by path all the same, so a reader of `run.md` can see exactly what this refresh touched.

### Flexible stages

One stage of this flow has a file set that is not fixed in advance: the **rebuild scope**. A full
refresh rebuilds every index; a partial refresh rebuilds only the indexes the freshness verdict
implicates, and leaves the rest byte-for-byte intact.

| Stage | Path pattern | Instantiated per |
|---|---|---|
| index rebuild | `<bank-dir>/<index>.md` | each index in the resolved scope (`experience_bank`, `projects`, `skills_matrix`) |

The scope comes from the freshness verdict and the curator's recommended next action — never from a
default and never from convenience. An index left out of the scope is named in `run.md` as
deliberately untouched, so "not rebuilt" never reads as "forgotten".

This flow has no user-registered stages. The active validation set of `user-context` belongs to the
CV flows; no validator runs here.

### Intermediate directories

| Directory | Holds | Rules |
|---|---|---|
| `<run>/work/` | Build byproducts: the raw output of the freshness script, the coverage-pass worksheet, and any source content fetched through the fallback reader because the shell could not read it. | Byproducts, not artifacts: nothing here is a contract instance, nothing here is a canonical source, and no later run may read it. Listed in the run's artifact index as byproducts. |

## Inputs

What one run of this flow is given. An index, not a second home for rules: each row points at the
section that owns it. This flow hardcodes no path and infers nothing from repository layout.

| Input | Contract / description | Required |
|---|---|---|
| `run_id` | the refresh date, built as *Run identifier and output layout* above defines it | required |
| user context | contract `user-context`, resolved at step 1 through the declared order. *User-context settings* below states what this flow reads from it. | required |
| canonical experience sources | the resolved source set — files, directories, URLs, descriptions, dictated content. The **only** input to the rebuild; an empty list stops the flow with a question at step 1. | required |
| `bank_dir` | the knowledge bank directory (contract `knowledge-bank`), passed to the curator as an explicit parameter and created at step 2 if it does not exist | required |
| `report_paths` | reports carrying `## Constraint proposals` that were never ingested — a CV run whose closing step was interrupted, say. Passed through to step 9. | optional |

The rebuild scope is **not** an input: it is decided at step 5 from the freshness verdict and the
curator's recommended next action, never from a default and never from convenience.

## Steps

`executor` is the `role.capability` that runs the step, or `flow` for orchestration the flow does
itself. Every path a role receives is passed explicitly by the flow.

| # | Step | Executor | Contract | Paths passed | Gate |
|---|---|---|---|---|---|
| 1 | Resolve user context | `flow` | `user-context` | — | G1 |
| 2 | Scaffold the run and seed the manifest | `flow` | `run-manifest` | `<run>/run.md` | — |
| 3 | Check freshness | `knowledge-bank-curator.check-freshness` | — (verdict returned) | `sources`, `bank_dir` | G2 |
| 4 | Resolve unreadable sources | `flow` | — | the per-source statuses from step 3 | G1 |
| 5 | Decide the rebuild scope | `flow` | — | the verdict and next action from step 3 | — |
| 6 | Rebuild the bank | `knowledge-bank-curator.build-banks` | `knowledge-bank` | `sources`, `bank_dir`, `scope`, `constraints_ledger` (read-only), `run_id` | G3, G4, G5 |
| 7 | Append the refresh log | `knowledge-bank-curator.build-banks` | `knowledge-bank` | `<bank-dir>/refresh_log.md`, the build summary of step 6 | G6 |
| 8 | Verify the written bank | `flow` | — | `sources`, the rebuilt index paths | G7 |
| 9 | Ingest constraint proposals | `knowledge-bank-curator.maintain-constraints` | `constraints-ledger` | `report_paths`, `direct_proposals`, `constraints_ledger`, `bank_dir`, `run_id` | G8 |
| 10 | Close the manifest | `flow` | `run-manifest` | `<run>/run.md` | — |

Steps run in order; this flow declares **no parallel groups**. The build is one indivisible operation
over the whole source set, and every later step depends on its outcome.

### 1. Resolve user context

Resolve the canonical experience sources per contract `user-context`, in its order:

1. the harness-native local agent rules file;
2. any other context or memory the harness provides;
3. **ask the user.**

Nothing else may supply a source. This flow hardcodes no path, carries no default source list, and
infers nothing from the repository layout — if the resolution order yields nothing, the correct
outcome is a question to the user, not a guess.

Validate what came back, per the preflight rules of the user-context contract:

- the source list is non-empty — an empty list stops the flow with a question; the supported fix is
  `setup-master.bootstrap` (first run) or `setup-master.update-settings`;
- each entry is classified as *time-checkable* (a file or directory path) or not (a URL, a
  description, dictated content). Both kinds are canonical; only the first can be compared by
  timestamp;
- anything ambiguous is asked about, never interpreted.

Record in `run.md` `## User context`: which resolution supplied the values, and the resolved snapshot
itself. That snapshot is what makes the refresh reviewable later.

### 2. Scaffold the run and seed the manifest

Create `<run>/` and `<run>/work/`, and write `run.md` per contract `run-manifest` with
`status: in-progress`, `producer: flow:refresh-knowledge-bank`, the flow version, the resolved
context snapshot, the step checklist of this table, and the gate list below. The manifest is written
as the run proceeds — a manifest reconstructed at the end cannot support resuming or blocking.

Create `<bank-dir>` if it does not exist. An existing bank is never deleted, only rewritten file by
file.

### 3. Check freshness

Invoke `knowledge-bank-curator.check-freshness` with the resolved sources and the bank directory.
Keep the script's raw output in `<run>/work/` and record the verdict, the per-source statuses and the
per-index statuses in `run.md` `## Bank freshness`.

A `fresh` verdict on a run the user asked for is still worth reporting: it is a legitimate outcome
("nothing changed"), and the flow completes at step 10 without a rebuild — after recording why.

### 4. Resolve unreadable sources

See *Unreadable sources* below. Nothing proceeds past this step with an unresolved `unreadable`
source.

### 5. Decide the rebuild scope

| Verdict / situation | Scope |
|---|---|
| bank missing, or any index missing | `full` |
| an index lacks its `## Source Metadata` block | `full` |
| the bank carries no `## Candidate` section — a legacy import, or another flow routed here because the section it needs is absent | `full`; the build derives the section, whatever the timestamps say |
| a source the bank has never seen | `full` |
| one changed source with a clearly bounded effect, and the curator recommends a partial refresh naming the sections | `partial`, with the sections named explicitly |
| `fresh`, and the user asked for a refresh anyway | `full` (an explicit user request outranks the timestamps) |
| `fresh`, and the flow was reached from another flow's stale check that has since resolved | none — record and close |

When in doubt, rebuild fully. A partial refresh that mis-guesses its blast radius leaves the bank
internally inconsistent, and the inconsistency is invisible.

Record the chosen scope and its justification in `run.md`.

### 6. Rebuild the bank

Invoke `knowledge-bank-curator.build-banks` with the resolved sources, the bank directory, the scope,
the constraints ledger (read-only), and the run id.

The capability owns the rules; the flow owns only the gates it must see green before continuing:

- **G3 self-check** — every entry carrying a specific claim was located in a source passage, and was
  corrected, tagged `(inferred from …)`, or removed when it could not be;
- **G4 coverage pass** — every substantial piece of evidence in every source has a corresponding
  entry, including every education, certification and awards section, and every position's location
  and dates at the source's own granularity;
- **G5 source metadata** — every rebuilt file carries a `## Source Metadata` block naming the sources
  it was prepared from, their modification timestamps where they have any, and whether this was a
  full or a partial refresh (a partial one naming the sections rebuilt and those deliberately left
  untouched).

Neither gate is skippable on the grounds that the build was done carefully. A build that cannot close
them reports the open items; the flow records them in `run.md` `## Open questions` and does not
pretend the bank is complete.

The build summary comes back to the flow: sources used with their read status, sections rebuilt, the
coverage result, open questions, and any `## Constraint proposals` the build raised. Step 9 ingests
those; the flow never writes the ledger itself.

### 7. Append the refresh log

The refresh log is a bank file, so it has the same single writer as every other bank file: the flow
passes `<bank-dir>/refresh_log.md` to the same `build-banks` invocation, and the curator appends one
entry from the build summary — date, scope (full or partial, and which sections), the sources seen
with their modification timestamps, what changed, which corrections were made and why, and what
triggered the refresh.

The log is append-only. An entry is never rewritten: a wrong entry is corrected by a later entry that
says so. **G6** is the entry existing and naming this run.

### 8. Verify the written bank

The flow's own check that the rebuild did what it claims — cheap, and it catches a build that wrote
to the wrong place or left an index behind:

1. re-run `check-freshness` over the same sources and the rebuilt indexes; the expected verdict is
   `fresh` (or `unknown` when a non-time-checkable source is in play — never `stale`);
2. confirm each rebuilt file against contract `knowledge-bank`: the envelope, the
   `## Source Metadata` block, the mandatory sections of that file kind, and the closing
   `## Conservative Gap Notes`;
3. confirm the scope: every index in scope was rewritten, and every index out of scope is unchanged.

A failure here is a **red gate (G7)**, not a warning. Report what is wrong, and either re-run step 6
with the corrected scope or stop and ask the user.

### 9. Ingest constraint proposals

Close by invoking `knowledge-bank-curator.maintain-constraints` — the only writer of the ledger —
with:

- `direct_proposals`: the `## Constraint proposals` of this run's build summary, plus anything the
  user stated during the run;
- `report_paths`: any report the user named as carrying proposals that were never ingested — for
  example a CV run whose closing step was interrupted;
- `constraints_ledger`, `bank_dir` (read-only), and this `run_id`.

Conservative proposals — an absence the build established, a cap on a claim, a factual limitation —
are applied without asking the user. Everything else becomes a recorded question. Nothing to ingest
is a success, not a defect: the ledger is left untouched and the run reports "no proposals".

**G8** is the ingestion having run and its summary being recorded — including the questions it raised
for the user.

### 10. Close the manifest

Fill `run.md`: final step statuses, gate states, the artifact index (the run report, every bank file
touched with its revision, and `<run>/work/` marked as byproducts), and the open questions. Set
`status: complete` only when the definition of done below is met; otherwise `blocked` (a decision is
needed) or `fail`, with the reason.

A `complete` manifest with a red gate or an unresolved open question is a defect.

## Unreadable sources

A canonical source can be present and still yield nothing. Two causes, both ordinary:

- **a permissions boundary the shell cannot cross** — the harness's shell is sandboxed, or the
  operating system gates the folder behind a privacy permission the shell does not hold;
- **a cloud-synced placeholder** — the file is listed with a plausible name, size and modification
  time, but its content has been evicted to the provider and has to be fetched before it can be read.

Both look identical to a timestamp comparison, and both are dangerous in exactly the same way: a
source dropped from the comparison makes a stale bank look fresh, and a bank built from a partial
source set looks complete while silently missing evidence.

The freshness script therefore reports `unreadable` **per source** — it probes for readable bytes,
not just for a modification time — and it neither crashes nor guesses. Resolving it is this flow's
job, in this order:

1. **Retry through the harness's own file tools.** They frequently reach what the shell cannot: a
   different permission context, and a reader that triggers the cloud provider's fetch. If the
   content comes back, treat the source as `ok`, use the timestamp the script reported, and note in
   `run.md` that the fallback reader was used for that source. Content fetched this way may be kept
   in `<run>/work/` for the duration of the build; it is a byproduct, never a canonical source.
2. **Ask the user.** Name the source, quote the reason the script gave, and ask for exactly one of:
   make the content available (fetch it, grant the access), point at a reachable copy, or remove the
   entry from their context. Record the answer in `run.md`.
3. **Never a fourth option.** Do not skip the source quietly, do not treat "the other sources were
   fine" as good enough, and do not let the flow crash on it. An unresolved `unreadable` source stops
   the flow with `status: blocked` and the question recorded — the bank stays as it was, which is a
   recoverable state; a bank rebuilt from a partial source set is not.

The same ladder applies to a source that reads as empty or visibly truncated: treat it exactly as
unreadable. It also applies at build time, not only at the freshness check — a source that was
readable in step 3 and unreadable in step 6 gets the same treatment.

Sources that are not files — URLs, descriptions, dictated content — are never `unreadable`; they are
`not-time-checkable`, judged by their record in the bank's source-metadata block. A source absent
from that block has never been seen by the bank, and that alone makes the verdict `stale`.

## Gates

| Gate | Requires | Evidenced by |
|---|---|---|
| G1 sources resolved | User context resolved through the declared order; the source list non-empty; every source readable or explicitly settled with the user. | `run.md` `## User context`, `## Bank freshness` |
| G2 freshness decided | A verdict with per-source and per-index status. `unknown` is a decided verdict; an undecided one is a red gate. | `run.md` `## Bank freshness` |
| G3 self-check | Every specific claim traced to a source passage, or tagged inferred, or removed. | build summary in `run.md` |
| G4 coverage pass | Every substantial piece of evidence has an entry; positions, education and certifications confirmed section by section. | build summary in `run.md` |
| G5 source metadata | A `## Source Metadata` block in every rebuilt file, naming sources, timestamps and refresh status. | the bank files |
| G6 refresh log | One appended entry for this run. | `<bank-dir>/refresh_log.md` |
| G7 bank verified | Post-write freshness re-check not `stale`; structure conforms to the contract; scope respected. | `run.md` step 8 notes |
| G8 ledger closed | `maintain-constraints` ran; its summary and any pending questions recorded. | `run.md`, `<bank-dir>/constraints.md` |

## Definition of done

- Every gate green in `run.md`, or explicitly waived by the user with the reason recorded.
- Every canonical source was read, or its unreadability was settled with the user — never silently
  skipped.
- Every rebuilt index carries its source metadata; every index left out of scope is named as
  deliberately untouched.
- The refresh log has this run's entry.
- The ledger ingestion ran, and its questions (if any) are in `## Open questions`.
- `run.md` has `status: complete` and no unresolved question.

## Escalation

Stop and ask the user — recording the question in `run.md` `## Open questions` and setting
`status: blocked` — when:

- no canonical sources could be resolved, or the resolved list is empty;
- a source stays unreadable after the fallback ladder below;
- a source is empty or visibly truncated;
- sources conflict on a fact (dates, titles, employers, scale) — the curator records both readings;
  the flow does not pick one;
- candidate identity cannot be derived for the `## Candidate` section;
- the constraints ledger is unreadable or malformed — the run stops rather than starting a new
  ledger: losing accumulated guardrails is worse than a failed closing step;
- the coverage pass cannot be closed and the missing evidence cannot be recovered from any source.

## Usage

`setup-master.register-with-harness` makes this repository's skills discoverable by the harness in
use. **Where registration succeeded, the flow is invoked by name:**

> run `refresh-knowledge-bank`

**Invocation by path is valid everywhere and is the fallback.** Registration may never have been run,
the user may have declined it, and the harness in use may have no discovery location for skills at
all — all ordinary outcomes, and then by-path is the whole of it. Point the agent at this file, whose
location the skills index gives for the name `refresh-knowledge-bank`.

An adapter is never authority. However the flow was reached, the executing agent reads this file, and
the loading rule in `AGENTS.md` — with its role-side reasoning in `role-conventions` — governs what
else a step's executor opens. This flow points at that rule rather than keeping its own copy: a rule
with several homes ages at different rates, and the copy an agent happens to read is the one it
obeys. On a harness with subagents the steps still run in order: this flow declares no parallel
groups, and the result must not differ between harnesses.

Before the first run the user's context must exist. If it does not, the correct outcome of preflight
is a question, and the supported answer is `setup-master.bootstrap`, which creates the harness-native
local rules file from the section template in contract `user-context`.

## User-context settings

**This skill recognizes no per-skill settings keys**, so this section carries no key table — the
shape `skill-conventions` prescribes for a skill with nothing to declare. A `## Skill settings`
subsection named after this skill in the user's local rules file has no meaning; report it as
unrecognized rather than interpreting it.

The table below is **not** a key declaration. It indexes the sections of contract `user-context` this
flow reads, and what it does with each:

| Item | Contract section | Use |
|---|---|---|
| Canonical experience sources | `## Experience sources (canonical)` | Required. The only input to the rebuild. Resolved at preflight through the declared order; never defaulted, never hardcoded here. |
| Additional rules | `## Additional rules` | Optional free text the flow honours, so long as it does not weaken truthfulness, the sole-writer rule, or run isolation. |

The active validation set is **not** used by this flow: no validator runs during a bank refresh.

## Dependencies

| Name | Kind | Needed for | Required / optional | When unbound |
|---|---|---|---|---|
| Read access to the canonical experience sources | capability | Reading every source at the freshness check and again at build time. | required | Follow the fallback ladder in *Unreadable sources*: retry with the harness's file tools, then ask the user. A source that stays unreadable blocks the rebuild — the flow records `status: blocked` and leaves the existing bank untouched. It never builds from a partial source set. |
| Harness-native file read tool (a reader independent of the shell) | capability | The first rung of that ladder: reaching a source the sandboxed shell cannot open, and forcing a cloud-synced placeholder to be fetched. | optional | Skip straight to asking the user, and note in `run.md` that no fallback reader was available. |
| `python3` ≥ 3.10 | tool | Running the bundled freshness script that `knowledge-bank-curator.check-freshness` invokes, at steps 3 and 8. | optional | The curator compares timestamps and content presence with the harness's own file tools, following the same rules, and notes in `run.md` that the check was done manually. A missing script runtime never fails this flow. |
| A question channel to the user | capability | Every escalation in this flow is a question, not a decision: empty context, unreadable sources, conflicting sources, undeliverable identity, a non-conservative constraint proposal. | required | The flow records the question in `run.md` `## Open questions`, sets `status: blocked`, and stops. It never answers its own question. |
| Web search | capability | The curator's external validation of inferred capability and pattern names while building the skills matrix. | optional | Those entries stay marked `unverified name`; the build continues and reports the skipped sub-step. Evidence is never dropped for lack of a search tool. |

Concrete bindings for these live in the user's harness configuration, not here. Unbound entries are
aggregated and reported by `setup-master.check-environment`.
