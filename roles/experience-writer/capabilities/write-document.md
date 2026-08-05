# Capability: experience-writer.write-document

## Purpose

Compose a candidate document from cited evidence: select the supported facts that best answer the
target's requirements, position them, and write them into the shape defined by the **document-format
contract passed in as a parameter**. The result is one instance of that contract, ready for the
reviewer.

This capability owns the **writing procedure** — how evidence becomes truthful prose. It does not
own the document's **shape**; that is the format contract's job (see *What this capability does not
define*).

## Inputs

| Parameter | Contract / description | Required |
|---|---|---|
| `document_format_contract` | The contract defining the document's shape, e.g. `cv-document`. Loaded before anything is written. | yes |
| `evidence_source` | `evidence-map` in a flow; another cited evidence artifact (e.g. `knowledge-bank`) when the role is invoked directly. The **only** admissible source of facts. | yes |
| `requirements_source` | `requirements-profile` — what the target asks for, must/nice split, keyword sets. | when the document targets a vacancy |
| `signals_source` | `recruiter-signals` — emphasis, pain points, the do-NOT-include list. | no |
| `constraints_ledger` | `constraints-ledger` — negative-evidence guardrails; binding when passed. | no |
| `in_run_proposals` | Constraint proposals raised by earlier steps of the same run, not yet ingested. Binding when passed. | no |
| `source_audit` | `source-audit` — the inventory of this run's inputs and their conflicts. | no |
| `additional_rules` | Free text the flow resolved from user context (wording preferences, things to avoid). Never overrides an invariant. | no |
| `output_path` | Where the document instance is written. | yes |
| `run_id`, `status` | Run identifier and the status the caller expects on the instance (as declared by the format contract). | yes |

## Outputs

| Parameter | Contract | Status values |
|---|---|---|
| `output_path` | one instance of `document_format_contract` | whatever that contract declares — typically `draft` from this capability; `revision: 1` |

Alongside the artifact, the capability returns to the caller: the positioning decisions it made, what
it deliberately omitted, every requirement it could not support (as gaps), and any constraint
proposals — placed in the artifact's own annex when the format contract declares one, and reported to
the flow otherwise.

## Procedure

1. **Load the format contract first.** Read `document_format_contract` end to end and treat it as the
   specification of the artifact: its section set and order, heading and entry conventions, block
   shapes, readability constraints, annex sections, envelope fields and status vocabulary. Never
   start drafting from an assumption about the shape; if the contract cannot be read, stop
   (see *Failure and skip conditions*).
2. **Inventory the evidence.** Read `evidence_source` completely and build a working list of
   supported facts, each with its citation and its strength marker. This list is the boundary of what
   may appear in the document. Note every item marked as a gap or carrying a constraint flag.
3. **Read the target.** From `requirements_source` take the must-have and nice-to-have requirements,
   the responsibilities, and the keyword sets; from `signals_source` take emphasis, pain points and
   the do-NOT-include list. Recruiter and people inputs are positioning signals only — they can never
   create a fact.
4. **Apply the guardrails before drafting.** Read `constraints_ledger` and `in_run_proposals` and
   strike anything they forbid out of the working list now, so that no forbidden claim is ever
   written and then hunted down later.
5. **Decide positioning.** Rank the working list by relevance to the target × evidence strength, and
   decide what leads, what is stated briefly, and what is left out. This ranking is the writer's own
   judgement, produced from requirements, signals and strength — see *Working from a neutral
   evidence-map*.
6. **Draft into the contract's shape.** Fill each element the format contract declares, using only
   items from the working list. One claim per statement; concrete and specific; where the evidence
   records an outcome, write the outcome rather than the duty. Where the evidence records only a
   responsibility, write the responsibility — do not manufacture an outcome to make it look stronger.
7. **Mirror the target's vocabulary, never its claims.** A supported fact may be renamed into the
   target's wording; a keyword with no supported fact behind it is never introduced. Where a required
   keyword has no support, it becomes a gap entry, not a phrasing exercise.
8. **Sanitize internal names.** Replace company-internal system and product names with short
   public-facing descriptions conveying the system's type and purpose — four words or fewer where
   possible. Publicly known products, platforms and services are named directly.
9. **Record the decisions.** Fill whatever decision annex the format contract declares — what was
   emphasized and why, what was deliberately omitted, the rationale behind judgement calls, and any
   optional elements offered as candidates rather than defaults. If the contract declares no such
   annex, hand the same notes to the calling flow instead of dropping them.
