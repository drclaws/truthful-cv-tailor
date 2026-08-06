# Skills index

Name → file for every skill package and every other document in this directory. A skill name used
anywhere in this repository resolves here.

## Skills

**Workflows** orchestrate several roles end to end; **tools** wrap one concrete operation and are
invocable both from a workflow step and standalone.

| Name | Group | File | Purpose in one line |
|---|---|---|---|
| `generate-targeted-cv` | workflow | `workflows/generate-targeted-cv/SKILL.md` | Produces the truthful, target-specific CV for one vacancy: job-side analysis, cited evidence retrieval, writing, checking, rendering, external checks, gap report, bank update brief, ledger close. |
| `refresh-knowledge-bank` | workflow | `workflows/refresh-knowledge-bank/SKILL.md` | Rebuilds the knowledge bank from the canonical experience sources, with the curator's self-check and coverage gates, source metadata, and the refresh log. |
| `render-cv-pdf` | tool | `tools/render-cv-pdf/SKILL.md` | Renders a final CV document into the delivered PDF through the resolved template bundle and runs the mechanical render gates; reports overflow back instead of restyling the template. |
| `validate-cv-ats` | tool | `tools/validate-cv-ats/SKILL.md` | Internal ATS structural check: is the CV machine-readable, and does it cover the vacancy's keywords. Executed by the reviewer. |
| `validate-cv-enhancv` | tool | `tools/validate-cv-enhancv/SKILL.md` | External, advisory check submitted through a real browser session; the raw report is captured verbatim for the reviewer to normalize. |
| `validate-cv-resumly` | tool | `tools/validate-cv-resumly/SKILL.md` | External, advisory check in manual mode: a person submits the PDF and transcribes the report verbatim. |

## Other documents in this directory

| Name | File | Purpose in one line |
|---|---|---|
| `skill-conventions` | `skill-conventions.md` | The house rules for every skill package: layout, frontmatter and the name rule, the required section set, the settings section, and the `## Dependencies` declaration format. |
| `BACKLOG` | `BACKLOG.md` | The deferred-work ledger: planned but unbuilt workflows, tools, roles, adapters and migrations. Entries have no authority. |
