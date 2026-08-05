# Capability: knowledge-bank-curator.build-banks

## Purpose

Rebuild the knowledge bank from the candidate's canonical experience sources: the identity section,
the thematic experience bullets, the employment/education/certification records, the project index,
and the skills matrix — each entry conservative, citable, and complete. This is the ETL step of the
bank refresh flow and the only capability that writes the bank indexes.

## Inputs

| Input | Contract / description | Required |
|---|---|---|
| `sources` | The resolved canonical experience sources — paths, URLs, or descriptions, in the order the caller gives them. | required |
| `bank_dir` | Directory the bank files are written into. | required |
| `scope` | `full` (rebuild every index) or `partial` with the explicit list of sections/entries to rebuild. Default `full`. | optional |
| `constraints_ledger` | The constraints ledger, read-only: documented corrections and confirmed absences. | optional |
| `run_id` | Run identifier for the envelope of the produced files. | required |

## Outputs

| Output | Contract | Status values |
|---|---|---|
| The bank index files in `bank_dir` (`experience_bank.md`, `projects.md`, `skills_matrix.md` — names fixed by the contract) | `knowledge-bank` | `complete`, `blocked` |
| The refresh log at `<bank_dir>/refresh_log.md`, when the caller passes it: one appended entry per refresh, written from the build summary | `knowledge-bank` | `complete` |
| A build summary returned to the caller: sources used with their read status, sections rebuilt, coverage-pass result, open questions | (returned inline; the flow records it in its run report) | — |

The build summary carries a `## Constraint proposals` section when the build discovered a durable
factual limitation. Proposals are not applied here — the ledger has its own writer.

## Procedure

1. **Read every source in full, first.** Do not start writing until all sources have been read. A
   source that cannot be read is handled under *Failure and skip conditions* — never silently
   skipped, because a bank built from an incomplete source set looks complete and is not.
2. **Read the constraints ledger**, when one was passed. Documented corrections and confirmed
   absences constrain what may be written; a canonical source that contradicts a ledger entry is a
   conflict to record and escalate, not to resolve.
3. **Derive the `## Candidate` section**: the candidate's full name and comparable identity facts
   (professional headline, location, contact handles) exactly as the sources state them, each with
   its citation. Never normalise, translate, transliterate, or complete a name beyond what a source
   shows; if two sources spell it differently, record both spellings and mark the conflict. An
   identity fact absent from every source is written as `unknown`. Downstream flows read export
   naming identity from this section, so its accuracy is not cosmetic.
4. **Build the experience bank** — thematic bullets, plus the first-class record sections
   (positions, education, certifications). See *Experience bank* below.
5. **Build the project index.** See *Project index* below.
6. **Build the skills matrix**, then run its dedicated second pass and the external validation of
   inferred names. See *Skills matrix* below.
7. **Self-check every file** against the sources (mandatory gate, below).
8. **Coverage pass** across every source, section by section (mandatory gate, below).
9. **Write the source metadata block** at the top of each file: the sources used, their modification
   timestamps where they have any, and whether this was a full or a partial refresh.
10. **Report** the build summary to the caller, including everything the coverage pass could not
    close and every question for the user.

## Rules

### Source of truth

The canonical sources are the truth for candidate facts. The bank is derived and must not override
them; the only exceptions are corrections documented in the constraints ledger or given explicitly
by the user. Nothing enters the bank that is not in a source — no facts, no metrics, no employers,
no dates, no titles, no degrees, no certifications, no achievements.

### Completeness mandate

The bank is a **cache of the canonical data, not a curated selection**. Everything downstream —
evidence retrieval, document writing, fit scoring — can only see what the bank contains: evidence
absent from the bank does not exist as far as the rest of the system is concerned.

Therefore: do not exclude evidence for being minor, unlikely to be used, or irrelevant to any
current vacancy. Relevance is decided at query time. The bank's job is to preserve everything; the
selecting is somebody else's job.

### Experience bank

A library of reusable, fact-checked, bullet-ready statements. Its job is recall: pre-vetted material
that can be adapted without re-reading the sources.

Organise bullets by theme, choosing themes that reflect the evidence actually found rather than a
fixed template. Capture:

- **Explicit evidence** — facts, outcomes and actions stated directly: technologies used, systems
  built, scale numbers, dates, specific improvements with before/after measurements.
