# Render LaTeX

After Codex creates `outputs/<job>/render/final_cv.tex`, compile:

```bash
cd outputs/<job>/render
pdflatex -interaction=nonstopmode final_cv.tex
pdflatex -interaction=nonstopmode final_cv.tex
mkdir -p ../exports
cp final_cv.pdf ../exports/FirstNameSurname.pdf
cd ../../..
make pdf-check JOB=<job> EXPORT_BASENAME=FirstNameSurname
```

Check:

- PDF has extractable text.
- Standard section names are present.
- Fonts are embedded and Unicode-mapped.
- No TODO/PLACEHOLDER remains.
- Final export filename follows `FirstNameSurname\..*`.
