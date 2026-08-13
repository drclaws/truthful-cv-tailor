# Tools index

Name → location for every tool package and every other document in this directory. A tool name used
anywhere in this package resolves here.

## Tools

A tool name resolves to the file below: the package directory, and `TOOL.md` inside it. Tools are
**internal** — they are reached from a workflow step, from `reviewer.run-check`, or by a user naming
one directly, and never from a discovery surface. Locations are written from the package root.

| Name | File | Purpose in one line |
|---|---|---|
| `render-cv-pdf` | `tools/render-cv-pdf/TOOL.md` | Renders a final CV document into the delivered PDF through the resolved template bundle and runs the mechanical render gates; reports overflow back instead of restyling the template. |
| `validate-cv-ats` | `tools/validate-cv-ats/TOOL.md` | Internal ATS structural check: is the CV machine-readable, and does it cover the vacancy's keywords. Executed by the reviewer. |
| `validate-cv-enhancv` | `tools/validate-cv-enhancv/TOOL.md` | External, advisory check submitted through a real browser session; the raw report is captured verbatim for the reviewer to normalize. |
| `validate-cv-resumly` | `tools/validate-cv-resumly/TOOL.md` | External, advisory check in manual mode: a person submits the PDF and transcribes the report verbatim. |

## Other documents in this directory

| Name | File | Purpose in one line |
|---|---|---|
| `tool-conventions` | `tools/tool-conventions.md` | The house rules for every tool package: layout, frontmatter and the name rule, the required section set, and what a tool is not — a workflow's caller, an actor, or a discoverable thing. |
