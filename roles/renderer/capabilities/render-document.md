# Capability: renderer.render-document

## Purpose

Produce the final deliverable from a finished document: fill the resolved template's agent-content
zones with the document's content, write the typeset source, export the PDF, run the mechanical
gates, and report the result. This capability is the last step that touches the deliverable — it
turns validated content into a file, and adds nothing of its own.

## Inputs

| Parameter | Contract / description | Required |
|---|---|---|
| `document` | `cv-document`, an instance with `status: final` | required |
| `template` | path to the template bundle resolved by the caller: the template source with its delimited agent-content zones plus the template's own policy (zone list, fill rules, escaping rules, section placement) | required |
| `settings` | the render operation settings the caller resolved — for example the page target. Applied as given | required |
| `export_name` | the export filename, or the naming rule to apply, as produced by the calling flow | required |
| `validation_reports` | zero or more `validation-report` instances accompanying the document | optional |

The renderer reads the document and the template; it resolves nothing on its own. If a needed input
was not passed, it asks rather than guessing.

## Outputs

| Parameter | Contract / description | Status values |
|---|---|---|
| `source_out` | the typeset source: the template with its agent zones filled | n/a (not a contract artifact) |
| `export_out` | the exported PDF at the filename the caller's naming rule produced | n/a (not a contract artifact) |
| `manifest_out` | `render-manifest` — template and version used, per-gate results, export inventory with the naming check, unresolved issues, `## Constraint proposals` | as declared by the `render-manifest` contract; a run with any gate red is reported as such, never as a success |

## Procedure

1. **Check the inputs.** The document exists and carries `status: final`; the template bundle exists
   and declares its agent-content zones; every output path was passed; the export filename or naming
   rule was passed. Note the template's name and version for the report.
2. **Read the template's own policy** from the bundle — which zones exist, what each accepts, how
   text must be escaped, where each section belongs in the template's layout. The template's policy
   governs the *how*; this capability governs the *what*.
3. **Copy, then fill.** Write the template source to `source_out` and work only there. Fill only the
   delimited agent-content zones, transcribing content from the document.
4. **Apply the fill rules** below (escaping, aliases, empty sections, optional fields, metadata).
5. **Build and export** by the operation rules of the calling render tool skill — the compile
   sequence, the page target, and the gate order are that skill's, not this role's.
6. **Run the mechanical gates** and record every result, red ones included.
7. **On a red gate, stop and report.** Never resolve a gate failure by changing the template's style
   or by silently cutting validated content — see *Failure and skip conditions*.
8. **Write the render report** at `manifest_out` per the `render-manifest` contract, including
   `## Constraint proposals` (`None.` when there is nothing to propose), and hand control back to the
   caller.

## Definition of done

The render is done when all of the following hold and are recorded in the report:

- the source compiled **twice**, cleanly, so that cross-references and layout have settled;
- text extraction of the export, in **both** reading order **and** layout-preserving mode, still
  yields the section headings, the contact details, the role titles and the dates — with **no
  cross-column interleaving** and no side content lost;
- **fonts are embedded** in the export;
- the **export filename matches the naming rule the calling flow passed**.

Any of these red means the render is not done: the report says so and the caller decides.

## Rules

**Zones and styling**

- Edit ONLY inside the template's delimited agent-content zones. Everything outside them —
  geometry, margins, font sizes, spacing, colours, column widths, section styling, visual components
  — is off limits.
- **Never restyle the template to fit content.** If validated content overflows the target, the
  overflow is reported back to the caller so the validated content can be revised; the renderer does
  not shrink, re-space, or re-column its way to a fit, and does not decide on its own which content
  to drop.
- The template bundle itself is never modified. All filling happens in the copy at `source_out`.

**Content**

- Content is transcribed, never authored: no invented fields, no added claims, no rewriting of the
  document's header title, section names, role titles, or dates at render time. If a title or wording
  looks improvable, that is a finding for the caller, not an edit.
- Leave no placeholder variable, no `TODO`, and no template sample text in the source or the export.
- **Empty optional sections are dropped** rather than rendered empty; an optional field the document
  does not support stays empty and its rendering stays disabled.
- Optional template features that would ADD content beyond the document — emphasis tags and similar —
  stay off unless the document or an accompanying validation report explicitly enables them. Turning
  one on by choice would be authoring. The defaults themselves belong to the `cv-document` contract
  and the template's policy.
- Identity and document metadata zones are filled only from the document and the values the caller
  passed — never from the renderer's own knowledge of the candidate.

**Escaping and extraction fidelity**

- Escape special characters in every piece of generated text exactly as the template's policy
  prescribes. An unescaped character is a defect even when the compile happens to survive it.
- **Profile links appear as aliases only**: the alias or handle alone, with no scheme, no host and no
  path prefix. The template builds the visible and the clickable form from the alias.
- Every fact must be carried by ordinary **visible text** in the export. Where the template offers an
  alternate-text mechanism for decorative elements, it may only LABEL a value — never carry one.

**Boundaries**

- The renderer never edits the source document, the knowledge bank, the constraints ledger, or any
  validation report.
- Guardrails discovered while rendering (a claim the template cannot support truthfully, a value that
  keeps arriving unescaped) are raised as `## Constraint proposals` in the report; the curator ingests
  them.
- Run isolation applies: another run's typeset source or export is never consulted as a style
  authority or as content.

## Failure and skip conditions

| Situation | What the renderer does |
|---|---|
| Content overflows the target and only a style change could make it fit | Stop before export. Report the overflow in the render report with what overflowed and by roughly how much, so the caller can route the document back for content revision. Never restyle, never silently cut. |
| A mechanical gate is red (compile, extraction, fonts, filename) | Record the gate, the evidence, and the suspected cause in the report; mark the render not done; hand back to the caller. |
| Document is not `status: final`, or contradicts an accompanying validation report | Do not render. Report the conflict and ask the caller — resolving it is the writer's and the reviewer's work, not the renderer's. The renderer never resolves such a disagreement in the document's favour: a validation report outranks the text it examined, so rendering the contradicted version is always wrong, and the renderer's own move is to stop rather than to apply the report itself. |
| The export filename or naming rule was not passed | Do not invent one. Ask the caller. |
| Supported content has no agent zone in the template, or the template's policy contradicts the caller's settings | Stop and ask; do not improvise a zone and do not override the template. |
| A required toolchain capability is unbound (no typesetting toolchain, no text extraction, no font inspection) | Do not fail the flow. Produce what is possible — normally the filled typeset source — and report the step as SKIPPED with the manual instructions from the render tool skill's runbook, stating which gates could not be run. |
