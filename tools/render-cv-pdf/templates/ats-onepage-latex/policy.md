# Template policy: ats-onepage-latex

Template version: 1.0

The **fill rules of this template bundle**: which agent-content zones exist, what each accepts, how
text must be escaped, where each section of the document belongs in this template's two-column
layout, and what this template's fixed style means for a render that does not fit.

Scope, so that nothing is stated twice:

- **This file governs the HOW** — the mechanics of filling *this* template.
- **The operation rules** — the page target, the content-first fit policy, the gate sequence, export
  naming, template resolution — live in the owning skill, `../../TOOL.md`.
- **The document-level rules** — which sections a CV has, in which order, how the header title is
  chosen, what may be claimed at all — belong to the `cv-document` contract. This file never restates
  them and never competes with them: if a rule here seems to contradict the document contract, stop
  and ask; do not choose.
- **The invariants of the actor** filling the template are the renderer's — role `renderer`,
  capability `renderer.render-document`. Content is transcribed, never authored.

## What this template is

A compact, ATS-gated one-page composition:

- a full-width contact header with visual icons and visible text labels;
- a **main narrative column** (`paracol`, 60% width) for Experience, Projects, Education;
- a **signal column** for Summary, Skills, Languages and other short supported signals.

The template is a renderer, not a source of truth. Candidate facts come from the validated document
the caller passed, never from the template's sample text.

## Agent content zones

Editing is confined to the three delimited zones below. Everything outside them — preamble,
geometry, colours, helper macro definitions, the `paracol` environment itself, the trailing checklist
— is off limits.

| Zone | Delimiters | Accepts |
|---|---|---|
| Candidate Metadata | `% BEGIN AGENT CONTENT: Candidate Metadata` … `% END AGENT CONTENT: Candidate Metadata` | identity, contact, optional profile aliases, the target-role line, PDF keywords, and the three visibility switches |
| Main Column | `% BEGIN AGENT CONTENT: Main Column` … `% END AGENT CONTENT: Main Column` | the narrative sections |
| Signal Column | `% BEGIN AGENT CONTENT: Signal Column` … `% END AGENT CONTENT: Signal Column` | the short scan sections |

The `% BEGIN`/`% END` comment lines themselves stay in the file, unchanged.

If supported content has no zone that can carry it, stop and ask the caller. Never invent a zone,
never move a macro definition, and never add a package.

## Candidate Metadata zone

Fill every field from the validated document and the values the caller passed — never from the
agent's own knowledge of the candidate. Every `TODO:` placeholder must be gone from the rendered
source.

| Macro | Filled with |
|---|---|
| `\PersonName` | the candidate's full name as the document states it |
| `\PersonRole` | the document's validated CV header title. Never replaced with the vacancy title at render time when the writer or a validation report chose a safer market-facing title |
| `\HeaderTags` | empty by default — see *Header focus tags* below |
| `\ContactLocation`, `\ContactEmail`, `\ContactPhone` | the visible contact values |
| `\ContactPhoneTel` | the same number in link form, E.164 preferred; it feeds `tel:` only |
| `\ContactLinkedInAlias`, `\ContactGitHubAlias` | the **bare alias or handle only** |
| `\PdfKeywords` | the target role, primary stack and relevant skills the document supports |

**Profile links are aliases only.** `\ContactLinkedInAlias` and `\ContactGitHubAlias` hold the bare
alias or handle — never `https://`, never `linkedin.com/in/`, never `github.com/`, never a path
segment. The template builds both the visible form and the clickable URL from the alias
(`\ContactLinkedInUrl`, `\ContactGitHubUrl`), so a URL stored in an alias field renders doubled and
extracts wrong.

**Visibility switches.** All three are false in the shipped template:

- `\ShowLinkedIntrue` / `\ShowGitHubtrue` — set only after filling the corresponding alias with a
  supported profile. An unsupported optional link stays empty **and** disabled; it is never rendered
  empty.
- `\ShowHeaderTagsfalse` — see below.

## Header focus tags

The rendering half of the rule; the document-level decision belongs to the `cv-document` contract.

- The switch is `\ShowHeaderTagsfalse` and `\HeaderTags` is empty — **that is the default and it
  stays that way** unless the document, or a validation report accompanying it, explicitly enables a
  small evidence-backed set for this application. Turning tags on by choice would be authoring.
- When they are explicitly enabled, `\HeaderTags` holds a short list of `\headertag{...}` calls, one
  supported focus area each, and `\ShowHeaderTagstrue` is set in the metadata zone.
- Each tag renders as ordinary visible PDF text; a tag is never a way to smuggle a keyword the body
  does not support.
- Tags never replace the Skills section. If a tag names a capability, that capability must also
  appear in Skills, Summary or Experience with supported wording.

## Section placement

The document is linear; this template's *visual* surface is not. Placement, keeping each section's
standard heading exactly as the document states it:

- **Main column** — Experience, Projects (when the document has them), Education: everything
  narrative, everything with bullets.
- **Signal column** — Summary, Skills, Languages, and other short supported signals such as
  Certifications: everything a recruiter scans rather than reads.

Section headings are produced with `\cvsection{...}` in either column. Keep density high without
shrinking text into illegibility — and note that "shrinking text" is a style change and therefore
forbidden anyway (see *Fixed style*).

### Main column macros