- **Implicit evidence** — patterns and practices that recur across projects, or that describe *how*
  the work was done rather than *what* was built. Look for: recurring delivery behaviours (gradual
  rollout, observability-first, feature-flagged releases, cutover coordination); design and
  documentation discipline (diagrams before coding, PR templates, runbooks, architecture reviews);
  cross-team coordination (escalation, domain-owner collaboration, handoffs, driving tickets in
  adjacent teams); test and quality practice (fixture builders, parametrised test modes, mock
  infrastructure, end-to-end setup, ephemeral per-change environments); review and ownership
  behaviour (mandatory approvals, review focus areas, onboarding support); performance and
  reliability engineering (profiling workflow, benchmark practice, before/after measurement, staged
  rollout); security and compliance practice (access-control design decisions, auth patterns,
  sensitive-data filtering, audit trails).

Bullet quality rules:

- Each bullet is a complete, standalone statement, intelligible without the surrounding source text.
- Pattern: action + scope or context + outcome or impact, where the source supports an outcome.
- **Conservative verbs**: built, designed, implemented, contributed to, supported, collaborated on.
  Use *led*, *owned* or *architected* only when a source uses that language explicitly.
- Include concrete numbers, dates and scale context when a source provides them. Never invent,
  round, or interpolate a metric.
- Something implied rather than stated gets `(inferred from <source section>)`.
- One verifiable claim per bullet. Never merge two facts to make a combined bullet sound stronger.
- Close the file with **Conservative Gap Notes**: experience categories clearly absent from the
  sources. This section prevents later stretching of weak evidence and is as important as the
  positive entries.

### Positions, education, certifications — first-class records

Header metadata (exact job title, company, location, dates) and standalone credentials are neither
thematic bullets nor projects, so they are the material that gets lost: it survives only by accident,
when a city or a date happens to appear inside a narrative. Capture it deliberately.

- Maintain a `## Positions (employment history)` section with one entry per role, stating exactly as
  the source does: job title, company, **location as city and country**, and start/end dates at
  **month level whenever the source gives months** (never invent a month).
- Include every role, freelance and self-education periods included, even when thematic bullets
  already mention the same employer.
- Maintain `## Education` and, when the sources have any, `## Certifications` sections: exact
  title/degree, institution, location and dates as stated. Never infer a degree that is not stated.
  Awards and licences belong here too, not scattered through thematic bullets.
- Coarser data than the source has is a **completeness defect**, not a simplification: a country
  where the source says city and country, a year where the source gives a month.
- If a source has no education or certification content at all, add none — and record the absence in
  the Conservative Gap Notes, so it reads as *checked*, not *overlooked*.
- Never rely on bullets or project narratives to carry title, company, location or dates. Those
  carry evidence; this section carries the record.

### Project index

One entry per body of work that had a distinct goal, scope and outcome, lasted long enough to
produce independently verifiable evidence, and is likely to be discussed as a unit. Freelance work,
self-education periods and part-time contributions qualify when there is concrete evidence worth
recalling. Minor tasks and one-off fixes are not projects — they belong in the experience bank as
bullets, and they are never dropped from the bank system entirely.

Each entry captures:

- **Context** — the problem that motivated the work: what existed, what was wrong or missing, the
  goal, why it mattered, plus scale or domain context when the source gives it.
- **Candidate role** — precisely what was owned or contributed (primary author, contributor,
  co-owner, architectural ownership on one side). Never inflate beyond the source.
- **What was built** — the concrete deliverables that exist as a result.
- **Technologies** — the stack, using public-facing names or class-mapping descriptions for internal
  tools.
- **Impact** — measured outcomes when the source has them; otherwise the qualitative change. Never
  invent a metric.
- **Evidence** — which source and section this entry comes from. Required, for later validation.

Entry rules: preserve the real role (a contributor entry must not read like sole ownership); state
the current state of unfinished work explicitly (what is done, what is pending, whether it reached
production); include the time period when the source gives it; never merge two projects, and never
split one continuous project unless the source itself treats the phases as separate goals.

### Skills matrix

A capability index with evidence notes and conservative level guidance. Its job is to make the full
breadth and depth visible — not only named technologies, but applied patterns, engineering
practices, domain knowledge and working behaviours.

Organise by capability group, chosen from the evidence found; do not limit the groups to languages
and tools. The classic failure mode is capturing the tools named in a stack while missing the
capabilities the work actually demonstrated. Cover:

