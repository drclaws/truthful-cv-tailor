# Run Pipeline

```bash
make pipeline JOB=company-role
```

Or explicitly:

```bash
codex "Run the full CV tailoring pipeline for data/jobs/company-role. Follow AGENTS.md and prompts/00_full_pipeline.md."
```

After `08_final_cv.md` exists:

```bash
make ats JOB=company-role
make keyword JOB=company-role
```

Then ask Codex:

```bash
codex "Review outputs/company-role/06_ats_static_check.md and outputs/company-role/keyword_match.md. Update ATS validation and only change the CV where facts are supported."
```
