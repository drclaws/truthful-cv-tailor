# Contracts index

Name → file for every document in this directory. A contract name used anywhere in this repository
resolves here.

## Contracts

Persistent — artifacts that outlive a single run:

| Name | File | Purpose in one line |
|---|---|---|
| `user-context` | `user-context.md` | What the flows need from the user, and how they resolve it. |
| `knowledge-bank` | `knowledge-bank.md` | The persistent, cited cache of what the canonical sources say about the candidate. |
| `constraints-ledger` | `constraints-ledger.md` | Negative evidence: the guardrails that keep later runs from re-making a caught mistake. |
| `transcript` | `transcript.md` | The written record of a spoken conversation, so that what was said can be cited. |
| `job-dossier` | `job-dossier.md` | The job-side inputs of one run, stored as files rather than as a summary. |

Per-run:

| Name | File | Purpose in one line |
|---|---|---|
| `run-manifest` | `run-manifest.md` | The single place that says what happened in a run: steps, gates, context, artifact index. |
| `source-audit` | `source-audit.md` | The run's audit trail of inputs: what was read, in what state, with what standing. |
| `requirements-profile` | `requirements-profile.md` | The structured reading of the vacancy — the target every later step aims at. |
| `recruiter-signals` | `recruiter-signals.md` | What the conversation revealed that the vacancy text does not say. |
| `evidence-map` | `evidence-map.md` | Per requirement: what the evidence actually says, and how strongly. |
| `cv-document` | `cv-document.md` | The candidate-facing deliverable in text form, and the CV format itself. |
| `validation-report` | `validation-report.md` | One uniform envelope for every check performed on a document. |
| `external-gate-decision` | `external-gate-decision.md` | The verdict and destination given to each external recommendation. |
| `fit-report` | `fit-report.md` | Candidate against vacancy: match, strength, risk, and whether applying is worth it. |
| `gap-report` | `gap-report.md` | The honest account of what this application does not have. |
| `render-manifest` | `render-manifest.md` | What happened when a document became its final file, and how the mechanical gates came out. |
| `bank-update-brief` | `bank-update-brief.md` | The answerable questions a run raises about the candidate's evidence. |

## Other documents in this directory

| Name | File | Purpose in one line |
|---|---|---|
| `artifact-conventions` | `artifact-conventions.md` | The rules every contract inherits: scope, artifact naming, the common envelope, truthfulness, run isolation, constraint proposals, versioning, and who writes what. |
| `predecessor-map` | `predecessor-map.md` | Archival: each rule of the deleted predecessor engine mapped to the file that owns it now. |
