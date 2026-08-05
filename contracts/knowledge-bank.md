# Contract: knowledge-bank

Version: 1.0

## Purpose

The knowledge bank is the persistent, cited cache of everything the canonical experience sources say
about the candidate. It exists so that every later step — evidence mapping, writing, fact-checking,
fit scoring — can work from pre-vetted, traceable material instead of re-reading the raw sources.

The bank is a **cache, not a curated selection**. Relevance is decided per run, downstream. Anything
present in a canonical source but missing from the bank is invisible to every consumer and will not
be used.

## File set

The bank is a set of files, each an instance of this contract:

| File | Role |
|---|---|
| experience bank | Themed, bullet-ready evidence statements, plus candidate identity, employment history, education and certifications. |
| projects index | One entry per significant body of work: context, role, deliverables, stack, impact, evidence. |
| skills matrix | Capability index with evidence context, conservative level signals and safe-use constraints. |
| refresh log | Append-only history of bank builds and refreshes. |

The constraints ledger lives beside these files but is governed by its own contract
(`constraints-ledger`) and is written by a different capability.

Placement is not defined here. The flow passes the bank directory to roles as an explicit parameter.

## Status values

- `current` — the live version of the file (contract-defined value).

Every rebuild or targeted refresh increments `revision:` and updates `updated:`. There is no `draft`
state: a partially built bank file is never saved over a good one.

## Envelope

The common envelope of `contracts/README.md` applies, with:

- `run_id: n/a` — the bank outlives runs;
- `producer: knowledge-bank-curator.build-banks`;
- `inputs:` — every canonical source read, as `<source locator> — canonical experience source`.

**Legacy import.** Bank files imported from a predecessor structure may lack the envelope and the
`## Candidate` section. They stay valid and readable until the first refresh, which adds both. A
consumer that needs identity from a bank without `## Candidate` asks the user or requests a refresh
instead of guessing.

## Shared rules (all bank files)

- **Source of truth.** Canonical experience sources decide every fact. The bank never overrides them;
  a correction is only allowed when the constraints ledger or the user documents it explicitly.
- **Completeness mandate.** Do not drop evidence for being minor, unlikely to be used, or irrelevant
  to a current target. Every substantial piece of evidence in a canonical source has a corresponding
  entry.
- **One claim per entry.** Two separate facts are never merged to make a single entry sound stronger.
- **Conservative verbs.** `built`, `designed`, `implemented`, `contributed to`, `supported`,
  `collaborated on`. `led`, `owned`, `architected` appear only when a canonical source uses that
  language.
- **Citations are mandatory.** Each entry names the canonical source (and section, where the source
  has sections) it was drawn from. An entry whose supporting passage cannot be located is corrected,
  tagged as inferred, or removed.
- **Inference is tagged.** Anything derived rather than read carries `(inferred from <source
  section>)` inline.
- **Numbers as stated.** Metrics, scale numbers and dates are copied, never interpolated, rounded up
  or reconstructed.
- **Date granularity.** Month-level when a canonical source gives months; never invent a month to
  make a range look precise.
- **Location granularity.** City **and** country when a canonical source gives them. Coarsening
  (country only, when the source names the city) is a defect.
- **Internal names.** Company-internal product and system names are recorded with a short
  public-facing class description; where the mapping is imperfect, the difference is recorded as a
  safe-use constraint on that entry.
- **Conservative Gap Notes.** Every bank file closes with a `## Conservative Gap Notes` section
  listing what is clearly absent from, or explicitly constrained by, the canonical sources. This
  section is as load-bearing as the positive evidence: it stops weak evidence being stretched later.

## `## Source Metadata` (every bank file, at the top)

```markdown
## Source Metadata
- Last updated: <timestamp>
- Prepared from: <source locators or input names>
- Source modification timestamps: <source>: <timestamp>
- Refresh status: <full refresh | partial refresh — which sections or entries>
```

Refresh status is specific: a partial refresh names the sections or entries it touched, and what was
deliberately left untouched.

## Sections of the experience bank

### `## Candidate` (mandatory, new in this contract)

Identity facts derived from the canonical sources: the candidate's full name as the sources state it,
and any other identity-level facts the sources carry (contact handles, location, work-authorization
statements). Each fact cited; nothing inferred; no fact created here that no source states.

