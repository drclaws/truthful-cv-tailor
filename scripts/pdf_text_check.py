#!/usr/bin/env python3
import re
import shutil
import subprocess
import sys
from pathlib import Path

REQUIRED_HEADINGS = ["summary", "skills", "experience", "education"]
REQUIRED_CONTACT_SIGNALS = {
    "email": r"\bemail\s*:\s*[\w.+-]+@[\w.-]+\.\w+",
    "phone": r"\bphone\s*:\s*(\+\d{1,3}[\s-]?)?[\(\d][\d\s\-\(\)]{7,}",
}
OPTIONAL_CONTACT_SIGNALS = {
    "linkedin": r"linkedin\.com",
}
PDFTOTEXT_CANDIDATES = [
    "pdftotext",
    "/opt/homebrew/bin/pdftotext",
    "/usr/local/bin/pdftotext",
    "/opt/homebrew/var/homebrew/tmp/.cellar/poppler/26.04.0/bin/pdftotext",
]


def find_pdftotext():
    for candidate in PDFTOTEXT_CANDIDATES:
        if "/" in candidate:
            path = Path(candidate)
            if path.exists() and path.is_file():
                return str(path)
        else:
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
    return None


def run(cmd):
    try:
        completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
        return completed.returncode, completed.stdout
    except FileNotFoundError:
        return 127, ""


def missing_signals(text):
    lower = text.lower()
    missing_headings = [heading for heading in REQUIRED_HEADINGS if heading not in lower]
    missing_contacts = [
        name for name, pattern in REQUIRED_CONTACT_SIGNALS.items()
        if not re.search(pattern, text, re.IGNORECASE)
    ]
    return missing_headings, missing_contacts


def print_result(label, text):
    missing_headings, missing_contacts = missing_signals(text)
    print(f"\n## {label}")
    print(f"Extracted characters: {len(text)}")
    print("\n### Required headings")
    for heading in REQUIRED_HEADINGS:
        print(f"- {heading.title()}: {'no' if heading in missing_headings else 'yes'}")
    print("\n### Required contact signals")
    for name, pattern in REQUIRED_CONTACT_SIGNALS.items():
        print(f"- {name}: {'no' if name in missing_contacts else 'yes'}")
    print("\n### Optional contact signals")
    for name, pattern in OPTIONAL_CONTACT_SIGNALS.items():
        print(f"- {name}: {'yes' if re.search(pattern, text, re.IGNORECASE) else 'no'}")
    print("\n### First 1000 characters")
    print("```text")
    print(text[:1000])
    print("```")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/pdf_text_check.py <FirstNameSurname.pdf>")
        sys.exit(1)
    pdf = Path(sys.argv[1])
    pdftotext = find_pdftotext()
    print("# PDF Text Extraction Check\n")
    if not pdftotext:
        print("FAIL: pdftotext is not available. Install Poppler/Xpdf-compatible tooling.")
        sys.exit(2)
    print(f"pdftotext: `{pdftotext}`")
    normal_code, normal_text = run([pdftotext, str(pdf), "-"])
    layout_code, layout_text = run([pdftotext, "-layout", str(pdf), "-"])
    if normal_code == 127 or layout_code == 127:
        print("FAIL: pdftotext could not be executed.")
        sys.exit(2)
    if not normal_text.strip() or not layout_text.strip():
        print("FAIL: pdftotext returned empty text. Is the PDF scanned or malformed?")
        sys.exit(2)
    print("Inspect both extracts for cross-column interleaving before export.")
    print_result("Normal extraction", normal_text)
    print_result("Layout extraction", layout_text)
    checks = {
        "normal": missing_signals(normal_text),
        "layout": missing_signals(layout_text),
    }
    failed = {
        label: result for label, result in checks.items()
        if result[0] or result[1]
    }
    if failed:
        print("\nFAIL: required extraction signals are missing.")
        sys.exit(3)

if __name__ == "__main__":
    main()
