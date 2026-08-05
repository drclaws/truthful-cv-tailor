# Contract: cv-document

Version: 1.0

## Purpose

A CV document is the candidate-facing deliverable in text form: a plain, linear, machine-readable
markdown document that a renderer can turn into the final file and a reviewer can check claim by
claim.

**This contract owns the CV format.** Every structural and formatting rule of the CV lives here, so
that the writing role stays document-format-agnostic and can be reused for other document kinds, and
so that a reviewer and a renderer read the same definition of "correct" that the writer wrote
against.

## Status values

- `draft` — written, not yet cleared by the run's checks;
- `final` — the run's gates have cleared this instance; it is what gets rendered and sent.

A `final` instance carries no unresolved required edit from any validation report. Which gates decide
that is the flow's business; the status only records the outcome.

## Envelope

The common envelope applies. `inputs:` names the requirements profile, the recruiter signals, the
evidence map, the constraints ledger and the source audit. `revision:` increments on every edit pass;
a re-check after an edit reads the new revision.

A flow that produces several instances (a draft and a final, or documents for several targets) names
them itself and records the mapping in `run.md`.

## Document structure

### Header block

1. **Candidate name**, exactly as the knowledge bank's `## Candidate` section states it.
2. **Header title** — see below.
3. **Contact information** as plain text: each contact fact readable on its own, never carried only
   by an icon, a link decoration, or a layout position.

Profile links are given as **aliases or handles** (`profile-alias`, `profile-handle`), not as full
addresses with schemes or path prefixes. The renderer constructs the visible and clickable form.

### Section order

Standard section names, in this order:

1. `Summary`
2. `Skills`
3. `Experience`
4. `Projects` — when it adds value
5. `Education`
6. `Certifications` — when any exist
7. `Languages` — when relevant

Names are standard: no invented, clever, or renamed headings. An optional section with no supported
content is **omitted entirely**, never kept as an empty heading. The order is the document's order; a
renderer may place sections differently on the page as long as it preserves the standard headings and
the document text survives extraction.

## The header title

The header title is a short, market-facing positioning line for this application. It starts from the
candidate's truthful professional identity and supported seniority, and adds only the specialization
that makes the target fit legible.

Format: **`Role | Domain`**.

- Role first, domain second.
- The domain label is **one to three words**.
- The domain suffix is **omitted** when the role title already implies the specialization, or when
  the evidence does not support the domain.
- **The vacancy title is never copied mechanically.** Vacancy wording is acceptable only when the
  resulting title stays truthful and implies no unsupported domain experience, tooling, ownership,
  management scope or seniority.
- The header title may be broader than the candidate's official job titles. **Experience titles stay
  source-backed regardless** — they are never rewritten to match the header.

The rationale for the chosen title is recorded in the annex, and the renderer uses this validated
title rather than the vacancy title.

## Section rules

### Summary

A short paragraph positioning the candidate for this target using supported evidence only. It carries
no claim that does not also stand up in Experience, Skills or the evidence map.

### Skills

- **Broader than tools when evidence supports it.** Programming languages and tools are one group
  among several: systems and problem domains, reliability and delivery practices, collaboration and
  working-mode skills, and language skills belong here too whenever the evidence supports them.
- **Concise and grouped.** Group by capability area; keep entries short.
- **Concrete labels beat vague ones.** `Architecture documentation`, `Cross-team migration delivery`,
  `Observability`, `Zero-downtime rollout` — not `communication`, unless a source supports that exact
  phrasing.
- Every skill listed is supported by the evidence map. A skill the candidate is only familiar with is
  never phrased so as to imply production use.

### Experience

Position headers use one of exactly two shapes:

- `Job Title, Company`
- `Job Title (Team/Domain), Company` — when the team or domain adds meaningful context for the target

The parenthetical keeps the context on one line while the **last comma-separated element remains the
company name**. A third bare comma element (`Title, Domain, Company`) is forbidden: parsers
misidentify the company. Examples: `Backend Software Engineer (Billing & Identity), <Company>`;
`Software Engineer (Core Platform), <Company>`. The parenthetical is omitted when the title already
implies the domain, or when there is no meaningful team context.