Flows read export-naming identity from this section. It is **not** a user-context item — it is
derived, like everything else in the bank.

### Themed evidence sections

One `##` section per theme, with themes chosen from the evidence actually found — never from a fixed
list. Each section holds standalone bullets.

Bullet shape: **action + scope or context + outcome or impact**, where supported. Each bullet is
intelligible without the surrounding source text, carries one verifiable claim, and includes concrete
numbers, dates and scale context when the source provides them.

Both **explicit** evidence (facts, outcomes, technologies, scale, before/after measurements) and
**implicit** evidence (recurring delivery behaviour, design and documentation discipline, cross-team
coordination patterns, test and quality practice, review and ownership behaviour, performance and
reliability approach, security and compliance practice) belong here; implicit entries carry the
`(inferred from …)` tag.

### `## Positions (employment history)` (mandatory)

Position metadata is first-class, never left to be inferred from thematic bullets. One entry per
role, each stating exactly what the canonical source states: job title, company, location (city,
country), start and end dates.

Every role from the canonical sources appears — including freelance and self-education periods, and
including roles already referenced by thematic bullets.

### `## Education` (mandatory)

Every education entry from every canonical source: exact title or degree, institution, location,
dates. A degree that is not stated is never inferred.

### `## Certifications` (mandatory)

Certifications, licenses and awards as stated. When the canonical sources contain none, the section
is present and says so explicitly, and the absence is also recorded in the Conservative Gap Notes —
so a consumer can tell "checked, none exist" from "never looked".

## Sections of the skills matrix

Entries are grouped by capability group, with groups chosen from the evidence found. Groups are never
limited to programming languages and tools: technical skills, applied architectural patterns with
production evidence, engineering practices, reliability and delivery practices, security and
compliance, domain knowledge, collaboration and operating style, and language skills all belong when
evidence supports them.

Each entry carries:

- the **evidence context** — which employer, project or situation supports it;
- a **conservative level signal** — `strong evidence` / `moderate evidence` / `limited evidence` /
  `surface-level familiarity` / `no evidence`. No numeric ratings. When evidence is ambiguous, the
  lower label wins.
- **safe-use constraints** — what must not be claimed when this entry is used.

An entry captured as inferred carries the `(inferred from …)` tag. When such an entry uses the name
of an established industry concept, it also records that the described work matches that concept's
definition, and notes any commonly confused neighbouring concept as a constraint.

## Sections of the projects index

One `##` section per project. A project is a body of work with a distinct goal, scope and outcome,
long enough to have produced verifiable evidence, and likely to be discussed as a unit. Freelance
work, self-education periods and part-time contributions qualify when concrete evidence exists.
Minor one-off tasks belong in the experience bank as bullets — but never nowhere.

Each entry carries: **Context** (what existed, what was wrong, the goal, why it mattered, scale or
domain context) · **Candidate role** (precisely what was owned or contributed — a contributor entry
must not read as sole ownership) · **What was built** (concrete deliverables) · **Technologies**
(public-facing names or class-mapping descriptions) · **Impact** (measured when the source measures
it, qualitative otherwise, never invented) · **Evidence** (source and section).

Entries state the time period when the source gives one, and state current state explicitly for
work in progress: what is complete, what is pending, whether it reached production. Two projects are
never merged into one entry; one continuous project is never split unless the source itself treats
its phases as having separate goals and outcomes.

## Sections of the refresh log

Append-only. One entry per build or refresh, newest first or last consistently within the file, each
recording: date, scope (full or partial, and which sections), the sources seen with their
modification timestamps, what changed, which corrections were made and why, and what triggered the
refresh. Entries are never rewritten — a wrong entry is corrected by a new entry that says so.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | `knowledge-bank-curator.build-banks` |
| Consumers | `knowledge-bank-curator` (query, freshness, feedback, constraints), `experience-writer`, `vacancy-analyst`, `reviewer` |

The bank has a **single writer**. No other role writes it under any circumstance; observations that
would change it travel as a `bank-update-brief` (questions for the user) or as constraint proposals
(ingested into the ledger by the curator).
