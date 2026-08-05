---
name: validate-cv-ats
description: ATS structural check spec — verifies that a CV stays machine-readable for applicant tracking systems and that it covers the vacancy's keywords, and reports a 0-100 measurement with keyword coverage and formatting risks. Internal validator, executed by the reviewer.
---

# Tool: validate-cv-ats — the ATS structural check

## What this skill is

The **spec of one check**: does this CV survive machine parsing, and does it carry the vacancy's
language? It holds the rules of that check — what is inspected, which inputs it needs, which
measurements it produces, which scripts it ships, and how it behaves when something is unavailable.

It is a **procedure plus assets, never an actor**. This skill defines no agent and holds no authority
of its own. It is executed by [`reviewer.run-check`](../../../roles/reviewer/capabilities/run-check.md)
under the reviewer's invariants (see [`roles/reviewer/ROLE.md`](../../../roles/reviewer/ROLE.md)),
which always outrank anything written here. In particular:

- **This check never edits the CV.** It produces findings and required edits; applying them is the
  writer's work.
- **Its score is a measurement, not truth.** The number defined below is the value of a formula
  stated in this file — it is never presented as a judgement of the candidate, and it never outranks
  a truthfulness finding.
- **It never invents.** A keyword the candidate's evidence does not support is a gap, not an edit
  suggestion. ATS optimization never outranks truth.

## Optional and user-registered

This validator is **optional**, exactly like every other entry of the validation set. It is the
shipped default for ATS-targeted CVs, but no workflow hardcodes it: it runs only while it is recorded
in the user's active validation set (kind `internal`) per
[`contracts/user-context.md`](../../../contracts/user-context.md). A user whose target is not an
ATS-processed application may legitimately remove it, and nothing else has to change.

The mandatory truthfulness check is a different thing entirely — `reviewer.fact-check`, invoked by
workflows directly and never part of the registered set.

## Inputs

Every path is passed in explicitly by the caller; this skill derives none from repository layout.

| Input | Contract / description | Required |
|---|---|---|
| `cv_document` | `cv-document` — the CV under review (markdown) | required |
| `requirements_profile` | `requirements-profile` — keyword sets, must-have requirements, seniority, hidden priorities | required |
| `job_description` | the vacancy text from the run's `job-dossier` | required |
| `static_check_output` | output of the bundled `scripts/ats_static_check.py` over `cv_document` | required — produced during this check |
| `keyword_match_output` | output of the bundled `scripts/keyword_match.py` over `job_description` (and the must-have list) versus `cv_document` | required — produced during this check |
| `rendered_pdf` | the rendered deliverable, when the run has already produced one | optional |
| `rendered_text_normal` | plain text extraction of `rendered_pdf` | optional — required to inspect the rendered form |
| `rendered_text_layout` | layout-preserving text extraction of `rendered_pdf` | optional — required for a columnar render |
| `recruiter_signals` | `recruiter-signals` — read only for its do-NOT-include list | optional |

The two bundled scripts are the check's own instruments: their outputs are **inputs of the check
itself**. Run them as part of executing this spec (the caller may also pass captures produced
earlier in the same run — then re-run them only if the CV changed). Their output is evidence for the
agent's judgement, never a verdict.

**Subject rule.** The markdown `cv_document` is always the subject. The rendered form is inspected in
addition, and only when it exists: pre-render this check runs on markdown alone and says so. Item 13
and the rendered half of items 1, 3, 5 and 9 are then reported as *not applicable at this stage*, not
as passes.

## Outputs

| Output | Contract | Status values |
|---|---|---|
| `report_path` | `validation-report` | `pass`, `pass-after-edits`, `fail`, `skipped`, `blocked` |

