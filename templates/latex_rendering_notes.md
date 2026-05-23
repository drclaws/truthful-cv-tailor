# LaTeX Rendering Notes

The LaTeX template is a renderer, not a source of truth.

Workflow:

1. Validate content in Markdown.
2. Render validated content into `templates/cv-ats-agent-template.tex`.
3. Write rendered file to `outputs/<job>/render/final_cv.tex`.
4. Compile twice with `pdflatex`.
5. Save final delivery files in `exports/` with `FirstNameSurname\..*`
   filenames, for example `JaneDoe.pdf`.
6. Check normal and layout-oriented text extraction with `pdftotext`.
7. Check fonts with `pdffonts`.
8. Re-run validation if content changed.

Useful commands:

```bash
pdflatex -interaction=nonstopmode final_cv.tex
pdflatex -interaction=nonstopmode final_cv.tex
pdftotext final_cv.pdf - | head -n 40
pdftotext -layout final_cv.pdf - | head -n 40
pdffonts final_cv.pdf
pdfinfo final_cv.pdf
```

For a columnar PDF, inspect both text extracts. Standard headings, contact
details, role titles, dates, and bullets must survive without incoherent
cross-column interleaving.
