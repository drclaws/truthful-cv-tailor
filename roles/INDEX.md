# Roles index

Name → location for every role package and every other document in this directory. A role name or a
`role.capability` name used anywhere in this repository resolves here.

## Roles

A role name resolves to the package directory below; the role card is `ROLE.md` inside it, and a
`role.capability` name resolves to `capabilities/<capability>.md` in the same package — a naming
convention, so capabilities have no rows of their own. Locations are written from the package root.

| Name | Directory | Mission in one line |
|---|---|---|
| `setup-master` | `roles/setup-master/` | Connects the toolchains to the user's environment; prepares, never executes flows. |
| `knowledge-bank-curator` | `roles/knowledge-bank-curator/` | Builds and maintains the knowledge bank; the sole writer of the bank and the constraints ledger. |
| `vacancy-analyst` | `roles/vacancy-analyst/` | Everything about the vacancy and the candidate-to-vacancy fit. |
| `experience-writer` | `roles/experience-writer/` | Writes and revises candidate documents from evidence. |
| `reviewer` | `roles/reviewer/` | Independent QA; never edits the document under review. |
| `renderer` | `roles/renderer/` | Template-driven production of the final file. |

## Other documents in this directory

| Name | File | Purpose in one line |
|---|---|---|
| `role-conventions` | `roles/role-conventions.md` | The house rules for every role package: layout, interaction model, progressive disclosure, the two templates, tool abstraction, and the script conventions. |
