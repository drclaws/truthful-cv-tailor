# Truthful CV Tailor

A set of **toolchains for CV and job-search work**, driven by an AI agent: they turn your canonical
experience sources plus one vacancy's material into a truthful, ATS-friendly, target-specific CV —
rendered to PDF, checked at every step, with the gaps written down instead of papered over.

The repository ships **no personal data and no machine settings**. It defines *what* the flows need;
you connect it to your own environment once, and the connection lives in your local rules file,
outside version control.

Three guarantees shape everything in here:

1. **Truth first.** Nothing is invented. Weak evidence is called weak, an unsupported requirement
   becomes a recorded gap, and machine-readability never outranks the truth.
2. **One source of candidate facts.** A knowledge bank, built from your canonical sources by a single
   role, is the only thing the CV flow reads about you — so every claim is traceable to a citation.
3. **Validation is independent and advisory.** The reviewer never edits the CV; external services
   never edit it either, and their scores are never treated as truth.

## Quickstart

```text
1. Connect the repository to your environment — once:
   invoke the setup-master role (roles/setup-master/ROLE.md), capability `bootstrap`.

2. Build the knowledge bank from your experience sources:
   execute skills/workflows/refresh-knowledge-bank/SKILL.md

3. Produce a CV for one vacancy:
   execute skills/workflows/generate-targeted-cv/SKILL.md for <run-id>
```

Step 3 wants a job dossier — at minimum a job description — under the run's `position/` directory;
the flow's scaffolding script creates the stubs for you to fill. The result lands in
`outputs/generate-targeted-cv/<run-id>/`: the manifest `run.md` with every step and gate, the
analysis artifacts, the checked document, the rendered PDF under `exports/`, and the gap report.

No harness auto-discovers the `skills/` directory yet, so flows are invoked **by path**, exactly as
above. Agent-side details, invariants and catalogs live in [`AGENTS.md`](AGENTS.md).

## Setup

**Setup is a role, not a script: [`roles/setup-master/ROLE.md`](roles/setup-master/ROLE.md).** Invoke
it directly and it will do the asking. Its capabilities:

| Capability | What it does |
|---|---|
| [`bootstrap`](roles/setup-master/capabilities/bootstrap.md) | First run. Detects your harness, determines its local rules file (Claude Code: `CLAUDE.local.md`), and creates or updates it from the template in `contracts/user-context.md` — your experience sources, the active validation set, per-skill settings. Then checks the environment and recommends next steps. |
| [`update-settings`](roles/setup-master/capabilities/update-settings.md) | Revisit or change any recorded setting later. |
| [`register-skill`](roles/setup-master/capabilities/register-skill.md) | Activate a validation skill — one shipped here, or one that lives in your own environment. **This is also the guide for adding a new validator.** |
| [`check-environment`](roles/setup-master/capabilities/check-environment.md) | Aggregate every shipped and registered skill's `## Dependencies` section and report the dependency matrix: dependency → status → affected steps. |

The local rules file is gitignored (`*.local.md`) and must never be committed: it holds real paths
and personal data.

### What the flows can use

Every capability below is checked at setup time and again at run time. **An unbound capability is
never a failure** — the step that needed it runs SKIPPED or manual, with instructions, and the flow
continues. Only the truthfulness check is unskippable.

| Capability | Used by | Typical binding | Required? |
|---|---|---|---|
| Read access to your canonical experience sources | `refresh-knowledge-bank` | the harness's own file tools, or a shell that can reach them | required — the bank cannot be built without it |
| A question channel to you | both workflows | the interactive session | required — every escalation is a question, never a decision |
| A LaTeX-class typesetting toolchain | `render-cv-pdf` | `pdflatex` (pdfTeX) with the packages the shipped template names | required to produce the PDF |
| PDF text extraction and inspection | `render-cv-pdf`, `validate-cv-ats` | Poppler/Xpdf `pdftotext`, `pdffonts`, `pdfinfo` | required for the render gates |
| Browser automation | `validate-cv-enhancv` | a browser-driver package plus a browser build, in a session with a visible window | optional — external checks are advisory |
| A person with a browser | `validate-cv-resumly` | you, interactively | optional — the manual-mode external check |
| Web search | both workflows | any search binding the harness offers | optional — company/market enrichment, and verifying inferred capability names |
| Professional-network profile lookup | `generate-targeted-cv` | any binding that reaches public profiles | optional — people/team context for recruiter signals |
| `python3` ≥ 3.10 | the bundled scripts | a local interpreter | optional — every script has a documented manual fallback |
| Concurrent step execution | `generate-targeted-cv` | subagents, where the harness has them | optional — the parallel groups then run sequentially, with an identical result |

The exact, authoritative list is each skill's own `## Dependencies` section; the table above is the
overview. PDF is the only deliverable this repository produces.

## How it fits together

- **Contracts** (`contracts/`) define the format and semantics of every artifact — and never its
  location. Paths are computed by the flow and passed to roles as explicit parameters.
- **Roles** (`roles/`) are the actors: `setup-master`, `knowledge-bank-curator`, `vacancy-analyst`,
  `experience-writer`, `reviewer`, `renderer`. Each is a compact `ROLE.md` index card plus one file
  per capability. Roles never call each other — data flows only through artifacts.
- **Skills** (`skills/`) are the procedures: workflows orchestrate roles end to end; tools wrap one
  operation and can also be run on their own.
- **Outputs** (`outputs/`) is the single output root: the knowledge bank, plus one directory per run.
  Gitignored in full.

## Repository map

```text
AGENTS.md                                    Agent entry point: invariants, skill and data catalogs
README.md                                    This file
contracts/README.md                          Envelope, contract index, predecessor coverage matrix
contracts/*.md                               One file per artifact contract
roles/README.md                              Role-card template, interaction model, conventions
roles/<role>/ROLE.md                         Compact index card per role
roles/<role>/capabilities/<name>.md          Full rules of one capability
roles/<role>/scripts/*.py                    Role-owned helpers, explicit CLI arguments only
skills/workflows/<flow>/SKILL.md             End-to-end flows
skills/tools/<tool>/SKILL.md                 Single-operation skills, incl. the validators
skills/tools/render-cv-pdf/templates/        Shipped CV template bundles (default: ats-onepage-latex)
skills/BACKLOG.md                            Deferred work; entries have NO authority
outputs/knowledge-bank/                      The knowledge bank (gitignored)
outputs/<flow>/<run-id>/                     One directory per run (gitignored)
```

## Privacy and git hygiene

This repository is safe to publish. Ignored by default: everything under `outputs/` (the knowledge
bank, every run, every export), the harness-native local rules file (`*.local.md`), local
AI-assistant settings (`.claude/`, `.codex/`, `.cursor/`, `.continue/`, `.windsurf/`, …), virtual
environments, LaTeX byproducts, and rendered PDF/DOCX files.

The rule behind the list: **committed files carry rules and scripts, never personal data.** Real
paths, real names and real job material belong in your local context and in `outputs/`. Committed
examples use placeholders.

## License

See [LICENSE](LICENSE).