- **Technical skills** — languages, frameworks, databases, infrastructure. For each: the evidence
  context (which employer, which project type) and the important constraints (for example "an
  internal platform equivalent, not direct public-cloud ownership").
- **Applied architectural patterns** — patterns used in production, evidenced by how a system was
  designed, not by a keyword list. Capture only patterns with concrete project evidence.
- **Engineering practices** — repeating behaviours across projects: design-first work,
  observability-first delivery, rollout discipline, structured documentation, test infrastructure
  design, performance engineering approach.
- **Reliability and delivery practices** — service-level objective design, alerting strategy,
  release engineering, on-call ownership, incident response, with scale context when available.
- **Security and compliance** — access-control decisions, service-to-service auth, identity
  integration, sensitive-data handling, audit trails. Capture the decision made, not just the tool.
- **Domain knowledge** — the business domains with production depth. Distinct from technical skills:
  what the systems do, not how they are built.
- **Collaboration and operating style** — cross-team coordination, domain-owner collaboration,
  review ownership, mentoring. Only behaviours with concrete evidence; no generic soft-skill labels.
- **Language skills** — level label plus any practical work-context evidence.

Each entry states the evidence context, a conservative level signal (strong evidence / moderate
evidence / limited evidence / surface-level familiarity / no evidence), and any constraints or
safe-use notes — what must *not* be claimed on the strength of this entry. **No numeric ratings**,
and ambiguity always resolves to the more conservative label.

A capability demonstrated by how the work was described rather than by an explicit claim is captured
with `(inferred from <source section or project name>)`. This matters most for architectural
patterns and engineering practices, which candidates rarely label as skills themselves.

Close the file with conservative gap notes: capabilities clearly absent or explicitly constrained by
the sources.

**Second pass — patterns and practices.** After the first build, go over the sources again with one
question per section: *what architectural patterns, engineering practices and working behaviours
does this description demonstrate, even though it never names them?* Read for structural decisions
(how a system was decomposed, how a migration was phased, how failure was isolated) → patterns;
repeating delivery behaviour → practices; how observability, testing, documentation and rollout were
handled → working style. Add whatever the first build missed.

**External validation of inferred names.** Building the bank is a heavy operation where extra
research is justified. For every capability captured as inferred — named architectural patterns and
engineering practices above all — validate before finalising the entry:

1. confirm the name is an industry-recognised concept with an established definition;
2. verify that the described work genuinely exemplifies it, rather than merely borrowing its
   vocabulary — check the definition against what was actually built;
3. for an internal tool mapped to a public equivalent, confirm the mapping is accurate and note the
   differences that should constrain how the equivalence may be used;
4. if the name is commonly confused with a different concept, record the distinction in the entry's
   constraints.

Validation does not require finding the candidate's own work externally — only that the concept is
real and that the work matches its definition. When the research capability is unavailable, keep the
entry and mark it `unverified name`; never drop evidence for lack of a search tool.

### Self-check (mandatory gate)

After building each file, verify it against the sources before saving. For **every entry containing
a specific claim** — a metric, a date, a scale number, a role description, an ownership level, a
before/after improvement — locate the exact passage that supports it. If the passage cannot be found,
or the entry says more than the passage does:

- correct the entry to match the passage, or
- add `(inferred from <source section>)` when the claim is reasonable but implicit, or
- remove the entry when it has no basis in any source.

This gate is not skippable on the grounds that the build was done carefully.

### Coverage pass (mandatory gate)

Read through each source section by section and confirm that every substantial piece of evidence has
a corresponding entry somewhere in the bank. Explicitly confirm that every education, certification
and awards section of every source has a matching section in the bank, and that every position's
location and dates match the source at the source's own granularity. Anything missing is a
completeness defect: fix it before finishing, or — if it cannot be fixed — report it as an open item.

### Source metadata

Every file gets, on every refresh, a block recording: the timestamp of the build; the sources it was
prepared from; the modification timestamp of each source that has one (sources without a timestamp —
URLs, descriptions, dictated content — are listed with `no timestamp` and the date they were last
confirmed with the user); and the refresh status (full, or partial with the sections rebuilt).

### Partial refreshes

A partial refresh rewrites only the named sections and leaves everything else byte-for-byte intact.
It never removes content it did not rebuild, and it updates the source metadata to say *partial* and
which sections. When in doubt about the blast radius of a change, do a full rebuild.

## Failure and skip conditions

- **A source cannot be read.** Try the fallback reader (the harness's own file tools may reach what
  the shell cannot; cloud-synced storage may keep an on-disk stub whose real content has to be
  fetched). If it is still unreadable, **stop and ask the user**. Do not write a bank from a partial
  source set: the result is indistinguishable from a complete one and silently loses evidence.
- **A source is empty or visibly truncated** — treat exactly as unreadable.
- **Sources conflict** on a date, title, employer or scale — record both readings with their
  citations, mark the conflict in the entry, and ask the user. Never pick one silently.
- **Identity cannot be derived** — write the `## Candidate` section with `unknown` for the missing
  facts, report it, and ask the user; do not invent a spelling.
- **The research capability is unavailable** — inferred names stay marked `unverified name`; the
  build continues and reports it. This is a SKIPPED sub-step with instructions, never a failure.
- **The ledger contradicts a canonical source** — do not resolve it here; record the conflict and
  escalate.
- **The bank directory does not exist** — create it; an existing bank is otherwise never deleted,
  only rewritten file by file.
