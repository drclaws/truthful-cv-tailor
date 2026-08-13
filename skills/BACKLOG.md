# Skills backlog

The **deferred-work ledger**: planned but NOT yet done work of every kind — skills, tools, roles,
harness adapters, and one-off migrations. It lives in this directory but is not limited to it; two
of its entries are tools, which belong to a different directory entirely. It exists so that a
decision already taken ("we
will need a scouting flow, and it will consume the requirements-profile contract") is written down
once, instead of being rediscovered or silently reinvented later.

## Entries have NO authority

This is the hard rule of this file, and it admits no exceptions:

- **An agent must never execute a backlog item as if it existed.** An entry is a note about
  something that has not been built. It is not a specification, not a permission, and not an
  instruction. Referencing an entry as though it were a shipped skill, role, or contract is a
  defect.
- **Nothing here may be cited as a rule or an authority** by a flow, a role, a contract, or an
  artifact. If a step needs a rule, that rule must live in an authoritative file — a contract, a role
  package, or a skill — the same promotion rule that run isolation imposes on run outputs.
- **Promotion happens only when the user asks for the item to be built.** At that point the item
  becomes a real skill or role in its own directory, with its contracts and dependencies declared,
  and its entry is **removed from this file**. An item is either here or built — never both.
- A backlog entry is therefore also the correct answer to "can you run X?" when X only appears
  here: X does not exist yet; say so and offer to build it.

## Entry format

One entry per item, as a level-3 heading, with these fixed fields in this order. Fields are never
omitted; when a field has no content, write `None.` or `To be defined.` rather than dropping it.

```markdown
### <name>

- **Kind:** workflow | tool | role | adapter | migration
- **Intent:** one paragraph — what it does, for whom, and why it is worth building. Enough for a
  reader to judge whether it is still wanted; not enough to be mistaken for a specification.
- **Contracts produced:** contract names this item would write, or `None.`
- **Contracts consumed:** contract names this item would read, or `None.`
- **Dependencies / notes:** what it needs before it can be built — other backlog items, abstract
  capabilities, external data, open questions. Concrete tool names are allowed here only as
  examples of a capability, never as a binding.
```

Entries are grouped by kind, and ordered within a group by name. Naming follows the same convention
as shipped skills (`<verb>-<object>`, lowercase, hyphenated).

## Entries

Grouped by kind — workflows, then tools, then roles, then adapters, then migrations — and ordered by
name within each group. An absent entry means the item was never planned, not that it may be
improvised.

### prepare-linkedin-profile

- **Kind:** workflow
- **Intent:** Produce a truthful professional-network profile — headline, about section, per-position
  descriptions, skills — from the same knowledge bank the CV flow uses, so that the profile and the
  CV never drift apart or contradict each other. It is worth a flow of its own rather than a variant
  of the CV flow because the deliverable is text pasted into a web form: no render step, no page
  target, no export, but a platform-specific shape and a much longer shelf life, which changes what
  "truthful" has to survive. The roles it needs already exist and are already format-agnostic —
  `experience-writer` takes its document shape from a format contract passed in, and
  `reviewer.fact-check` explicitly checks any candidate document rather than assuming a CV.
- **Contracts produced:** a new `profile-document` contract (the platform's shape: field lengths,
  section set, what may carry a claim), plus `run-manifest`, `validation-report`, `gap-report`,
  `bank-update-brief`.
- **Contracts consumed:** `user-context`, `knowledge-bank`, `constraints-ledger`, `evidence-map`, and
  `requirements-profile` when the profile is aimed at a class of roles.
- **Dependencies / notes:** the `profile-document` contract has to be written first — everything
  CV-specific in `cv-document` (the header title, position headers, one-page compression) is exactly
  what must not be carried over. Reading or updating a live profile would need a professional-network
  capability and is optional; a flow that only produces text to paste needs none. Open question:
  whether the profile is written per target audience or once, which decides whether
  `requirements-profile` is an input at all.

### scout-vacancies

- **Kind:** workflow
- **Intent:** Screen a batch of vacancies against the candidate's evidence and return a ranked
  shortlist with reasons, so that tailoring effort goes to the applications worth it. It scores each
  vacancy before any CV exists, which is precisely why `vacancy-analyst.score-fit` was kept
  input-format-agnostic: the bank is a legitimate candidate-data format, and the fit report declares
  which format it used. The output is a comparison, not a document — no writer, no renderer, no
  validators.
- **Contracts produced:** `run-manifest`, one `requirements-profile` and one `fit-report` per
  vacancy, and a new `shortlist` contract holding the ranked comparison with its caveats.
- **Contracts consumed:** `user-context`, `knowledge-bank`, `constraints-ledger`, and one
  `job-dossier` per vacancy.
- **Dependencies / notes:** vacancy intake is the unsolved part — a batch of dossiers has to come
  from somewhere, and web search or a job-search capability would be optional bindings rather than
  requirements. The `shortlist` contract must carry the fit report's own rule that scores are
  comparable only within one candidate-data format: ranking runs across vacancies scored the same
  way, or not at all. It writes no CV and must not — a shortlist entry is promoted by running
  `generate-targeted-cv` on it.

### query-bank

- **Kind:** tool
- **Intent:** Wrap `knowledge-bank-curator.query-bank` as a standalone skill, so that "what evidence
  do I have for X?" can be asked directly — preparing for an interview, judging whether a vacancy is
  worth pursuing, checking whether a claim is supported — without starting a CV run. The capability
  already has a single-query mode that answers inline and writes no artifact; what is missing is the
  skill wrapper that gives it a documented invocation, an output location for the batch case, and a
  `## Dependencies` section.
- **Contracts produced:** `evidence-map` in batch mode, and a minimal `run-manifest` for a standalone
  run. Nothing in single-query mode, by design.
- **Contracts consumed:** `knowledge-bank`, `constraints-ledger`, and `requirements-profile` for
  batch mode.
- **Dependencies / notes:** no new capability — it reads files the user already has. The open
  question is scope discipline: retrieval must not quietly become authoring, so the wrapper has to
  carry the capability's deliberate out-of-scope boundary rather than adding usage advice on top of
  the extracts.

### validate-cv-jobscan

- **Kind:** tool
- **Intent:** An external, advisory CV check on the Jobscan service, in the same shape as the two
  external validators this repository ships: service parameters, trust policy, a runbook covering
  environment preparation and the manual fallback, and a `## Dependencies` section. The predecessor
  carried it as a disabled registry entry — wanted, recognisable, not built — which is exactly the
  state this file exists to record.
- **Contracts produced:** a raw capture, which is not a contract instance. The `validation-report`
  that follows is written by `reviewer.normalize-external-report`, never by the tool.
- **Contracts consumed:** the run's final `cv-document` and its rendered deliverable, plus the job
  description its match-based checks need.
- **Dependencies / notes:** the service is account-gated and rate-limited, which is why it was
  disabled in the predecessor and the first thing to settle before building it. It would need browser
  automation or a human operator; both are capabilities, and the entry runs SKIPPED with instructions
  when neither is bound. Activation is `setup-master.register-skill` with kind `external` — no
  workflow change, because external placement is driven by the registered set.

### validate-cv-skillsyncer

- **Kind:** tool
- **Intent:** An external, advisory keyword-and-match check on the SkillSyncer service, in the same
  shape as the other external validators. Also inherited from the predecessor's disabled registry
  entries.
- **Contracts produced:** a raw capture, which is not a contract instance.
- **Contracts consumed:** the run's rendered deliverable and the job description.
- **Dependencies / notes:** it overlaps heavily with the keyword half of the shipped ATS check, so
  the first question is whether its advice adds anything the internal check does not already produce
  more cheaply and without sending the deliverable to a third party. Build it only if the answer is
  yes. Browser automation or a human operator, as above.

### transcriber

- **Kind:** role
- **Intent:** Import meeting recordings — recruiter screens, interviews, calls — as timestamped
  transcripts the vacancy analyst can read as people-side input. The output contract already exists
  (contract `transcript`), because the recruiter-notes format points at it; what does not exist is
  the role that produces one. Building it turns "the recruiter said something about the team's real
  problem" from a memory into a citable source, which is the difference between a positioning signal
  that can be attributed and one that cannot.
- **Contracts produced:** `transcript`.
- **Contracts consumed:** `None.` Its input is a recording or a live conversation, not a repository
  artifact.
- **Dependencies / notes:** needs a speech-to-text capability and, for multi-speaker calls, speaker
  attribution — both capabilities the user binds. Kept outside the repository so far because the
  recordings are personal data and the transcription may run anywhere. The hard rule it must carry
  from day one: a transcript is an emphasis-and-positioning source, never candidate evidence —
  nothing said in a conversation creates a candidate fact.

### split-legacy-constraints

- **Kind:** migration
- **Intent:** Separate a constraints ledger inherited from a predecessor structure into its two
  rightful homes. The negative-evidence guardrails — "do not claim X unless a canonical source adds
  it" — stay in the ledger, which is the only thing the `constraints-ledger` contract governs. The
  inherited sections that are positioning and style policy rather than negative evidence — how to
  position the candidate, which header title to use, which wording to avoid and which is allowed,
  which sections a document should cover, how to treat external validator advice — move to
  `## Additional rules` in the user's local rules file, which is where `user-context` puts the
  free-text preferences the flows honour. It is worth doing because the two kinds of statement carry
  different authority: one narrows what may be claimed and binds every consumer, the other shapes
  how a document reads and is the user's to change at will. Mixing them lets a preference be read as
  a factual limitation, which is exactly what the curator's ingest rules already refuse to allow for
  new proposals.
- **Contracts produced:** `constraints-ledger` (rewritten in the shape the contract defines) and
  `user-context` (the local rules file gains the moved sections).
- **Contracts consumed:** `constraints-ledger` (the imported file as it stands) and `user-context`.
- **Dependencies / notes:** this is the **user's action, not an automatic one**. The ledger is
  personal data in a gitignored location, and deciding which inherited section is policy and which
  is a real guardrail needs the user's judgement rather than a heuristic — a wrong call either drops
  a guardrail or freezes a preference into a binding rule. No agent performs the split on its own
  initiative, and the standing rule of this file applies with full force: until the user asks for
  it, it has not happened, and an imported ledger is read exactly as it is under the legacy-import
  allowance in contract `constraints-ledger`. Done once per ledger; there is nothing to build
  and nothing to schedule.
