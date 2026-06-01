# Build Master CV Banks

Produce or refresh the three derived evidence indexes in `data/master/`:

- `experience_bank.md`
- `skills_matrix.md`
- `projects.md`

---

## Shared rules

### Source of truth

Canonical candidate inputs are the source of truth for all three files. The
indexes must not override canonical inputs unless `constraints.md` or the user
explicitly documents a correction. Do not invent facts, metrics, or experience
absent from canonical inputs.

### Source metadata block

Write a source metadata block at the top of each file on every refresh:

```
## Source Metadata
- Last updated: <timestamp>
- Prepared from: <file paths or input names>
- Source modification timestamps: <file>: <mtime>
- Refresh status: <full refresh / partial refresh — which sections or entries>
```

---

## experience_bank.md

### Purpose

A library of reusable, fact-checked, bullet-ready statements. Its job is
recall: give the CV writer pre-vetted material that can be inserted or adapted
without re-reading the full canonical sources.

Organise bullets by theme. Choose themes that reflect the actual evidence found,
not a fixed template.

### What to capture

Read all canonical candidate inputs fully before writing. Capture:

**Explicit evidence** — facts, outcomes, and actions directly stated in the
source: technologies used, systems built, scale numbers, dates, specific
improvements with before/after measurements.

**Implicit evidence** — patterns and practices that appear repeatedly across
projects or that describe how work was done rather than what was built. Look for:
- Recurring delivery behaviours across multiple projects (gradual rollout,
  observability-first, feature-flagged releases, cutover coordination)
- Design and documentation discipline (Mermaid diagrams before coding, PR
  templates, runbooks, architecture reviews)
- Cross-team coordination patterns (escalation, domain-owner collaboration,
  handoff coordination, driving tickets to resolution in adjacent teams)
- Test and quality practices (builder patterns for fixtures, parametrised test
  modes, mock infrastructure, E2E setup, per-PR ephemeral environments)
- Code review and ownership behaviours (mandatory approvals, review focus areas,
  onboarding support with explanatory comments)
- Performance and reliability engineering approaches (profiling tools and
  workflow, benchmark practice, before/after measurement, staged rollout)
- Security and compliance practices (RBAC design decisions, auth patterns,
  sensitive-data filtering, audit trail design)

### Bullet quality rules

- Each bullet must be a complete, standalone statement intelligible without
  reading surrounding source text.
- Follow the pattern: action + scope or context + outcome or impact, where
  supported.
- Use conservative verbs: built, designed, implemented, contributed to,
  supported, collaborated on. Use "led", "owned", or "architected" only when
  the source uses that language explicitly.
- Include concrete numbers, dates, and scale context when the source provides
  them. Do not invent or interpolate metrics.
- When a bullet reflects something implied rather than explicitly stated, add:
  `(inferred from <source section>)`.
- Keep each bullet scoped to one verifiable claim. Do not merge two separate
  facts to make a combined bullet sound stronger.
- Close the file with a **Conservative Gap Notes** section listing experience
  categories clearly absent from canonical inputs.

---

## skills_matrix.md

### Purpose

A capability index with evidence notes and conservative level guidance. Its job
is to make the evidence mapper and CV writer aware of the full breadth and depth
of the candidate's capabilities — not only named technologies, but also applied
patterns, engineering practices, domain knowledge, and working behaviours
relevant for senior-level roles.

Organise entries by capability group. Choose groups that reflect the actual
evidence found. Do not limit groups to programming languages and tools.

### What to capture

The most common failure mode is capturing only the tools named in a technology
stack while missing the deeper capabilities the candidate demonstrated. For each
area below, look past explicit tool lists and read how the work was done.

