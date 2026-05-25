# Run Pipeline

All steps run through the agent. Start a full run with a request like:

```text
Run the full CV tailoring pipeline for data/jobs/company-role.
Follow AGENTS.md and prompts/00_full_pipeline.md.
```

After `08_final_cv.md` exists, ask the agent to run local checks and review the
results, for example:

```text
Run scripts/ats_static_check.py and scripts/keyword_match.py for
outputs/company-role, then review the reports and update ATS validation only
where facts are supported.
```
