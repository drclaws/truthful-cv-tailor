---
name: render-cv-pdf
description: Renders a final CV document into the delivered PDF using the resolved template bundle, runs the mechanical render gates (compile twice, text extraction, fonts, page target, export naming), and reports overflow back to the caller instead of restyling the template.
---

# Tool: render-cv-pdf

Turns a finished CV document into the file the user sends out: fill the resolved template's
agent-content zones, build the PDF, run the mechanical gates, report.

**PDF is the only deliverable.** No other export format is produced by this tool, deliberately.

## What this tool is

**A tool, and an internal one.** It is reached by name — from a flow step naming `tool:render-cv-pdf`,
or from a user naming it directly with explicit paths — and by nothing else: it is registered with no
harness, discovered by none, and never offered in a selection surface. A render is the step of a run
whose checks have already been cleared, so a request that landed here directly would arrive without
them; `tool-conventions` states that reasoning once, for every tool in this package.

**Procedures-plus-assets, never an agent.** This tool defines no role, holds no authority of its own,
and decides nothing about content. It is executed by the role `renderer`, capability
`renderer.render-document`, and the renderer's invariants apply to every line of it: content is
transcribed and never authored, only the template's delimited agent zones are edited, the template's
style is never changed, the knowledge bank and the constraints ledger are never written, another
run's output is never a style authority.

Where this file and the renderer's capability describe the same step, the role states *what* the
renderer is responsible for, and this file states the *operation rules* — the page target, how an
overflow is reported, the gate sequence, the export naming check, and how a template is resolved.
Where a rule here would contradict the role, the role wins and the contradiction is a defect to
report.

## Inputs

| Input | Contract / description | Required |
|---|---|---|
| `document` | `cv-document` instance with `status: final` | required |
| `template` | the resolved template setting: a folder name under `templates/`, or a path to an external bundle satisfying the template bundle contract below. Defaults to `ats-onepage-latex` | required (defaulted) |
| `export_name` | the export filename, or the naming rule, produced by the calling flow | required |
| `source_out`, `export_out`, `manifest_out`, `build_dir` | output paths, passed by the caller | required (`build_dir` optional) |
| `page_target` | the target page count; defaults to **1** | optional |
| `validation_reports` | zero or more `validation-report` instances accompanying the document | optional |

Nothing is resolved by convention: if an input was not passed, ask the caller rather than guessing —
least of all the export filename.

## Outputs

| Output | Contract / description |
|---|---|
| the typeset source at `source_out` | the template copy with its agent zones filled; not a contract artifact |
| the exported PDF at `export_out` | the deliverable, named per the caller's naming rule |
| the render report at `manifest_out` | `render-manifest`: template name and version, per-gate results (red ones included), export inventory with the naming check, unresolved issues, `## Constraint proposals` |

Build byproducts go to `build_dir` and are never part of the deliverable.

## User-context settings

Per contract `user-context`, a package's own definition file defines the keys of its settings
subsection. This tool recognizes exactly one:

```markdown
### render-cv-pdf
- template: ats-onepage-latex        # or a path to an external template bundle
```

| Key | Required | Values | Default | Meaning |
|---|---|---|---|---|
| `template` | optional | the name of a folder under this tool's `templates/`, or a path to an external bundle satisfying the template bundle contract below | `ats-onepage-latex` | Which template bundle this tool resolves and fills. |

Any other key in this subsection is **reported as unrecognized** at preflight, never silently
ignored and never guessed at. The page target is an operation rule of this tool (default: one page),
not a user-context key; a caller that needs a different target passes `page_target` explicitly.

## Template resolution

1. Take the `template` value the caller resolved from user context. If there is none, use
   `ats-onepage-latex` — the shipped default, and the only bundle this repository ships.
2. A value **without a path separator** names a folder under this tool's `templates/`. Resolve it
   there; if that folder does not exist, stop and ask — do not fall back to the default silently,
   because the user asked for something specific.
3. A value **with a path separator** is a path to an external bundle, and it lives wherever the user
   keeps it — outside this package, which ships exactly one bundle. Resolve it as given: an absolute
   path is the reliable form and is what to ask for, because a relative one can only be resolved
   against the location the caller happens to be working in, which is neither this package nor
   anything this tool can establish. An external bundle that is missing or unreadable is reported to
   the caller; it is not replaced by the default.