**Technical skills** — languages, frameworks, databases, infrastructure tools.
For each: state the evidence context (which employer, which project type) and
note important constraints (e.g. "internal PaaS equivalent, not direct
public-cloud ownership").

**Applied architectural patterns** — patterns used in production, not just known
in theory. Evidence for a pattern comes from how a project was designed, not
from a keyword list. Examples: strangler fig, outbox, dead-letter routing,
cursor-based migration, repository pattern with config-driven source switch,
multi-lane queue routing, sliding-window SLO alerts, gradual rollout by traffic
share, two-layer abstract workflow graphs, cross-system reconciliation with
auto-ticketing. Capture only patterns with concrete project evidence.

**Engineering practices** — repeating behaviours across projects that show how
the candidate works: design-first approach, observability-first delivery,
gradual rollout discipline, structured documentation, test infrastructure
design, performance engineering approach (profiling workflow, benchmark
practice, before/after measurement in production).

**Reliability and delivery practices** — SLO design, alerting strategy, release
engineering, on-call ownership, incident response workflow. Include scale
context when the source provides it.

**Security and compliance** — RBAC design decisions, service-to-service auth
patterns, SSO/identity integration, sensitive-data handling, audit trail design,
compliance context. Capture the decision made, not just the tool used.

**Domain knowledge** — business domains and problem spaces where the candidate
has production depth. Distinct from technical skills: covers what systems do,
not how they are built.

**Collaboration and operating style** — cross-team coordination, domain-owner
collaboration, code review ownership, onboarding or mentoring. Capture only
behaviours with concrete evidence; do not include generic soft-skill labels.

**Language skills** — with level label and any practical work-context evidence.

### Entry format and level guidance

For each capability, write a short entry including:
- The evidence context (which employer, project, or situation)
- A conservative level signal: strong evidence / moderate evidence / limited
  evidence / surface-level familiarity / no evidence
- Any constraints or safe-use notes (what not to claim when using this entry)

Do not use numeric ratings. Bias toward the more conservative label when
evidence is ambiguous.

### Implicit capability rule

If a capability is demonstrated by how work was described rather than by an
explicit claim, capture it with a note: `(inferred from <source section or
project name>)`. This is especially important for architectural patterns and
engineering practices, which candidates rarely label as skills in their own CVs.

### Conservative gap notes

Close the file with a section listing capabilities that are clearly absent or
explicitly constrained by canonical inputs. This section is as important as the
positive evidence: it prevents evidence mappers from stretching weak evidence
into unsupported claims.

---

## projects.md

### Purpose

A project-level recall index. Its job is to give the evidence mapper fast
access to the context, scope, candidate role, and outcomes of each significant
project — without requiring a full re-read of the canonical sources.

### What counts as a project entry

Create a separate entry for any body of work that:
- Had a distinct goal, scope, and outcome
- Lasted long enough to produce independently verifiable evidence
- Is likely to be discussed as a unit in a CV, interview, or evidence map

Freelance work, self-education periods, and part-time contributions qualify if
there is concrete evidence worth recalling. Do not create entries for minor
tasks or one-off fixes; those belong in the experience bank as bullets.

### Entry structure

For each project, capture:

**Context** — the problem or situation that motivated the work: what existed,
what was wrong or missing, what the goal was, and why it mattered. Include
scale or domain context when the source provides it.

**Candidate role** — what the candidate specifically owned or contributed. Be
precise: primary author, contributor, co-owner, architectural ownership on one
side, etc. Do not inflate role claims beyond what the source supports.

**What was built** — the concrete deliverables: systems, frameworks, patterns,
infrastructure, processes, documentation. Describe what exists as a result of
the work.

**Technologies** — the stack used. Use public-facing names or class-mapping
descriptions for internal tools.

**Impact** — measurable or observable outcomes when the source provides them.
When no number exists, describe the qualitative change. Do not invent metrics.

**Evidence** — which canonical source and section this entry is drawn from.
Required for later validation.

### Entry rules

- Preserve the candidate's actual role accurately. A contributor entry must not
  read like sole ownership.
- Note the current state explicitly when a project is still in progress: what
  is complete, what is pending, whether it has reached production.
- Include the time period when the source provides it.
- Do not merge two separate projects into one entry.
- Do not split one continuous project unless the source treats distinct phases
  as having separate goals and outcomes.
