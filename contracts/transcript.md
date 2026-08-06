# Contract: transcript

Version: 1.0

## Purpose

A transcript is the written record of a spoken conversation relevant to a job search: a recruiter
screening call, a hiring-manager conversation, a technical interview, a debrief. It exists so that
what was actually said can be cited later, instead of being remembered.

This contract formalizes the external meeting transcripts that recruiter notes already point at. Its
producer — a meeting **transcriber** role — is not built yet; the contract is defined now so that
transcripts produced by any means (a transcription service, a harness, a person) are usable without
renegotiation.

## Status values

- `draft` — captured but not yet reviewed for speaker attribution and gaps;
- `final` — reviewed; safe to cite.

## Envelope

The common envelope applies. `run_id` is `n/a` — a transcript belongs to a conversation, not to a
run; runs reference it from their job dossier. `producer` is the transcriber role once it exists, or
`the user` when the transcript was produced outside the toolchain.

## Sections

### `## Metadata`

| Field | Rule |
|---|---|
| date | When the conversation happened (not when it was transcribed). |
| participants | Every speaker, with the role each played in the conversation (candidate, recruiter, hiring manager, interviewer, other). Speaker labels used in the dialogue must match these names. |
| related vacancy | The position the conversation concerns, or `none`. |
| language | The language spoken. When the transcript is translated, both languages are stated and the translation is marked as such. |
| recording reference | A locator for the source recording or capture, or `not retained`. |
| capture method | How the text was produced: live notes, automated transcription, automated transcription plus human correction. |
| completeness | `full` · `partial` (state which part) · `excerpt`. |

### `## Dialogue`

Timestamped turns, in order:

```markdown
[hh:mm:ss] <Speaker>: <what was said>
```

- **Verbatim by default.** Speech is recorded as spoken. Light cleanup of filler is acceptable and,
  when applied, is stated in the metadata; rewording that changes meaning is not cleanup.
- **Unclear audio is marked** `[inaudible]` or `[unclear: <best guess>]`. It is never filled in with
  a plausible sentence.
- **Gaps are marked** `[gap: <duration or description>]` where the recording is missing.
- **Editorial additions are bracketed** and attributed, so they can never be mistaken for speech.

### `## Notes` (optional)

Observations by the transcriber that are not speech: what was shown on screen, what was promised as
a follow-up, non-verbal context that affects meaning. Clearly separated from the dialogue.

## Evidence semantics — the rule consumers must not forget

A transcript is a record of **claims made in conversation**, not a canonical experience source.

- What a **recruiter or interviewer** says defines emphasis, priorities and context. It can never
  create a candidate fact.
- What the **candidate** says about themselves is a **self-report**. It is not canonical candidate
  evidence and does not license a CV claim on its own. It may reveal experience that the canonical
  sources under-document — that observation belongs in a `bank-update-brief` question, or leads the
  user to add the fact to a canonical source, after which the bank may carry it.

Consumers classify a transcript accordingly in the `source-audit`.

## Producer and consumers

| Direction | Roles |
|---|---|
| Producer | transcriber (planned; see `BACKLOG`) or the user |
| Consumers | `vacancy-analyst` (via the job dossier), `reviewer` (when checking what a signal was based on) |
