#!/usr/bin/env python3
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python scripts/create_job.py <job-slug>")
    sys.exit(1)
job = sys.argv[1]
for base in [Path("data/jobs")/job, Path("outputs")/job, Path("outputs")/job/"external_validators", Path("outputs")/job/"exports", Path("outputs")/job/"render"]:
    base.mkdir(parents=True, exist_ok=True)
files = {
    Path("data/jobs")/job/"job_description.md": "# Job Description\n\nPaste job description here.\n",
    Path("data/jobs")/job/"recruiter_notes.md": "# Recruiter Notes\n\nPaste recruiter notes here.\n",
    Path("data/jobs")/job/"company_notes.md": "# Company Notes\n\nOptional.\n",
}
for path, content in files.items():
    if not path.exists(): path.write_text(content, encoding="utf-8")
print(f"Created job workspace for {job}")
