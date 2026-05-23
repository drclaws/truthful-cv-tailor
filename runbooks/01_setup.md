# Local Setup Runbook

Use this only when the local machine is missing tools. The agent can check these
items during a run and report what needs to be installed.

## Tool Checklist

- Python 3.10+
- LaTeX with `pdflatex`
- Poppler/Xpdf tools: `pdftotext`, `pdffonts`, `pdfinfo`
- Pandoc for DOCX export
- Python Playwright and Chromium only for browser-based Enhancv validation

## Optional Python Environment

Create a local environment when package isolation is useful:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install browser automation dependencies only when running browser-based
validators such as Enhancv:

```bash
python -m pip install playwright
python -m playwright install chromium
```

Keep local assistant settings outside git.

## Input Setup

Provide canonical candidate and job inputs in the request, or save them in local
files referenced by the request. Optionally create a reusable job folder:

```bash
make new-job JOB=company-role
```

If using a job folder, fill `data/jobs/company-role/job_description.md` and
`recruiter_notes.md`.
