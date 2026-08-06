# Contract: render-manifest

Version: 1.0

## Purpose

The render manifest records what happened when a document was turned into its final file: which
template produced it, which mechanical gates were run and how they came out, what was exported, and
whether the export is named correctly.

Rendering is the step where a document can silently stop being readable — text lost between columns,
fonts not embedded, a heading swallowed by decoration. This artifact is the evidence that it did not.

## Status values

- `pass` — every mechanical gate is green and the exports match the naming rule;
- `fail` — a gate failed; the exports are not deliverable as they stand;
- `blocked` — rendering could not run to completion (a required capability is not bound, an input is
  missing). Recorded with instructions, never a silent absence.

## Envelope

The common envelope applies. `inputs:` names the source document with its revision, the template
identity, and the validation reports that cleared the document for rendering.

## Sections

### `## Render`

| Field | Meaning |
|---|---|
| source document | The document rendered, with its revision. |
| template | The template's name and version, and whether it came from a user-recorded setting or the shipped default. |
| target | The intended page count and any other target property the calling operation set. |
| naming rule | The export naming rule the caller passed, and the identity values used to instantiate it. |
| run source | The intermediate render source file produced, when the template produces one. |

The template identity matters: a document rendered under a different template version is a different
artifact, and a later reader must be able to tell.

### `## Mechanical gates`

One row per gate, each `green` / `red` / `not run` with the observed result:

| Gate | Requirement |
|---|---|
| compile | The render source builds cleanly, run twice so that cross-references and layout settle. |
| page count | The output matches the target, or the overflow is quantified. |
| fonts | All text fonts are embedded. |
| text extraction — reading order | Extraction in normal reading order returns the document's text. |
| text extraction — layout preserving | Extraction in layout-preserving mode returns the same facts without cross-column interleaving or lost side content. |
| content survival | Headings, the candidate name, contact facts, position titles, dates, bullets, skills, education and languages are all present in the extracted text. |
| visible text | No critical fact is carried only by an icon, a decoration, a color, a position, or an extraction-time label substitution. |

A red gate is a `fail`. It is never waived by declaring the visual result good: a file that looks
right and extracts badly fails.

### `## Fit outcome`

Whether the content fitted the target, and what was done if it did not.

**The template is never restyled to make content fit.** Geometry, margins, font sizes, spacing,
colors, column widths, section styling and visual components stay as the template defines them. When
validated content overflows, the renderer **reports the overflow back to the caller** — with the
amount and the sections involved — so that the content can be revised by the role that owns it. When
edits free space, the manifest records that, so the space can be reused for the strongest supported
target-relevant material.

This section states which of those happened, and what the caller must do next.

### `## Exports`

One row per exported file: path, format, size, and the naming check against the naming rule (`match`
or `mismatch`, with the expected name). An export whose name does not match the rule is a finding,
not a detail — downstream steps and the user both address files by that name.

Intermediate and compatibility artifacts are listed separately and marked as such, so they are never
mistaken for the deliverable.

### `## Notes`

Anything a later reader needs: a warning that did not fail a gate, a template quirk worked around, a
capability that was unavailable and how the step compensated.

### `## Constraint proposals`

Guardrails discovered while rendering — for example a content pattern that reliably breaks
extraction and should be avoided in the document itself. See `artifact-conventions.md`. `None.` when
there is nothing to propose.

## Rules

- **Gates are recorded with their observed result**, not as a bare tick. "Extraction preserved all
  headings and dates" is a record; "OK" is not.
- **A content change after rendering invalidates the checks that ran before it.** The manifest states
  what changed, so the caller can re-run the truthfulness check and the affected registered checks.
- **The renderer never edits the document's content**, and never adds a fact that was not in it.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | `renderer.render-document` |
| Consumers | `reviewer` (gate state before external checks), the user, `experience-writer` (when an overflow requires a content revision) |
