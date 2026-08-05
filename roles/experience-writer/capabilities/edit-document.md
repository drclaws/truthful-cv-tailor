# Capability: experience-writer.edit-document

## Purpose

Revise an existing candidate document so that validated findings, gate verdicts and caller
instructions are resolved — and **nothing else changes**. The output is a new revision (or a new
instance) of the same document-format contract, ready for the checks the flow decides to re-run.

This is the edit loop's only writing step. The reviewer finds and judges; the writer changes. The two
never swap roles.

## Inputs

| Parameter | Contract / description | Required |
|---|---|---|
| `document_path` | The existing document instance to revise. | yes |
| `document_format_contract` | The contract that instance obeys, e.g. `cv-document`. Loaded before editing. | yes |
| `findings` | One or more `validation-report` instances: findings with severity and required edits. | yes, unless `gate_decisions` or `caller_instruction` is supplied |
| `gate_decisions` | `external-gate-decision` — per-recommendation verdicts. | no |
| `caller_instruction` | An explicit revision request from the flow or a tool step — most commonly a length or fit request ("does not fit the target length; revise content"). | no |
| `evidence_source` | `evidence-map`, or another cited evidence artifact when invoked directly. Required whenever wording changes or content is re-selected — which is nearly always. | yes |
| `requirements_source` | `requirements-profile` — used to rank what to keep when content must shrink. | no |
| `signals_source` | `recruiter-signals` — emphasis and the do-NOT-include list. | no |
| `constraints_ledger` | `constraints-ledger`; plus any constraint proposals raised earlier in the same run. Binding when passed. | no |
| `output_path` | Where the revision goes: the same path (overwrite in place) or a new path for a new instance (e.g. the final alongside the draft). Decided by the flow. | yes |
| `status` | The status the caller expects on the result, from the format contract's vocabulary. | yes |

## Outputs

| Parameter | Contract | Status values |
|---|---|---|
| `output_path` | an instance of `document_format_contract` | as that contract declares; `revision:` incremented when the same path is overwritten, `revision: 1` when a new instance is created |

Alongside the artifact, the capability returns a **disposition list**: every finding and verdict with
what was done about it (applied / applied with rewrite / not applied, plus the reason), and an
account of what changed materially — the flow uses that to decide which checks re-run.

## Procedure

1. **Load the format contract and the document.** Read `document_format_contract`, then the current
   instance, including its envelope. Confirm the findings refer to *this* document and *this*
   revision; if they refer to another artifact or an older revision, stop and report it.
2. **Build the change list.** Enumerate every finding (with its severity and required edit), every
   gate verdict, and the caller instruction. Classify each item before touching the text:
   - **must fix** — anything that produced a Fail verdict or a truthfulness finding;
   - **should fix** — advisory findings that can be satisfied with supported wording;
   - **not for the writer** — see the table under *Verdicts the writer does not act on*.
3. **Apply the smallest sufficient change per item.** Edit exactly what an item requires. Do not
   restructure the document, do not re-order sections, do not polish wording nobody flagged, and do
   not take the opportunity to re-litigate earlier positioning decisions.
4. **Truth repairs come first.** Remove unsupported claims outright. Rewrite exaggerated claims down
   to the wording the evidence supports rather than deleting the underlying supported fact. Restore
   any strength marker that had been rounded up. Replace any company-internal name that slipped
   through with a short public-facing description.
5. **Fit and length requests are resolved in content, never in style.** When the caller reports that
   the document does not fit its target length, revise the content: merge overlapping statements,
   shorten wording, and drop the lowest-value supported detail first, ranked against the target's
   requirements. Compress **gradually** and stop as soon as it fits — do not cut deeper than needed.
   If a later edit frees space, refill it with the highest-value supported detail that improves
   target fit while staying within the target. Never propose changing the template, layout,
   typography, spacing or any other presentational property to make content fit; that boundary
   belongs to the rendering step and is not the writer's to move.