Each position states its location and its dates in a readable, unambiguous form (for example
`Jan 2021 – Present`, `Mar 2018 – Dec 2020`), taken from the knowledge bank's positions section at
the granularity the sources give.

Bullets follow **action + scope or context + impact or result + technologies**, where supported.
Achievements are preferred over responsibility descriptions. Each bullet is specific, truthful, and
traceable to evidence; bullets are clear and recruiter-readable rather than dense.

### Projects, Education, Certifications, Languages

Drawn from the corresponding knowledge-bank sections, at the granularity the canonical sources give.
Education and certification entries are never inferred, upgraded, or reworded into something the
sources do not state. Language entries carry the level the sources state.

## Format rules

The markdown document stays **plain, linear and machine-readable**:

- No tables in CV content.
- No images, graphics, skill bars, or rating marks.
- No fact carried only by an icon, a color, an alignment, or a position on the page.
- No critical information placed only in a running header or footer.
- Simple bullet points; standard headings.
- Columns and decorative contact icons are the renderer's business, permitted only while the rendered
  file's text extraction stays readable — never introduced into the markdown document.
- Characters that a downstream renderer must escape are written naturally here; escaping is the
  renderer's responsibility, not a reason to distort the text.

## Truthfulness rules

- **Only supported facts.** No invented experience, metrics, tools, employers, dates, titles,
  degrees, certifications or achievements.
- **Every important claim is traceable** to a source listed in the run's source audit, through the
  evidence map.
- **Weak evidence is worded weakly.** Where the evidence is narrower than the target asks, the
  document says what is true, not what would score well.
- **Constraints bind.** A claim forbidden by the constraints ledger does not appear, however well it
  would fit.
- **Target keywords are mirrored only where the evidence carries them.** Optimizing for a keyword
  scanner never outranks truth.
- **No `TODO`, no `PLACEHOLDER`, no unsupported claim** reaches a `final` instance — and a `draft`
  containing one names it in the annex so it cannot be missed.
- **Internal product and company names are replaced with short public-facing descriptions** that
  convey the system's type and purpose to an outside reader — "internal CI/CD platform", "in-house
  inventory service", "proprietary ETL pipeline" — four words or fewer where possible. Publicly known
  products, tools and platforms are named directly.

## Header tags

Compact header tags (short scan signals rendered near the title) are **off by default**. The document
must read correctly without them.

- Tags never appear in the markdown body. They live in the annex as **candidates**.
- A tag is only ever a supplement: if it names a key skill or capability, that capability must also
  appear in Skills, Summary or Experience with supported wording. A tag is never the only carrier of
  an important skill or of any critical fact.
- Tags never carry unsupported keywords, vague soft-skill labels, domain claims, or inflated
  ownership. They are not a side channel for claims that would not survive in the body.
- Tags are enabled only when a validation step explicitly recommends a small, evidence-backed set for
  this application and confirms the set does not merely duplicate Skills.

## `## Annex: writer notes`

Every instance ends with an annex. It is part of the artifact but not part of the CV: a renderer
takes the document above it, a reviewer reads both.

1. **Emphasis choices** — what was foregrounded for this target and why, referencing the requirements
   profile and the recruiter signals.
2. **Intentional omissions** — supported material that was left out, and the reason (space, low
   relevance, a do-not-include instruction). This is what stops a reviewer from reading an omission
   as an oversight.
3. **Header title rationale** — why this title, and how it stays truthful against the vacancy title.
4. **Tag candidates** — each with its evidence note and an explicit render recommendation. **The
   default recommendation is not to render header tags** unless they add clear scan value beyond
   Skills, Summary and Experience.
5. **Open issues** — anything the writer could not resolve: a requirement with no honest angle, a
   conflict between sources, a claim awaiting a decision.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | `experience-writer.write-document`, `experience-writer.edit-document` |
| Consumers | `reviewer` (fact-check and registered checks), `renderer`, `vacancy-analyst` (fit scoring, gap analysis) |
