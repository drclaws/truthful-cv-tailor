# CV Template Policy

## Default template

Use `templates/cv-ats-agent-template.tex` for production CV PDFs.

The template is a renderer. Candidate facts come from validated master and job
artifacts, not from the template.

## Design direction

Use a compact recruiter-first layout based on a main content column and a
supporting signal column.

- Keep the old visual language: restrained blue palette, crisp rules, strong
  role headings, and a contact block with visual icons.
- Header focus tags are disabled by default. They may be enabled only as a small
  validated exception for supported themes that add clear scan value beyond the
  role title, Summary, Skills, and Experience. They are not a substitute for a
  clear role title, Summary, Skills, or experience evidence.
- Put experience, projects when useful, and education in the main column.
- Put summary, grouped skills, languages, and other short supported signals in
  the side column.
- Keep density high without shrinking text into illegibility.
- Prefer extracted text skill chips for compact skills. Do not replace text with
  charts, rating dots, or skill bars.
- Skills should not be limited to programming languages and tools. When
  evidence supports it, include concise grouped skills for systems/problem
  domains, reliability and delivery practices, collaboration or working modes,
  and languages.
- Header focus tags are not a replacement for Skills. If a tag names a key
  skill or capability, that capability must also appear in Skills, Summary, or
  Experience with supported wording.
- Do not show key skills in the header by default; keep them in the Skills
  section unless validation recommends a small nonredundant header tag set.

## Fit policy

The template style is fixed. Do not change geometry, margins, font sizes,
spacing, colors, column widths, section styling, or visual components merely to
make a CV fit.

When the target is a one-page CV and validated content overflows, solve the fit
problem by editing content, especially Experience content:

- merge overlapping bullets;
- remove lower-value or less job-relevant details;
- shorten wording while preserving concrete scope, impact, tools, and seniority;
- keep the strongest supported evidence for the target role.

Compress gradually. The goal is a complete, recruiter-readable one-page CV, not
the shortest possible CV. If later edits create unused space, reuse it for the
highest-value supported Experience information that improves target fit, as long
as the CV still fits and passes validation.

## ATS contract

Human-readable visual structure may be nonlinear. ATS-readable content must
remain text-based and recoverable.

- Use standard section names.
- Do not use tables for final CV content.
- Columns are allowed in the rendered PDF only when extraction checks pass.
- Icons are allowed for visual contact mapping, but every icon must have visible
  text beside it or immediately after it.
- Icon labels may use PDF `ActualText` so text extraction reads labels such as
  `Phone:`, `Email:`, `Dates:`, or `Location:` while the visual PDF shows only
  the icon. This is allowed only for the icon label; the actual contact, date,
  location, or other critical value must still be ordinary visible text.
- Do not encode critical facts only through color, icons, alignment, shapes, or
  headers/footers.
- Do not use images, scanned text, skill bars, rating dots, or hidden duplicate
  text to compensate for a risky layout.
- Skill chips may use light borders and fills only when each chip is ordinary
  visible PDF text and extraction checks preserve the chip text.
- Header focus tags follow the same rule: every tag must be ordinary visible PDF
  text and its meaning must be supported by validated evidence or elsewhere in
  the CV body.
- URLs must remain visible text when links are important.
- Empty optional sections must be removed.
- Unsupported facts and placeholders must not reach final exports.

## Column gate

After rendering a PDF with columns:

1. Run a LaTeX sanity check and confirm text fonts are embedded.
2. Run normal `pdftotext` and `pdftotext -layout`.
3. Confirm name, contact text, standard headings, role titles, dates, bullets,
   skills, education, and languages remain extractable.
4. Inspect for incoherent cross-column interleaving or lost side-column text.
5. Re-run fact and ATS validation after any render-content change.

If the visual PDF fails this gate, simplify the layout before export. A fallback
single-column render is preferable to a visually strong PDF that extracts badly.

## Candidate metadata

The production template must stay candidate-neutral. Fill name, contacts,
optional profile links, target role, and PDF metadata from validated artifacts.
Leave unsupported optional links out.

For optional profile links, agent-filled fields must contain only the profile
alias/handle. Do not store full URLs, URL paths, or schemes in alias fields:
use a bare alias/handle, not `https://linkedin.com/in/<alias>`,
`linkedin.com/in/<alias>`, or `github.com/<handle>`. The template visually
shows only the alias/handle and constructs the clickable URL. It may use PDF
`ActualText` so text extraction returns the generated full URL.

## CV header title

The header title is a short market-facing positioning line for the application.
It should start from a truthful professional identity and supported seniority,
then add only the specialization needed to make the target fit legible.

- Do not copy the vacancy title mechanically.
- Vacancy wording is acceptable only when the title remains truthful and does
  not imply unsupported domain experience, tools, ownership, management scope,
  or seniority.
- The header title may be broader than official Experience titles.
- Experience role titles must stay source-backed and must not be rewritten only
  to match the header.

## Section order

The Markdown CV remains linear:

1. Name and contact information
2. Summary
3. Skills
4. Experience
5. Projects, if useful
6. Education
7. Certifications, if useful
8. Languages, if useful

The rendered PDF may move Summary, Skills, Languages, and other short supported
signals into the side column while retaining their standard section headings.

## Content rules

Experience bullets should follow:

Action + scope/context + impact/result + tools/technologies, where supported.

Use readable dates such as:

Jan 2021 -- Present
Mar 2018 -- Dec 2020

Escape generated LaTeX text:

- `\` as `\textbackslash{}` when needed
- `%` as `\%`
- `&` as `\&`
- `_` as `\_`
- `#` as `\#`
- `$` as `\$`
- `{` and `}` as `\{` and `\}`
