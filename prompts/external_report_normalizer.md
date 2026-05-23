# External Report Normalizer

Input:
- Raw report from an external resume/ATS validator
- Job description
- Final CV

Normalize the report into this structure:

# External Validator Report

## Validator
Name:

## Input files
- Resume:
- Job description:

## Scores
- ATS score:
- Match score:
- Readability score:
- Other scores:

## Critical issues
Issues that may block ATS parsing or recruiter readability.

## Keyword gaps
Keywords or skills the validator says are missing.

## Formatting issues
Issues related to layout, sections, file type, bullets, dates, tables, columns, icons, or parsing.

## Content suggestions
Suggestions to improve summary, bullets, skills, or positioning.

## Potentially unsafe suggestions
Suggestions that would require adding facts, tools, metrics, certifications, domain experience, or seniority claims not present in the current CV.

## Recommended next actions
List actions, but mark each as:
- Safe formatting edit
- Needs fact validation
- Gap only
- Reject
