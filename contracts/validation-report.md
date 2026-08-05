# Contract: validation-report

Version: 1.0

## Purpose

One uniform envelope for **every** check performed on a document, whatever its origin: the mandatory
truthfulness check, any registered internal check, and any external service's report after it has
been normalized. A consumer therefore reads one shape — verdict, findings, required edits — instead
of one shape per checking tool.

## Status values

The status **is** the verdict:

- `pass` — no required edit;
- `pass-after-edits` — the document is sound once the listed required edits are applied;
- `fail` — the document must not proceed in its current state;
- `skipped` — the check could not run (a capability is not bound, an input is missing). A skipped
  check is a recorded outcome with instructions, never a silent absence and never a failure of the
  flow.

## Envelope

The common envelope applies. `producer` names the capability that wrote the report
(`reviewer.fact-check`, `reviewer.run-check`, `reviewer.normalize-external-report`). `inputs:` names
the checked document **with its revision** and every evidence source used. When a check is re-run
after an edit, the report is overwritten and `revision:` increments.

## Common sections

### `## Check`

| Field | Meaning |
|---|---|
| check name | The truthfulness check, or the name of the registered validator. |
| kind | `fact-check` · `internal` · `external (normalized)`. |
| subject | The artifact checked, and its revision. |
| basis | What the check was performed against: evidence sources, a check specification, an external service. |

### `## Verdict`

`Pass` / `Pass-after-edits` / `Fail`, matching the envelope status, with one or two sentences saying
what decided it.

### `## Findings`

One entry per finding:

| Field | Rule |
|---|---|
| id | A short identifier the edit pass and any re-check can cite. |
| severity | `critical` (must be fixed; blocks) · `major` (should be fixed) · `minor` · `advisory`. |
| location | Where in the document — section, position header, bullet. |
| finding | What is wrong, stated concretely. |
| basis | The evidence or rule that makes it wrong. A finding without a basis is an opinion. |
| required edit | The concrete change. |

`critical` findings and `fail` go together: a report with a critical finding is not a pass.

### `## Scores` (optional)

Whatever the check produces, each score named with its scale. **Scores are never a verdict**, and
external scores are never truth: a verdict comes from findings, not from a number.

### `## Keyword coverage` (optional)

`Covered` / `Missing` / `Weak`, against the requirements profile's keyword sets. A missing keyword is
a finding **only** when the candidate's evidence actually supports it — a keyword the evidence does
not carry is a gap, not a defect in the document.

### `## Constraint proposals`

Guardrails discovered while checking — a claim that keeps reappearing unsupported, a wording pattern
that repeatedly overstates. See `contracts/README.md`. `None.` when there is nothing to propose.

## Profiles

A report carries the common sections plus the sections of its profile.

### Fact-check profile

The truthfulness check. Additional sections:

- **`## Claim classification`** — every meaningful claim in the document, classified as `Supported` ·
  `Partially supported` · `Unsupported` · `Exaggerated` · `Too vague` · `Needs evidence`, each with
  the source passage that supports it or the note that none was found. Claims to check with
  particular care: the header title and other positioning lines, job titles, dates, company names,
  tools, programming languages, the Skills section's coverage and wording, seniority claims,
  leadership and ownership claims, metrics, business impact, domain experience, certifications,
  education, management scope, and any compact header tag or positioning label.
- **`## Header title check`** — whether the title is a truthful, supported positioning line; whether
  it accidentally implies unsupported domain experience; and whether the Experience titles remain
  source-backed.
- **`## Supported tag signals`** — the tag candidates that are safe to render, each with its evidence
  basis. Because header tags are off by default, a tag is listed as recommended only when it adds
  clear scan value beyond Skills, Summary and Experience; a tag that is safe but redundant is marked
  **safe-but-omit**. A tag that is the only carrier of an important capability is a finding.
  Omitted entirely when no tags are proposed.

Rules the profile records: be strict; an unsupported claim is never rewritten into a fact; a metric
absent from the sources is unsupported; a technology listed as familiar but not used professionally
never implies production experience; skills claims of any kind — technical, systems and domains,
reliability and delivery practices, collaboration and working-mode, languages — each need their own
evidence.

### Internal-check profile

A registered internal check. Its own specification defines what it examines; this contract defines
how it reports. Typical additional sections: `## Structural findings` (headings, contact readability,
date readability, title readability, formatting risks) and `## Coverage` (missing important skills,
ambiguous seniority, recruiter readability). The specification of any given check lives with that
check, never here.

### Normalized-external profile

An external service's report, restated in this envelope. Additional sections:

- **`## Validator`** — service name, the input files submitted, the raw capture the normalization was
  made from;
- **`## Keyword gaps`** — the keywords or skills the service says are missing, as it stated them;
- **`## Formatting issues`** — layout, sections, file type, bullets, dates, columns, icons, parsing;
- **`## Content suggestions`** — summary, bullets, skills, positioning;
- **`## Potentially unsafe suggestions`** — suggestions that would require adding facts, tools,
  metrics, certifications, domain experience, or seniority claims the document does not have. Called
  out separately because they are the ones that do damage.
- **`## Recommended next actions`** — each labelled `Safe formatting edit` · `Needs fact validation` ·
  `Gap only` · `Reject`.

Normalization **restates, it does not endorse**. Nothing in an external report becomes an edit by
being written down here; the decision belongs to the `external-gate-decision`.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | `reviewer.fact-check`, `reviewer.run-check`, `reviewer.normalize-external-report` |
| Consumers | `experience-writer` (edit pass), `renderer` (gate state before rendering), `vacancy-analyst` (fit and gap analysis), `reviewer` (gating external recommendations), `knowledge-bank-curator` |

The reviewer **never edits the document it checks**. It produces findings and required edits; the
writer applies them.