| Macro | Use |
|---|---|
| `\job{Company}{Location}{Role}{Dates}` | a full Experience entry |
| `\briefjob{Company}{Location}{Role}{Dates}` | a compact earlier Experience entry |
| `\stack{...}` | the technologies of that role, when the document supports them |
| `\begin{itemize} \item ... \end{itemize}` | the entry's bullets |
| `\cvitemdivider` | **between** repeated narrative items only — never after the last item of a section |
| `\education{Degree}{Institution}{Location}{Dates}` | an Education entry |
| `\project{Name}{host/path}{Role and stack}` | a Project entry; the second argument is a bare host and path, the template adds the scheme |

Dates are rendered in the readable form the document uses, e.g. `Jan 2021 -- Present`,
`Mar 2018 -- Dec 2020`. Locations follow the document's granularity (city and country).

### Signal column macros

| Macro | Use |
|---|---|
| `\cvlanguage{Language}{Level}` | one language line |
| `\skillgroup{Group name}{chips}` | one labelled skill group |
| `\skillchip{Label}` | one skill chip inside a group |

The Summary is plain paragraph text under its `\cvsection{Summary}` heading.

### Skill chips

- **Prefer short chips over long comma-separated skill paragraphs** when the content allows it: they
  are what makes this template's signal column readable, and each chip is ordinary PDF text.
- Chips are **not limited to programming languages and tools**. When the document supports it, chips
  may carry systems and problem domains, reliability and delivery practices, collaboration or working
  modes, and language skills — anything job-relevant and evidence-backed that the document already
  states.
- Keep chip labels short enough to wrap compactly; a chip that wraps mid-label defeats its purpose.
- Chips may carry the template's light rule and fill, and nothing more: no charts, no rating dots, no
  skill bars, no progress meters.

## Escaping

Every piece of generated text that reaches a zone is escaped before it is written. An unescaped
character is a defect even when the compile happens to survive it.

| Character | Written as |
|---|---|
| `\` | `\textbackslash{}` |
| `%` | `\%` |
| `&` | `\&` |
| `_` | `\_` |
| `#` | `\#` |
| `$` | `\$` |
| `{` | `\{` |
| `}` | `\}` |

Escaping applies inside macro arguments too — a company name with an `&`, a metric with a `%`, a
technology with an `_` are the usual offenders.

## Alternate-text labels

The template maps decorative icon glyphs to readable extraction labels through PDF `ActualText`
(`\withactualtext`, used by `\cvicon`, `\cvmetaicon`, `\cvmetadata`, `\contactitem`, `\contactlink`,
`\profilelink`). Text extraction therefore reads labels such as `Phone: `, `Email: `, `Dates: `,
`Location: ` where the visual PDF shows only the icon.

The hard boundary: **`ActualText` may LABEL a value, never CARRY one.** The phone number, the email
address, the dates, the locations, the skills and the bullets are ordinary visible text in the
document body. The one exception the template makes by design is `\profilelink`, whose `ActualText`
exposes the generated full URL while the page visibly shows the alias — the alias itself is still
visible text.

Never use invisible text or `ActualText` to add anything the visible page does not say.

## ATS rendering rules

The render form of the ATS contract; the document-level form belongs to the `cv-document` contract.

- Use the standard section names the document uses; do not rename a heading at render time.
- **No tables** for CV content, **no images**, **no scanned text**, **no skill bars or rating dots**,
  no hidden duplicate text to compensate for a risky layout.
- Icons are allowed for visual contact mapping, but **every icon has visible text beside it or
  immediately after it**. No icon-only facts.
- No critical fact is encoded only through colour, icon, alignment, shape, or a header/footer.
- Columns are allowed in the exported PDF **only while the column gate below passes**.
- URLs stay visible text wherever the link matters.
- **Empty optional sections are removed**, not rendered empty.
- No `TODO`, no `PLACEHOLDER`, no template sample text, no unsupported claim survives into the
  rendered source or the export.

## Fixed style

**The style of this template is fixed.** Do not change geometry, margins, font sizes, spacing,
colours, column widths, `\columnratio`, `\linespread`, section styling, or any visual component —
least of all to make a CV fit.

When validated content overflows the page target, the fit problem is a **content** problem and it
goes back to the caller. The tactics for resolving it, and the rule that the tool reports rather than
cuts, live in `../../TOOL.md` (*Content-first fit policy*). Nothing in this file authorises a style
change, and no template fallback is selected to squeeze content onto the page.

## Column gate

A two-column PDF is only acceptable while its text still extracts coherently. After the export is
produced, and before it is handed over:

1. Confirm the source compiled cleanly and the export's text fonts are embedded.
2. Extract the text **twice** — plain reading order and layout-preserving mode.
3. Confirm that the name, the contact text, the standard headings, the role titles, the dates, the
   bullets, the skill chips, education and languages are all still present in both extracts.
4. Inspect for **incoherent cross-column interleaving** and for **lost signal-column text** — the
   two failure modes this composition can produce.
5. Any render-content change afterwards re-opens the checks that the change could invalidate: the
   truthfulness check and the registered internal checks run again.

The concrete commands are in `runbook.md`; the gate's place in the overall sequence is in
`../../TOOL.md`.

**When the gate fails**, it is a red gate: report it, with the evidence, and hand back to the caller
— exactly as `renderer.render-document` requires. The remedy this template recommends, and which the
report should state, is to **simplify the rendered layout before export — a single-column fallback
render is preferable to a visually strong PDF that extracts badly**. That simplification changes the
visual composition, so it is the caller's decision to take, not one the renderer makes on its own.