4. Validate the resolved bundle against the template bundle contract below before using it. A bundle
   that does not satisfy it is reported, not repaired.
5. Record the bundle's **name and version** in the render report — the `render-manifest` contract
   requires them, and a rerun must be attributable to a specific template.

**Which bundle to register is the user's decision**, recorded in this tool's settings subsection in
user context — for instance a simpler or stricter bundle when the target system demands one. This
tool never switches bundle on its own, and a bundle is **never** changed to make content fit: that
is an overflow, and overflow goes back to the caller as content to revise.

## Template bundle contract

Any bundle — shipped or the user's own — satisfies this contract. It is what makes a user-supplied
template usable without changing this tool.

Required files, at the root of the bundle folder:

| File | Must contain |
|---|---|
| `template.tex` (or the source file the bundle's `runbook.md` names) | the typeset source, **candidate-neutral**, with **delimited agent-content zones** marked by paired begin/end comments that name each zone |
| `policy.md` | the bundle's version; the list of zones and what each accepts; the fill rules (macros/fields, optional fields, empty sections); the escaping rules of its markup language; where each document section is placed in its layout; its stance on style changes; any gate the composition itself requires (e.g. a column extraction gate) |
| `runbook.md` | the concrete toolchain: which engine builds it and which packages it needs, the exact build commands, the inspection commands, a troubleshooting table, and what to produce when the toolchain is unavailable |

Rules a bundle must obey:

- **Candidate-neutral and user-data-free.** Placeholders only; no real name, contact, employer or
  path may live in a committed bundle.
- **Path- and OS-neutral.** No external absolute paths, no OS-specific assumptions.
- **Zones are explicit.** Anything an agent may edit is inside a named, delimited zone; everything
  else is structure and style, and is off limits.
- **ATS-safe by construction.** Every fact it renders is ordinary visible text; no fact is carried
  only by an image, an icon, a colour, a table, or alternate text.
- **It governs the *how*, never the *what*.** A bundle's policy may not relax the truthfulness
  invariants, the document contract, this tool's operation rules, or the renderer's authority. A
  bundle that tries to is rejected and reported.
- **Concrete tool names belong to its `runbook.md`**, and any tool it requires beyond this tool's
  `## Dependencies` must be declared there so `setup-master.check-environment` can be told about it.

A bundle may ship extra assets (scripts, fonts it is licensed to redistribute, sample fills). They
are optional and never override the three required files.

The shipped default is `templates/ats-onepage-latex/`:
[`template.tex`](templates/ats-onepage-latex/template.tex),
[`policy.md`](templates/ats-onepage-latex/policy.md),
[`runbook.md`](templates/ats-onepage-latex/runbook.md).

## Page target, and what an overflow is

**The target is one page** unless the caller passed a different `page_target`. **This tool declares
the target and measures it on the export**, never estimating it from the source: a page count read
off the typeset source is a guess about the file that is actually sent, and gate 2 checks the file
itself.

**What happens when validated content does not fit is not this tool's rule to state.** The document
it renders is a `cv-document`, which is a **deliverable-document contract**, so the
**content-first fit policy** of that family in `artifact-conventions` governs it: the
evidence-carrying section is compressed first and gradually, space that later edits free is refilled,
and restyling the delivered result — or reaching for another template to squeeze the same content in
— is out of bounds, because a fit problem is a content problem. That policy is stated once there and
is not restated here. It is also not a rendering rule: it holds for a deliverable that is pasted into
a web form and never rendered at all, which is why it does not belong to a render tool.

What is this tool's, and is stated here, is what it does with an overflow:

- **Report it to the caller** — what overflowed and by roughly how much — so the document can go back
  for content revision by the writer, under the reviewer's checks. **That is the whole of this tool's
  authority over a fit problem**: it decides nothing about content, so it neither drops validated
  content on its own nor switches to a bundle that would hide the overflow.
- **Never restyle to fit.** The bundle's style is fixed by the bundle (for the shipped default, its
  `policy.md` says so in its own words), and this tool has no authority to change it in any case.
- Every content change after a render re-opens the checks it could invalidate: the mandatory
  truthfulness check and the affected registered internal checks run again, and the document is
  re-rendered.

## Gate sequence

