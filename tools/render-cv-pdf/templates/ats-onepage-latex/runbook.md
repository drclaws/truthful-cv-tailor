# Template runbook: ats-onepage-latex

The **toolchain half** of this bundle: which engine builds it, the exact commands, and what to do
when one of them fails. The order in which these commands sit inside the render operation — and what
each gate means — is in `../../TOOL.md`; this file only says how to invoke them for *this* template.

Placeholders: `<source>` is the filled `.tex` the renderer wrote, `<export>` the exported PDF,
`<build-dir>` the directory that may hold build byproducts. All of them are passed in by the caller;
this file never assumes a repository layout.

## Engine

**`pdflatex` (pdfTeX) — required, and not interchangeable.** The template uses pdfTeX primitives
directly: `\pdfgentounicode=1` for Unicode-mapped text extraction and `\pdfliteral direct` for the
`ActualText` spans that give icons readable extraction labels. XeTeX and LuaTeX spell those
differently and the template will not compile unchanged on them. If only another engine is
available, that is an unbound dependency: report it as such rather than porting the template.

LaTeX packages the template loads, all of them part of a full TeX Live / MacTeX / MiKTeX
installation: `geometry`, `fontenc`, `inputenc`, `lmodern`, `babel`, `microtype`, `xcolor`,
`enumitem`, **`paracol`**, `needspace`, `etoolbox`, **`fontawesome5`**, `hyperref`. A minimal TeX
installation typically lacks `paracol` and `fontawesome5`; install them through the distribution's
package manager before the first render.

Text extraction and PDF inspection use a Poppler-compatible toolchain: `pdftotext`, `pdffonts`,
`pdfinfo`. Xpdf builds of the same commands work equally well.

## Build

Compile **twice** from the directory holding the source, so that `paracol` balancing, `\Needspace`
breaks and the PDF metadata settle:

```bash
pdflatex -interaction=nonstopmode <source>
pdflatex -interaction=nonstopmode <source>
```

`-interaction=nonstopmode` keeps the run from stopping at a prompt; it does **not** make errors
acceptable. Read the log: the second run must end with no error, and its overfull/underfull warnings
are the earliest signal that content is fighting the page.

Byproducts (`.aux`, `.log`, `.out`, `.pdf` next to the source) belong in `<build-dir>`. Point the
engine at it, or move them afterwards — they are never part of the deliverable:

```bash
pdflatex -interaction=nonstopmode -output-directory <build-dir> <source>
```

Then place the export at the path and filename the caller passed:

```bash
cp <build-dir>/<source-basename>.pdf <export>
```

## Gate commands

```bash
pdftotext <export> - | head -n 80          # reading order
pdftotext -layout <export> - | head -n 80  # layout-preserving
pdffonts <export>                          # every font must be embedded
pdfinfo <export>                           # page count, title/author metadata
```

Read both extracts, not one: the reading-order extract shows what an ATS parser gets, the
layout-preserving extract shows whether the two columns stayed apart. The column gate in `policy.md`
lists what must survive in both.

`pdffonts` must show `emb` = `yes` for every font in the table (`uni yes` confirms the Unicode
mapping `\pdfgentounicode=1` produces). `pdfinfo` reports `Pages:` — the page target check reads it.

The bundled script `../../scripts/pdf_text_check.py` runs the two extractions and reports the
required headings and contact signals in one pass; see the skill's runbook for its arguments and
exit codes. It complements these commands, it does not replace reading the extracts.

## Troubleshooting

| Symptom | Cause and remedy |
|---|---|
| `! LaTeX Error: File 'paracol.sty' not found` (or `fontawesome5.sty`) | Incomplete TeX installation. Install the package through the distribution's package manager; do not remove the package from the preamble. |
| `! Undefined control sequence. \pdfgentounicode` or `\pdfliteral` | The build is not running on pdfTeX. Use `pdflatex`; see *Engine*. |
| `! Missing $ inserted`, `! Illegal parameter number`, unexpected `%` swallowing a line | Unescaped text in a zone. Apply the escaping table in `policy.md` — `%`, `&`, `_`, `#`, `$`, `{`, `}`, `\`. |
| Content spills onto a second page | A content problem, never a style problem. Do not touch geometry, font size or spacing: report the overflow per the content-first fit policy in `../../TOOL.md`. |
| One column runs long while the other ends early | `paracol` does not balance for you. Rebalance by *placing* sections per `policy.md`, not by restyling; if the supported content genuinely does not fit the composition, report it. |
| `pdffonts` shows `emb no` | A font is referenced but not embedded — usually a locally substituted font. Rebuild with the standard `lmodern` setup the preamble declares, then re-check. |
| Extraction shows interleaved columns or drops signal-column text | The column gate failed. Report it with both extracts as evidence, and state the recommended remedy from `policy.md` (simplify the layout / single-column fallback) for the caller to decide. |
| The alias appears twice in a link, or a link points at `https://linkedin.com/in/https://…` | A full URL was stored in an alias field. Alias or handle only — see `policy.md`. |
| A `TODO:` string survives in the export text | A metadata field or a sample block was left unfilled. Fill it from the document or delete the block; never export with it. |

## When the toolchain is unavailable

If `pdflatex` is missing, write the filled source anyway and report the render as SKIPPED with these
commands as the manual instructions — the source is the part that carries the work. If only the
Poppler tools are missing, the export still happens; the gates that need them are reported as not
run, and `pdfinfo`-free page counting has no substitute — say so rather than assuming the target was
met.
