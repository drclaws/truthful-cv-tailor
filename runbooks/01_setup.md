# Setup Runbook

1. Install an AI coding assistant or local automation runner.
2. Install Python 3.10+.
3. Install LaTeX, Poppler tools, and Pandoc.
4. Create and activate a local Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

5. Install browser automation dependencies only when running browser-based
   validators such as Enhancv:

```bash
python -m pip install playwright
python -m playwright install chromium
```

6. Keep local assistant settings outside git.
7. Provide canonical candidate and job inputs for the first run. Inputs may be
   included directly in the request or saved in local files referenced by the
   request.
8. Optionally create a reusable job folder:

```bash
make new-job JOB=company-role
```

9. If using a job folder, fill `data/jobs/company-role/job_description.md` and
   `recruiter_notes.md`.