Run in this order, on every render. Record **every** result in the render report, red ones included;
a run with any gate red is reported as not done, never as a success.

| # | Gate | Green when | Red means |
|---|---|---|---|
| 1 | **Compile twice** | the source builds twice in a row with no error, so cross-references, column breaks and PDF metadata have settled | a build error, or content still moving between the two runs. Fix the fill or the escaping — never the style |
| 2 | **Page target** | the export's page count is at most `page_target` | overflow: stop before handing over, and report it to the caller as *Page target, and what an overflow is* above requires |
| 3 | **Text extraction, both modes** | extracting in plain reading order **and** in layout-preserving mode still yields the section headings, the contact details, the role titles, the dates and the bullets, with **no cross-column interleaving** and no side content lost; and no `TODO`, `PLACEHOLDER` or template sample text appears in either extract | the layout defeats parsing. Report it with both extracts as evidence and the bundle's recommended remedy; the caller decides |
| 4 | **Fonts embedded** | every font in the export is embedded (and Unicode-mapped, where the engine offers it) | the file will not render or extract reliably elsewhere; rebuild per the bundle's runbook |
| 5 | **Export naming** | the exported filename matches the naming rule the calling flow passed | do not rename by invention; ask the caller |

The concrete commands live in the resolved bundle's `runbook.md`; the general half of the procedure
is in this tool's runbook below. Gates 3 and 4 also feed the bundle's own composition gate — for
the shipped template, the column gate in
[`templates/ats-onepage-latex/policy.md`](templates/ats-onepage-latex/policy.md).

An unbound toolchain does not fail the flow: produce what is possible — normally the filled typeset
source — mark the affected gates as **not run**, and report the step SKIPPED with the manual
instructions from the bundle's runbook. Say which gates could not be run; never assume a gate that
did not run would have passed.

## Export naming

The naming **rule** belongs to the calling flow, never to this tool, never to a contract, and never
to user context. This tool only:

- applies the filename or rule the caller passed;
- checks the produced filename against it (gate 5);
- reports a mismatch, and asks when nothing was passed.

## Where the outputs go

- **Invoked from a workflow step:** every path is passed by the workflow; write exactly there and
  nowhere else.
- **Invoked standalone by the user:** default to `outputs/render-cv-pdf/<run-id>/` with a minimal
  `run.md` (`run-manifest`) recording the inputs, the resolved template and the gate results, plus
  `render/` for the typeset source and build byproducts and `exports/` for the deliverable. The user
  may override any of these by passing explicit paths.

## Runbook

The general half — the template-specific commands are in the resolved bundle's `runbook.md`.

**Prepare.** Confirm the document is `status: final`; resolve the template and read its `policy.md`
before touching anything; confirm the output paths and the export name were passed; check the
toolchain the bundle's runbook names, and decide up front whether this is a full render or a
SKIPPED-with-instructions render.

**Render.** Copy the bundle's source to `source_out` and work only in the copy — the bundle itself is
read-only. Fill only the delimited zones, escaping every generated string as the bundle's policy
prescribes. Build into `build_dir`, then place the export at `export_out` under the caller's name.

**Check.** Run the gate sequence above. For the text-extraction gate, the bundled script does the
mechanical part in one pass:

```bash
python3 scripts/pdf_text_check.py <export.pdf>
python3 scripts/pdf_text_check.py <export.pdf> --json --excerpt 0
python3 scripts/pdf_text_check.py <export.pdf> --heading summary --heading experience
```

Its exit codes: `0` pass, `1` fail (a required heading or contact signal is missing, or an extract
came back empty), `2` usage error, `3` skipped (the extraction binary was not found — the gate did
not run), `4` the PDF could not be read. It takes every signal it checks as an explicit argument and
reads no rules file. **It does not replace reading both extracts**: interleaved columns and lost side
content are visible to a reader, not to a signal check.

**Manual fallback.** With no typesetting toolchain: write the filled source anyway, report the render
SKIPPED, and hand the caller the bundle's build commands verbatim so a human can produce and check
the PDF. With no extraction or font inspection: the export still happens, gates 3 and 4 are recorded
as not run with the commands to run them by hand, and the report says the render is not done.

**Troubleshooting.**

