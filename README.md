# CV Tailoring Pipeline Starter Kit

Starter kit for a truthful, ATS-friendly CV tailoring pipeline.

The project is designed around these guarantees:

1. **Truth first**: final CV claims must be supported by canonical candidate inputs.
2. **Position fit**: each generated CV is checked against the target job.
3. **ATS safety**: final CV is rendered through an ATS-gated LaTeX template and validated with local checks.
4. **External validators are last and advisory**: enabled registered validators run after local gates unless explicitly disabled. Their reports can suggest improvements, but cannot modify the CV directly.
5. **Flexible plugins**: new external validators can be added through `validators/external/registry.yaml`.
6. **Useful scan signals survive**: optional render tags can preserve verified
   hiring-manager signals that are relevant but do not need primary CV space.

## Quick start

```bash
cd cv-codex-agent-starter

make new-job JOB=example-company-role
# Provide canonical candidate/job inputs and optionally refresh data/master/*.md indexes
make source-check SOURCES="path/to/original_cv.md path/to/linkedin.md"
```

## Run The Pipeline

After creating a job folder and adding candidate/job inputs, run the workflow
from the project root with your preferred local automation setup. The project
policy lives in `AGENTS.md`, and the stage templates live in `prompts/`.

## Recommended Local Tools

Required for best results:

- An AI coding assistant or local automation runner
- Python 3.10+
- LaTeX distribution with `pdflatex`
- `pdftotext`, `pdffonts`, `pdfinfo` from Poppler/Xpdf-compatible tooling
- `pandoc` for DOCX export

Optional:

- Playwright MCP for browser-based job page extraction or external validator automation
- Python Playwright for local browser-based validators such as Enhancv:
  `python3 -m pip install playwright && python3 -m playwright install chromium`
- MarkItDown CLI/MCP for importing old PDF/DOCX resumes into Markdown

## Main workflow

```text
1. Job Parser
2. Recruiter Signal Extractor
3. Evidence Mapper
4. CV Writer
5. Fact Validator
6. ATS Static Validator
7. Position Match Validator
8. Template Renderer into LaTeX
9. PDF/DOCX Export
10. External Validator Runner, unless explicitly disabled
11. External Report Normalizer
12. External Validation Gate
13. Final Fact + ATS re-validation
```

## Important files

```text
AGENTS.md                                  Project operating policy
prompts/*.md                               Stage templates for the workflow
templates/cv-ats-agent-template.tex        Production ATS-gated LaTeX template
templates/template_policy.md               Rules for safe rendering
data/master/experience_bank.md             Derived candidate evidence index
data/master/projects.md                    Derived project evidence index
data/master/skills_matrix.md               Derived skills evidence index
data/master/constraints.md                 Persistent truth and safety constraints
data/jobs/<job>/*.md                       Per-job inputs
outputs/<job>/*                            Generated artifacts and reports
validators/external/registry.yaml          External validator plugin registry
scripts/*.py                               Local ATS and keyword checks
Makefile                                   Convenience commands
```

Use `make source-check SOURCES="..."` when canonical inputs are files. It
compares source modification times against `experience_bank.md`, `projects.md`,
and `skills_matrix.md` and reports whether the derived indexes need refresh.

## Safety rule

Never let external validators directly modify the CV. Import their reports,
normalize them, pass them through `External Validation Gate`, then re-run `Fact
Validator`. Final exports in `outputs/<job>/exports/` should be named with the
`FirstNameSurname\..*` pattern, for example `JaneDoe.pdf` and `JaneDoe.docx`.

## Git hygiene

This starter kit is safe to publish with the included `.gitignore`: generated
CV outputs, validator artifacts, private candidate indexes in `data/master/`,
real per-job inputs in `data/jobs/<job>/`, local AI-assistant/agent settings
such as `.codex/`, `.claude/`, `.cursor/`, `.continue/`, and `.windsurf/`,
virtual environments, and rendered PDF/DOCX files are ignored by default.

Keep reusable examples under `data/jobs/example-company-role/`. Put real
candidate evidence, recruiter notes, job inputs, and generated exports only in
ignored paths unless they have been explicitly sanitized.
