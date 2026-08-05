# Contract: job-dossier

Version: 1.0

## Purpose

The job dossier is the set of **job-side inputs** for one run, stored as files so that later steps
cite stored text rather than a summary that no longer exists. Everything the run knows about the
vacancy, the recruiter conversation and the company originates here.

The dossier belongs to the run that holds it. Copying it into each run — including reruns of the same
vacancy — is deliberate: it is what makes a run self-contained and independently re-readable.

## Files

| File | Contents |
|---|---|
| job description | The vacancy text, stored as close to verbatim as the source allows. |
| recruiter notes | Screening signals, recruiter and hiring-manager statements, with a pointer to the `transcript` they were drawn from when one exists. |
| company notes | Company context: what it does, stage, market, team structure, anything that shapes positioning. |

Additional job-side files are allowed — notes on interviewers or team members, a public engineering
blog post, a product page. Each additional file states its own kind and source. Every file present is
listed in the run's `source-audit` and indexed in `run.md`.

A file with nothing to say is **omitted**, not filled with speculation. Its absence is recorded in
the source audit.

Placement (`<run>/position/` in the CV flow) is a flow decision and is not part of this contract.

## Status values

- `in-progress` — the dossier is still being assembled;
- `complete` — assembly finished; what is present is what the run will use.

## Envelope

The common envelope applies **per file**. `producer` is the flow scaffolding or the user, depending
on how the file was created. `inputs:` names where the content came from — a locator, a fetch date,
or a description when the original cannot be stored.

## Content rules

- **Store the original, not a retelling.** When the source can be stored, store it. When it cannot,
  record enough source metadata and enough extracted factual snippets to support later validation,
  and mark the file as a partial capture.
- **Provenance travels with the content.** Every file states where its content came from and when it
  was captured. Content assembled from several sources attributes each part.
- **Never mix in candidate evidence.** The dossier is job-side. Candidate facts live in the knowledge
  bank and in canonical experience sources.
- **Recruiter, interviewer and people/team inputs are emphasis-and-positioning signals only.** They
  say what the employer cares about. They can never create a candidate fact, upgrade an ownership
  claim, or license a skill.
- **Candidate self-reports made in a conversation are marked as self-reports** and carry the same
  restriction (see the `transcript` contract).
- **Conflicts are not resolved here.** Where two job-side sources disagree, both are stored and the
  conflict is recorded in the `source-audit`.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | the flow scaffolding, or the user supplying the inputs |
| Consumers | `vacancy-analyst` (source audit, job analysis, recruiter signals, fit, gaps), `reviewer` (verifying what a claim or signal rests on), `experience-writer` (targeting context, via the analyst's artifacts) |
