# External Validation Gate

Inputs:
- Final CV
- Canonical candidate inputs and `00_source_audit.md`, when used
- Experience bank
- Skills matrix
- Projects
- Constraints
- Job description
- Internal ATS validation
- Position match report
- External validator reports

Evaluate external validator recommendations and decide which changes are allowed.

Decision labels:
- APPLY: safe and supported
- APPLY_WITH_REWRITE: useful but must be rewritten truthfully
- GAP_ONLY: important but unsupported; add to gap report, not CV
- REJECT: irrelevant, unsafe, misleading, or harmful
- MANUAL_REVIEW: requires user decision

Rules:
- Fact validation overrides external validator suggestions.
- Treat external validators as the last advisory gate after local fact, ATS,
  position match, render sanity, and PDF extraction checks.
- Do not add unsupported skills.
- Do not add unsupported tools.
- Do not add unsupported metrics.
- Do not add unsupported domain experience.
- Do not add unsupported leadership or ownership claims.
- Keyword suggestions are allowed only if the underlying experience is supported.
- Formatting suggestions are usually safe unless they reduce readability.
- Do not accept formatting or fit suggestions that require changing template
  style, geometry, margins, font sizes, spacing, colors, column widths, section
  styling, or visual components merely to make content fit.
- For one-page fit recommendations, apply the existing content rule: optimize
  Experience moderately first, preserve useful supported evidence, and reuse any
  newly available space for the strongest target-relevant Experience detail.
- Persistent conservative constraints may be added to `constraints.md` without
  direct user approval when they document unsupported claims, wording risks,
  recurring external-validator traps, or source conflicts.

Output:

# External Validation Gate Report

## Accepted changes

## Changes requiring truthful rewrite

## Gaps to document but not add to CV

## Rejected suggestions

## Manual review items

## Final recommendation
Proceed / Revise / Do not send yet
