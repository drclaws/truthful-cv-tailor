# Contracts index

Name → file for every document in this directory. A contract name used anywhere in this package
resolves here. Locations are written from the package root.

## Contracts

Persistent — artifacts that outlive a single run:

| Name | File | Purpose in one line |
|---|---|---|
| `user-context` | `contracts/user-context.md` | What the flows need from the user, and how they resolve it. |
| `knowledge-bank` | `contracts/knowledge-bank.md` | The persistent, cited cache of what the canonical sources say about the candidate. |
| `constraints-ledger` | `contracts/constraints-ledger.md` | Negative evidence: the guardrails that keep later runs from re-making a caught mistake. |
| `transcript` | `contracts/transcript.md` | The written record of a spoken conversation, so that what was said can be cited. |
| `job-dossier` | `contracts/job-dossier.md` | The job-side inputs of one run, stored as files rather than as a summary. |

Per-run:

| Name | File | Purpose in one line |
|---|---|---|
| `run-manifest` | `contracts/run-manifest.md` | The single place that says what happened in a run: steps, gates, context, artifact index. |
| `source-audit` | `contracts/source-audit.md` | The run's audit trail of inputs: what was read, in what state, with what standing. |
| `requirements-profile` | `contracts/requirements-profile.md` | The structured reading of the vacancy — the target every later step aims at. |
| `recruiter-signals` | `contracts/recruiter-signals.md` | What the conversation revealed that the vacancy text does not say. |
| `evidence-map` | `contracts/evidence-map.md` | Per requirement: what the evidence actually says, and how strongly. |
| `cv-document` | `contracts/cv-document.md` | The candidate-facing deliverable in text form, and the CV format itself. |
| `validation-report` | `contracts/validation-report.md` | One uniform envelope for every check performed on a document. |
| `external-gate-decision` | `contracts/external-gate-decision.md` | The verdict and destination given to each external recommendation. |
| `fit-report` | `contracts/fit-report.md` | Candidate against vacancy: match, strength, risk, and whether applying is worth it. |
| `gap-report` | `contracts/gap-report.md` | The honest account of what this application does not have. |
| `render-manifest` | `contracts/render-manifest.md` | What happened when a document became its final file, and how the mechanical gates came out. |
| `bank-update-brief` | `contracts/bank-update-brief.md` | The answerable questions a run raises about the candidate's evidence. |

## Other documents in this directory

| Name | File | Purpose in one line |
|---|---|---|
| `artifact-conventions` | `contracts/artifact-conventions.md` | The rules every contract inherits: scope, artifact naming, the common envelope, truthfulness, run isolation, constraint proposals, versioning, and who writes what. |
| `engine-conventions` | `contracts/engine-conventions.md` | The rules a run obeys: the invariants, the reference grammar, where this package sits on the machine, what a step loads, and where a run writes. Every public entry point loads it first. |
| `predecessor-map` | `contracts/predecessor-map.md` | Archival: each rule of the deleted predecessor engine mapped to the file that owns it now. |