| Symptom | What it means here |
|---|---|
| Build errors that vanish when a font size or margin is changed | Out of scope by construction. The fix is content or escaping, never style. |
| The export needs two pages | Gate 2 red — report the overflow to the caller, who resolves it under the content-first fit policy the document's contract family declares; do not shrink anything here. |
| Extraction loses side-column text | Gate 3 red — report with both extracts; the remedy the bundle recommends (for the shipped template: simplify the layout, single-column fallback) is the caller's decision. |
| The document holds supported content the bundle has no zone for | Stop and ask. Never improvise a zone. |
| The bundle's policy contradicts the settings the caller passed | Stop and ask. Never override the bundle and never override the caller. |
| A gate cannot run because a tool is missing | Not a failure: mark it not run, report SKIPPED with the manual instructions, and keep the rest of the sequence. |

## Dependencies

| Name | Kind | Needed for | Required / optional | When unbound |
|---|---|---|---|---|
| Typesetting toolchain named by the resolved template bundle's `runbook.md` | capability | Building a PDF from the filled template source when a bundle other than the shipped default is registered. | required | The filled typeset source is still written; the render step is reported SKIPPED with the bundle's manual build instructions, and every gate is recorded as not run. |
| `pdflatex` (pdfTeX) | tool | Compiling the shipped `ats-onepage-latex` template; it uses pdfTeX primitives (`\pdfgentounicode`, `\pdfliteral`) and is not portable to XeTeX or LuaTeX unchanged. | required for the shipped template (and any bundle whose runbook names it) | As above — filled source written, render reported SKIPPED with the commands from `templates/ats-onepage-latex/runbook.md`. |
| The LaTeX packages the shipped template loads — `geometry`, `fontenc`, `inputenc`, `lmodern`, `babel`, `microtype`, `xcolor`, `enumitem`, `paracol`, `needspace`, `etoolbox`, `fontawesome5`, `hyperref` | component-set | The same compile: every one of them is loaded by the template's own preamble, so `pdflatex` alone does not make it build. Check, one command per package: `kpsewhich geometry.sty`, `kpsewhich fontenc.sty`, `kpsewhich inputenc.sty`, `kpsewhich lmodern.sty`, `kpsewhich babel.sty`, `kpsewhich microtype.sty`, `kpsewhich xcolor.sty`, `kpsewhich enumitem.sty`, `kpsewhich paracol.sty`, `kpsewhich needspace.sty`, `kpsewhich etoolbox.sty`, `kpsewhich fontawesome5.sty`, `kpsewhich hyperref.sty` — each prints a path and exits 0 when the package is present. | required for the shipped template | As above. A minimal installation typically lacks `paracol` and `fontawesome5`; the remedy is the distribution's own package manager, named in `templates/ats-onepage-latex/runbook.md`, and the packages are never dropped from the preamble to make a build succeed. |
| Rendered-document text extraction (normal and layout-preserving) | capability | Gate 3 — confirming the export's text survives extraction in plain reading order **and** in a mode that preserves the page's column layout, so that cross-column interleaving and lost side content are visible. | required | The export is still produced; gate 3 is recorded as **not run** with the manual commands from the bundle's runbook, and the render is reported not done rather than passed. |
| `pdftotext` (Poppler- or Xpdf-compatible) | tool | Running the bundled `scripts/pdf_text_check.py`, which invokes the extractor as `<command> [<layout-flag>] <pdf> -` and passes `-layout` literally, so this one calling convention is what the script assumes. Version probe argument: `-v` — these builds do not answer to `--version`. | required for the bundled script | The capability above still satisfies gate 3; the script is reported SKIPPED and the two extractions are run by hand from `templates/ats-onepage-latex/runbook.md`. |
| `pdffonts` (Poppler- or Xpdf-compatible) | tool | Gate 4 — confirming every font in the export is embedded. Version probe argument: `-v`. | required | Gate 4 recorded as not run with the manual command; never assumed to pass. |
| `pdfinfo` (Poppler- or Xpdf-compatible) | tool | Gate 2 — reading the export's page count against the page target. Version probe argument: `-v`. | required | Gate 2 recorded as not run; the report states that the page target could not be verified instead of claiming it was met. |
| `python3` ≥ 3.10 | tool | Running the bundled `scripts/pdf_text_check.py`. Answers to `--version`. | optional | Run the two extraction commands from the bundle's runbook by hand and read the extracts; gate 3 is still evaluable, just manually. |