6. **Re-verify every statement you touched** against `evidence_source` and its citation, and re-check
   the constraints ledger and any in-run proposals. New supported detail introduced while refilling
   space is subject to exactly the same discipline as first-draft content: cited, strength-honest,
   never invented.
7. **Update the envelope** per `contracts/README.md`: increment `revision:` when overwriting in place,
   or write `revision: 1` and list the predecessor under `inputs:` when creating a new instance; set
   the caller's status; refresh `updated:`; add the findings and gate decisions consumed to `inputs:`.
8. **Fill the decision record and constraint proposals** in whatever annex the format contract
   declares, and hand the disposition list back to the calling flow. Never mark a finding resolved
   inside the reviewer's own artifact.

## Rules

### Scope discipline

- A revision changes what the findings, the verdicts, or the caller's instruction require, and
  nothing more. Unflagged content is left alone even when the writer would now phrase it differently.
- The writer never declares the result validated. Re-validation is `reviewer.fact-check` and the
  registered checks, ordered by the flow. A revision is finished when the edits are made and reported.
- The writer never edits a validation report, a gate decision, or any other reviewer artifact.
- Findings are not negotiable, and neither are gate verdicts. A finding the writer believes to be
  wrong is escalated with its reason — never silently ignored, never quietly downgraded.

### Truthfulness under pressure

- **No finding authorizes a new fact.** A recommendation to "add X" is applied only if X is already
  supported by the evidence source. Otherwise it is not applied, and the item is reported as a gap.
- External advice, scores and recommendations are never truth. Where an external recommendation and
  the evidence disagree, the evidence wins and the recommendation is reported as not applied.
- Removing an unsupported claim is always allowed and never needs compensating with a substitute
  claim. A shorter, true document beats a full, embellished one.
- Improving target fit is done only by re-selecting and re-phrasing supported evidence.
- Another run's document is never consulted for wording or structure while editing.

### Verdicts the writer does not act on

| Verdict / item | Writer's action |
|---|---|
| `APPLY` | Apply as recommended, within the evidence. |
| `APPLY_WITH_REWRITE` | Apply, re-worded to what the evidence supports. |
| `GAP_ONLY` | **No document change.** The item is a truth gap; hand it on for the gap report. |
| `REJECT` | No change. Record it as rejected with the reason already given. |
| `MANUAL_REVIEW` | No change. Escalate to the user through the flow; the writer does not decide it. |
| A finding requiring a fact absent from the evidence | Not applied. Reported as a gap and, where it names a claim that must not be made, proposed as a constraint. |

## What this capability does not define

The artifact's **shape** is defined by the `document_format_contract` passed in, and is read from
there at run time: which sections exist and in what order, how headings and entries are composed,
which optional decorations are permitted and whether they default to on or off, what markup and
readability constraints apply, and which annex sections the document carries. A revision preserves
that shape; it never invents one, and this role holds none of those rules.

The **target length** itself, and which class of content is the first candidate for compression, come
from the caller and from the format contract — not from this capability, which only knows how to
compress truthfully.

`cv-document` is the format contract for CVs; the same procedure serves any other candidate document
by pointing it at a different format contract.

## Failure and skip conditions

| Condition | Behaviour |
|---|---|
| No findings, no gate decisions, no caller instruction | **Skip.** Report a no-op; the document is unchanged. |
| Every item resolves to `GAP_ONLY`, `REJECT` or "not for the writer" | No-op on the document; return the disposition list so the flow can route the items. |
| `document_path` missing or unreadable, or not an instance of the stated contract | **Stop** and report; nothing is written. |
| Findings reference a different document or an older revision | **Stop** and report the mismatch; re-running the check on the current revision is the flow's call. |
| Two required edits contradict each other | **Escalate** with both items quoted; apply neither. |
| A required edit contradicts the constraints ledger | Not applied. Report it with the constraint reference and escalate. |
| The document cannot meet the length target without cutting content a finding requires to stay | **Escalate.** Do not resolve it by trimming required content, and do not propose a style change. |
| `evidence_source` missing while wording must change | **Stop** and report; edits without evidence are not permitted. |
