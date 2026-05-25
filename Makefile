JOB ?= example-company-role
OUT = outputs/$(JOB)
JOBDIR = data/jobs/$(JOB)
PYTHON ?= python3
AI_CMD ?= agent
EXPORT_BASENAME ?= FirstNameSurname
EXPORT_PDF = $(OUT)/exports/$(EXPORT_BASENAME).pdf
EXPORT_DOCX = $(OUT)/exports/$(EXPORT_BASENAME).docx

.PHONY: new-job source-check ats keyword pdf-check export external-prepare external-enhancv external-normalize external-gate pipeline

new-job:
	$(PYTHON) scripts/create_job.py $(JOB)

source-check:
	$(PYTHON) scripts/source_freshness_check.py $(foreach src,$(SOURCES),--source $(src))

ats:
	mkdir -p $(OUT)
	$(PYTHON) scripts/ats_static_check.py $(OUT)/08_final_cv.md > $(OUT)/06_ats_static_check.md

keyword:
	mkdir -p $(OUT)
	$(PYTHON) scripts/keyword_match.py $(JOBDIR)/job_description.md $(OUT)/08_final_cv.md > $(OUT)/keyword_match.md

pdf-check:
	$(PYTHON) scripts/pdf_text_check.py $(EXPORT_PDF) > $(OUT)/pdf_text_check.md

export:
	mkdir -p $(OUT)/exports
	pandoc $(OUT)/08_final_cv.md -o $(EXPORT_DOCX)
	@echo "For PDF, prefer LaTeX render: outputs/$(JOB)/render/final_cv.tex -> $(EXPORT_PDF)"

external-prepare:
	mkdir -p $(OUT)/external_validators
	@echo "Upload $(EXPORT_DOCX) or $(EXPORT_PDF) to external validators."
	@echo "Save Resumly raw report to $(OUT)/external_validators/resumly_raw.md"
	@echo "Run Enhancv with: make external-enhancv JOB=$(JOB)"

external-enhancv: pdf-check
	$(PYTHON) scripts/run_enhancv_validator.py --job $(JOB) --pdf $(EXPORT_PDF)

external-normalize:
	$(AI_CMD) "Normalize $(OUT)/external_validators/resumly_raw.md using prompts/external_report_normalizer.md. Save normalized report to $(OUT)/external_validators/resumly_report.md."
	$(AI_CMD) "Normalize $(OUT)/external_validators/enhancv_raw.md using prompts/external_report_normalizer.md. Save normalized report to $(OUT)/external_validators/enhancv_report.md."

external-gate:
	$(AI_CMD) "Run prompts/external_validation_gate.md using available reports in $(OUT)/external_validators, $(OUT)/08_final_cv.md, canonical candidate inputs, derived evidence indexes, constraints, and job inputs. Save consolidated report to $(OUT)/external_validators/consolidated_external_validation.md."

pipeline:
	$(AI_CMD) "Run the full CV tailoring pipeline for $(JOBDIR). Follow AGENTS.md and prompts/00_full_pipeline.md."
