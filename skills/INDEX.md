# Skills index

Name → file for every skill package and every other document in this directory. A skill name used
anywhere in this package resolves here.

## Skills

Every skill here orchestrates several roles end to end. This is the whole of what may be invoked
directly; locations are written from the package root.

| Name | File | Purpose in one line |
|---|---|---|
| `connect-environment` | `skills/connect-environment/SKILL.md` | Connects this package to a machine and to one project: the harness in use and the local rules file it auto-loads, what the flows need from the user, the dependency matrix, and — only on the user's assent, item by item — closing the gaps it found and making these skills discoverable. |
| `generate-targeted-cv` | `skills/generate-targeted-cv/SKILL.md` | Produces the truthful, target-specific CV for one vacancy: job-side analysis, cited evidence retrieval, writing, checking, rendering, external checks, gap report, bank update brief, ledger close. |
| `refresh-knowledge-bank` | `skills/refresh-knowledge-bank/SKILL.md` | Rebuilds the knowledge bank from the canonical experience sources, with the curator's self-check and coverage gates, source metadata, and the refresh log. |

## Other documents

The first two are documents of this directory; the third is the index next door, listed so that a
reader who came here looking for a tool is not stranded.

| Name | File | Purpose in one line |
|---|---|---|
| `skill-conventions` | `skills/skill-conventions.md` | The house rules for every skill package: layout, frontmatter and the name rule, the required section set, the settings section, and the `## Dependencies` declaration format. |
| `BACKLOG` | `skills/BACKLOG.md` | The deferred-work ledger: planned but unbuilt workflows, tools, roles, adapters and migrations. Entries have no authority. |
| the tools index | `tools/INDEX.md` | Where a tool name resolves. The single-operation packages — the renderer, the validators — are **tools**, not skills: they are internal, they are never listed here, and `tool-conventions` governs them. |
