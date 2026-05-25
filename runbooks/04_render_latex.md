# Render LaTeX

Ask the agent to render and validate the PDF after `outputs/<job>/render/final_cv.tex`
exists. The agent should compile LaTeX, copy the export to
`outputs/<job>/exports/FirstNameSurname.pdf`, and run `scripts/pdf_text_check.py`
for the job export.

Manual compile reference if needed:

```bash
cd outputs/<job>/render
pdflatex -interaction=nonstopmode final_cv.tex
pdflatex -interaction=nonstopmode final_cv.tex
mkdir -p ../exports
cp final_cv.pdf ../exports/FirstNameSurname.pdf
```

Check:

- PDF has extractable text.
- Standard section names are present.
- Fonts are embedded and Unicode-mapped.
- No TODO/PLACEHOLDER remains.
- Final export filename follows `FirstNameSurname\..*`.
