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

## Environment Setup

1. Install system tools:

```bash
# macOS example
brew install python pandoc poppler
```

Install a LaTeX distribution separately if `pdflatex` is not already available.
On macOS, BasicTeX or MacTeX both work.

2. Create and activate a local Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

The core scripts use the Python standard library. Install Python Playwright only
when you plan to run the browser-based Enhancv validator:

```bash
python -m pip install playwright
python -m playwright install chromium
```

3. Keep local assistant settings outside git. Directories such as `.codex/`,
`.claude/`, `.cursor/`, `.continue/`, and `.windsurf/` are ignored by default.

4. Verify the local tools you intend to use:

```bash
python --version
make --version
pdftotext -v
pandoc --version
pdflatex --version
```

## Prepare Inputs

Start each CV run with explicit inputs in the request or in files referenced by
the request:

- Candidate evidence: original CV, LinkedIn/profile notes, portfolio/project
  notes, GitHub/publication notes, or interview notes.
- Job targeting: job description, recruiter notes, company notes, and any
  provided team/interviewer context.
- Output target: job slug, target page count, export requirements, and whether
  external validators should run.

The optional project files under `data/master/` and `data/jobs/<job>/` are a
convenient local structure for repeated runs, but they are not the only valid
input format.

## Run The Pipeline

Run the workflow from the project root with your preferred local automation
setup. Include the candidate evidence, job targeting inputs, and desired output
target in the request, or reference local files that contain those inputs. The
project policy lives in `AGENTS.md`, and the stage templates live in `prompts/`.

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
