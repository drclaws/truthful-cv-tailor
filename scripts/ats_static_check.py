#!/usr/bin/env python3
import re
import sys
from pathlib import Path

STANDARD_HEADINGS = [
    "summary",
    "professional summary",
    "skills",
    "core skills",
    "experience",
    "professional experience",
    "projects",
    "selected projects",
    "education",
    "certifications",
    "languages",
]

RISK_PATTERNS = {
    "markdown_table": r"\|.+\|",
    "html_tags": r"<[^>]+>",
    "icons_or_symbols": r"[★●◆■✓➤→]",
    "skill_bars": r"(advanced|expert|beginner)\s*[:\-]\s*(\d+%|[█▇▆▅▄▃▂▁]+)",
    "image_reference": r"!\[.*?\]\(.*?\)",
    "placeholder": r"TODO|PLACEHOLDER|\{\{.+?\}\}",
}

def load_text(path):
    return Path(path).read_text(encoding="utf-8")

def check_headings(text):
    lower = text.lower()
    return [h for h in STANDARD_HEADINGS if h in lower]

def check_risks(text):
    issues = []
    for name, pattern in RISK_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            issues.append(name)
    return issues

def check_contact(text):
    email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    linkedin = "linkedin.com" in text.lower()
    phone = re.search(r"(\+\d{1,3}[\s\-]?)?[\(\d][\d\s\-\(\)]{7,}", text)
    return {"email": bool(email), "phone": bool(phone), "linkedin": linkedin}

def check_bullets(text):
    bullets = [line for line in text.splitlines() if line.strip().startswith(("-", "*"))]
    long_bullets = [b for b in bullets if len(b) > 240]
    return {"bullet_count": len(bullets), "long_bullets": len(long_bullets)}

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/ats_static_check.py <cv.md-or-txt>")
        sys.exit(1)
    text = load_text(sys.argv[1])
    headings = check_headings(text)
    risks = check_risks(text)
    contact = check_contact(text)
    bullets = check_bullets(text)
    score = 100
    if len(headings) < 4: score -= 15
    if risks: score -= 10 * len(risks)
    if not contact["email"]: score -= 20
    if not contact["phone"]: score -= 10
    if bullets["long_bullets"] > 3: score -= 10
    score = max(score, 0)
    print("# Static ATS Check\n")
    print(f"Score: {score}/100\n")
    print("## Headings found")
    for h in headings: print(f"- {h}")
    print("\n## Contact info")
    for k, v in contact.items(): print(f"- {k}: {'yes' if v else 'no'}")
    print("\n## Formatting risks")
    if risks:
        for r in risks: print(f"- {r}")
    else:
        print("- none")
    print("\n## Bullets")
    print(f"- total bullets: {bullets['bullet_count']}")
    print(f"- long bullets: {bullets['long_bullets']}")

if __name__ == "__main__":
    main()
