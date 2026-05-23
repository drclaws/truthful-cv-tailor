# Setup Runbook

1. Install Codex CLI.
2. Install Node.js/npm for MCP servers run through `npx`.
3. Install Python 3.10+.
4. Install LaTeX and Poppler tools.
5. Copy `.codex/config.toml.template` to `.codex/config.toml`.
6. Replace `/ABSOLUTE/PATH/TO/cv-codex-agent-starter` with your actual path.
7. From project root, run:

```bash
codex "Summarize active instructions and MCP configuration."
```

8. Provide canonical candidate inputs for the first run. Optionally refresh
   `data/master/experience_bank.md`, `data/master/projects.md`, and
   `data/master/skills_matrix.md` as derived evidence indexes.
9. Create first job:

```bash
make new-job JOB=company-role
```

10. Fill `data/jobs/company-role/job_description.md` and `recruiter_notes.md`.