10. **Self-check before writing status.** Walk the finished document once, statement by statement:
    every claim traceable to a citation; no strength rounded up; no fact absent from the working
    list; no unresolved placeholder text; no forbidden claim; every element the format contract
    requires present, and none it forbids. Fix what fails, or escalate if it cannot be fixed
    truthfully.
11. **Write the envelope** per `contracts/README.md`: contract name and version, `producer:
    experience-writer.write-document`, run id, every input actually consumed with its contract name,
    the caller's status, `revision: 1`, and dates taken from the environment.

## Rules

### Evidence discipline

- The evidence source is the **only** admissible origin of facts. Background knowledge about the
  candidate, plausible inference, and anything remembered from elsewhere are not evidence.
- Every claim must be traceable to a canonical source through the citation attached to it in the
  evidence source. An uncited item is treated as absent.
- Strength markers are carried over as found. `Weak` evidence yields hedged wording or no claim at
  all — never confident wording.
- An unsupported requirement is reported as a gap. It is never implied, never approximated with an
  adjacent fact, and never covered by vaguer phrasing that a reader would take as a claim.
- Never invent experience, metrics, tools, employers, dates, titles, degrees or certifications, and
  never sharpen a recorded value (a range does not become its upper bound; "several" does not become
  a number).
- Optimization for keywords, scanning or fit never outranks truth.

### Working from a neutral evidence-map

The evidence source this capability receives is **retrieval output, not writing advice**. It reports,
per requirement, what evidence exists, with citation, strength, constraint flags and gap markers —
deliberately with no suggestion of where a fact should go, how it should be phrased, or how much
space it deserves. That is by design: placement is the writer's judgement, and no placement
mechanism is provided.

Consequently:

- Do not wait for, look for, or assume usage hints in the evidence source; their absence is normal.
- Derive placement and weight yourself, from the requirements, the signals and the evidence strength.
- Read the evidence source **in full** rather than only the entries that map to the loudest
  requirements — strong evidence that no requirement asked about is exactly what a neutral map
  cannot flag for you, and leaving it unused is the failure mode to guard against.
- If an evidence item looks unusable (ambiguous, uncited, or contradicted elsewhere), record it in
  the decision notes as unused-with-reason rather than silently dropping it.

### Scope discipline

- The writer selects and phrases; it does not verify. Verification is `reviewer.fact-check`, and the
  document is never described as validated by its own author.
- The writer does not score fit, does not write the gap report, and does not decide whether to apply.
  It reports the gaps it hit; the analyst owns their analysis.
- The knowledge bank and the constraints ledger are never modified. Guardrails discovered while
  writing are proposed, per the invariant on the role card.
- Another run's document is never consulted — not for content, not for wording, not for structure.

## What this capability does not define

Everything about the artifact's **shape** belongs to the `document_format_contract` passed in, and
must be read from there at run time:

- which sections the document has, what they are called, and in what order they appear;
- how the document's own heading or title is composed, and how far it may differ from the target's
  wording;
- the shape of an individual entry's heading (what elements it carries and how they are punctuated);
- whether compact scan annotations or similar optional decorations are permitted, and whether they
  are on or off by default;
- readability constraints — what markup is allowed, what must stay plain and linear, what is left to
  a later rendering step;
- which annex or notes sections the document carries, and whether it carries a `## Constraint
  proposals` section of its own.

`cv-document` is the format contract for CVs and is where the CV-specific answers to all of the above
live. This role holds none of them, so that the same writing procedure serves a professional-network
profile or any other candidate document by pointing it at a different format contract.

## Failure and skip conditions

| Condition | Behaviour |
|---|---|
| `document_format_contract` missing or unreadable | **Stop.** Nothing is written — the shape is not guessable. Report the missing contract to the flow. |
| `evidence_source` missing, empty, or without citations | **Stop.** Report it. A document written without cited evidence would violate the truthfulness invariant. |
| `requirements_source` absent for a targeted document | **Stop and ask** whether to proceed as an untargeted document. |
| A format rule can only be satisfied by an unsupported claim | **Escalate.** Leave the element out, record the conflict, and ask the user through the flow. |
| The constraints ledger forbids something a must-have requirement demands | Write the document without it, record it as a gap with the constraint reference, and flag it to the flow. |
| An optional input (`signals_source`, `source_audit`, `additional_rules`) is absent | Continue, and note in the decision record which optional inputs were unavailable. |
| Requirements remain unsupported after drafting | Not a failure. Gaps are the expected, honest outcome; they are recorded and handed on. |