The reviewer writes the report; this spec supplies the findings and the measurements, with the labels
defined under [Measurements and report labels](#measurements-and-report-labels). The report envelope,
severity vocabulary and `## Constraint proposals` section come from the `validation-report` contract
and the reviewer's rules, not from here.

## The check

Thirteen items. Each one is either satisfied, satisfied-with-remarks, violated, or not applicable at
this stage; anything other than "satisfied" produces a finding that names the location in the CV,
what is wrong under this spec, and the edit required.

| # | Item | Subject | What it establishes |
|---|---|---|---|
| 1 | **Machine-readable structure** | markdown (+ rendered when present) | The document parses linearly: one column of meaning, headings before their content, no tables, no embedded markup, no artwork carrying text. Nothing is reachable only through visual layout. |
| 2 | **Standard section headings** | markdown | Sections use conventional, unambiguous names (Summary, Skills, Experience, Projects, Education, Certifications, Languages) in a conventional order. Creative or invented headings are a finding, whatever their appeal. |
| 3 | **Contact readability** | markdown (+ rendered when present) | Name, email, phone, location and profile links exist as plain visible text that survives extraction — not only as an icon, a hyperlink alias with no text, or a graphic. |
| 4 | **Date readability** | markdown | Every position and education entry carries dates in one consistent, unambiguous, machine-parsable format; ranges and "present" are written the same way throughout; no gaps disguised by format changes. |
| 5 | **Job-title readability** | markdown (+ rendered when present) | Each position header is parsable as title plus employer (optionally a team/domain qualifier), on its own line, never fused into prose and never ambiguous about which part is the title. |
| 6 | **Keyword coverage** | markdown vs job side | The vacancy's significant terms appear in the CV where the candidate's evidence supports them. Uncovered terms split into: unsupported (a gap — record it, never write it in) and supported-but-absent (a real edit for the writer). |
| 7 | **Must-have keyword coverage** | markdown vs `requirements_profile` | Every must-have requirement is either present in the CV's own words or explicitly recorded as a gap. A missing must-have that the evidence *does* support is the highest-value finding this check produces. |
| 8 | **Keyword overuse** | markdown | No term is repeated to the point of reading as stuffing, and no bullet exists solely to host keywords. Repetition that a human recruiter would notice is a finding even when the parser would not mind. |
| 9 | **Formatting risks** | markdown (+ rendered when present) | The formatting rules below hold. Each violated rule is one finding, named by rule. |
| 10 | **Missing important skills** | markdown vs job side | The Skills section covers the supported job-relevant capabilities — including the non-tool ones (systems and problem domains, reliability and delivery practices, collaboration or working-mode skills, languages) — not only a tool list. A capability that the evidence supports and the vacancy asks for, but the CV omits, is a finding. |
| 11 | **Ambiguous seniority** | markdown vs `requirements_profile` | The document communicates a seniority level consistent with the evidence and legible to a filter: titles, scope of ownership and the positioning line do not contradict each other and do not leave the level unreadable. Inflation is a truthfulness matter and is reported as such, not "fixed". |
| 12 | **Recruiter readability** | markdown (+ rendered when present) | A human skimming for 20 seconds reaches the decisive facts: current role, core stack, scale/domain, most relevant achievements. Wall-of-text bullets, buried leads and unexplained internal jargon are findings. |
| 13 | **Rendered scan tags** | rendered only | When the render places short compact tags (in a header or elsewhere), they behave per the tag rules below. Not applicable when no render exists or the render carries no tags. |

## ATS formatting rules

The rule set item 9 tests, and the vocabulary its findings use.

**Structure**

- **No tables in the final CV.** A table in the markdown document is a violation without exception.
- **Columns are allowed in the rendered PDF only** while extraction stays readable: section headings
  survive, and facts are neither interleaved between columns nor lost. A columnar render whose
  extraction scrambles content fails this rule even when it looks perfect on screen.
- **No images**, and no information that exists only inside one.
- **No skill bars**, ratings, percentages or star scales for proficiency.
- **No critical information in the header or footer** area of the render — parsers routinely drop it.
- **No unusual section names.**
- **Simple bullet points**: one claim each, plain markers, no nested decoration.
- **Text-based PDF, never a scanned or image-only one.**
- **For a columnar PDF, inspect both extractions** — normal and layout-oriented. Disagreement between
  the two is itself the finding.

**Icons and tags (machine readability)**

- **Icons may be decorative**, but every contact or skill fact must also exist as visible text.
- **Render tags may serve as short visible scan aids**, but they may never be the sole carrier of
  critical information, and they may never introduce a keyword the CV's content does not support.
- **Header tags are off by default.** Treat any rendered tag as an exception and flag one that merely
  duplicates key skills belonging in the Skills section.
- **A key skill that appears only in a header tag or a compact scan signal is flagged as missing from
  the main ATS-readable content** — the tag does not count as coverage for item 6, 7 or 10.

**Boundary — out of scope here.** Whether a tag is *truthful* (source-backed; not misleading about
domain, ownership, seniority or production use; safe-but-omit when it merely duplicates the body) is
the mandatory truthfulness check's business and is defined in
[`roles/reviewer/capabilities/fact-check.md`](../../../roles/reviewer/capabilities/fact-check.md).
This spec judges only machine readability and coverage. If a tag looks untruthful while running this
check, record it as a note for the fact check rather than re-deciding it here.

## Measurements and report labels

This spec produces the following measurements. The reviewer records them with **exactly these
labels** inside the report envelope.

| Label | Type | Definition |
|---|---|---|
| `ATS score` | integer 0–100 | Computed by the formula below. A measurement under this spec's definition — never an independent judgement, never a verdict. |
| `static check score` | integer 0–100 | The score printed by `scripts/ats_static_check.py`, recorded verbatim and separately. It is a crude signal over the markdown only; it is never merged into `ATS score` silently and never replaces it. |
| `Critical issues` | list | The findings that must be fixed before the CV is sent. |
| `Keyword coverage` | percentage + three lists | The percentage printed by `scripts/keyword_match.py`, plus `Covered`, `Missing`, `Weak`. |
| `Formatting risks` | list | One entry per violated formatting rule, named by rule, with its location. |
| `Recommended edits` | list | Concrete, truthful edits, each tied to the finding it resolves. |
| `Verdict` | enum | `Pass` / `Pass-after-edits` / `Fail`. |

**Keyword coverage lists.**

- **Covered** — the term appears in the CV, in a place a parser reads, supported by evidence.
- **Missing** — the term does not appear. Each missing term is marked either `supported` (the
  evidence carries it; the writer can add it) or `gap` (the evidence does not; it stays out and is
  recorded as a gap).
- **Weak** — the term appears, but only once, or only in a tag, or only in a list with no
  corroborating experience bullet. Weak is never rounded up to Covered.

**`ATS score` formula.** Start at 100 and subtract per finding: **20** for each blocking finding,
**8** for each major, **3** for each minor. Floor the result at 0. When part of the check could not
run (no render, or an unbound dependency), state the score as partial and name what was not measured.

**Severity classes** (mapped onto the severity levels the `validation-report` contract declares):

- **Blocking** — item 1 violated; a table in the final CV; an unreadable or absent contact fact; a
  scanned/image-only PDF; critical information reachable only in a header/footer or only in a tag; a
  supported must-have keyword absent (item 7).
- **Major** — non-standard section headings; unparsable dates or job titles; an important supported
  skill missing (item 10); ambiguous seniority; a columnar render whose two extractions disagree.
- **Minor** — keyword overuse, recruiter-readability remarks, cosmetic formatting risks with no
  extraction impact.

**No score threshold.** This spec declares no pass/fail threshold on `ATS score` — the verdict is
derived from findings only, per the reviewer's verdict vocabulary: `Fail` when at least one blocking
finding stands, `Pass-after-edits` when edits are required but none blocks, `Pass` when there is
nothing to fix. A high score never converts a blocking finding into a pass.

## Runbook

**1. Establish the subject.** Read `cv_document`. Determine whether a render exists; if it does,
obtain both text extractions (normal and layout-oriented) before inspecting the rendered form. If
extraction is unavailable, do not guess from the markdown — mark the rendered items not measured.

**2. Run the static check.**

```
python3 skills/tools/validate-cv-ats/scripts/ats_static_check.py --cv <path-to-cv.md>
```

Optional: `--out <path>` to write the report instead of printing it; `--long-bullet-chars N` to
change the long-bullet threshold (default 240); `--json` for a machine-readable capture. The script
reports headings found, contact-field presence, formatting-risk patterns, bullet statistics and its
own score. It flags *candidates* — for example an `icons_or_symbols` hit is a pointer to inspect, not
a finding by itself.

**3. Run the keyword match.**

```
python3 skills/tools/validate-cv-ats/scripts/keyword_match.py --job <path-to-job.md> --cv <path-to-cv.md> [--must-have <path-to-list.txt>]
```

`--must-have` takes a plain-text file, one keyword or phrase per line (`#` comments allowed), which
the agent writes from the must-have requirements of `requirements_profile`. Optional: `--top N`
(number of job terms considered, default 100), `--list-limit N` (entries printed per list, default
60), `--weak-max-count N` (a covered term at or below this count is reported as weak, default 1),
`--overuse-min-count N` (repetition threshold, default 6), `--out`, `--json`.

Both scripts read UTF-8 and accept any plain-text input — markdown, or text extracted from a PDF.
To run the keyword match against the rendered form, extract its text to a file first and pass that
file as `--cv`.

**4. Judge, do not transcribe.** Script output is evidence. Every item of the check is decided by
reading the CV against the job side; the numbers only direct attention. Never report a script line as
a finding without stating what is actually wrong in the document.

**5. Assemble the report** with the labels above, hand it to the reviewer's envelope, and stop. No
edits, no rewritten CV, no "suggested replacement document".

**Graceful degradation.**

- **No render yet** — normal. Run the markdown half, mark items 13 and the rendered halves as not
  applicable at this stage, and state that the check must be re-run after render if the CV changes.
- **Render exists but text extraction is unbound** — the rendered half is SKIPPED with instructions
  (bind an extraction tool, or extract manually and pass the text files); the markdown half still
  runs, and the report is marked partial. Per the reviewer's rules a partial check cannot return
  `Pass` for the parts it could not inspect.
- **A script fails** — report what was attempted, the raw error, and which items are therefore
  unverified. The judgement of every item that does not depend on that script still stands; the
  script is an aid, and its absence degrades precision, not validity.
- **An input is missing or unreadable** — that is a precondition failure; the reviewer reports
  `blocked`. Do not substitute another artifact for a declared input.

**Manual fallback.** Without Python, every item is still decidable by reading: the scripts only
automate counting. Do the item-by-item pass by hand, state in the report that the measurements were
derived manually, and give `ATS score` and `Keyword coverage` from the same definitions.

**Troubleshooting.**

- *Coverage looks absurdly low* — the job-side input probably contains boilerplate (benefits, legal
  text). Trim it, or lower `--top`, and re-run; note in the report which input was used.
- *`markdown_table` fires on a line with pipes* — a code fragment or a pipeline example can trigger
  it. Confirm in the document before recording a finding.
- *`icons_or_symbols` fires on bullet markers* — check which character it matched; a decorative
  bullet is a formatting remark, a fact carried only by an icon is a blocking finding.
- *The two rendered extractions disagree* — that is the columnar-render finding of item 1/9, not a
  tooling problem. Report it.

## Settings

This skill recognizes **no keys** under `## Skill settings` in the user's context. Its behaviour is
fully determined by its inputs and the CLI options above. Any key recorded under a
`### validate-cv-ats` subsection is unrecognized and is reported at preflight per
[`contracts/user-context.md`](../../../contracts/user-context.md), never silently ignored.

Registration itself (name + kind `internal`) lives in the `## Validation skills` list, not here.

## Dependencies

| Field | Value |
|---|---|
| **name** | `python3` (≥ 3.10) |
| **kind** | tool |
| **needed for** | running the bundled `scripts/ats_static_check.py` and `scripts/keyword_match.py` |
| **required \| optional** | optional |
| **when unbound** | the check still runs — every item is decidable by reading. The measurements are derived manually per the runbook's manual fallback, and the report states that no script measurement was available. |

| Field | Value |
|---|---|
| **name** | rendered-document text extraction (normal and layout-preserving) |
| **kind** | capability |
| **needed for** | inspecting the rendered PDF: item 13, the columnar-extraction gate, and the rendered halves of items 1, 3, 5 and 9 |
| **required \| optional** | optional |
| **when unbound** | the rendered half runs SKIPPED with instructions (bind an extraction tool, or extract the text manually and pass the two text files as inputs); the markdown half runs normally and the report is marked partial. |

| Field | Value |
|---|---|
| **name** | file reading and writing within the paths passed |
| **kind** | capability |
| **needed for** | reading the CV, the job-side inputs and the extractions; writing the report at the path the caller passed |
| **required \| optional** | required |
| **when unbound** | the check cannot run at all; the reviewer reports `blocked`. |
