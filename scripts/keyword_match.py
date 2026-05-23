#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from collections import Counter

STOPWORDS = {
    "and", "or", "the", "a", "an", "to", "of", "in", "for", "with", "on", "by",
    "is", "are", "be", "as", "at", "from", "this", "that", "you", "we", "our", "your",
    "will", "can", "have", "has", "their", "they", "them", "it", "into", "using"
}

def words(text):
    return [
        w.lower()
        for w in re.findall(r"[A-Za-z][A-Za-z0-9\+\#\.\-]{1,}", text)
        if w.lower() not in STOPWORDS
    ]

def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/keyword_match.py <job.md> <cv.md>")
        sys.exit(1)
    job = Path(sys.argv[1]).read_text(encoding="utf-8")
    cv = Path(sys.argv[2]).read_text(encoding="utf-8")
    job_words = Counter(words(job))
    cv_words = set(words(cv))
    important = [w for w, c in job_words.most_common(100) if len(w) > 2]
    covered = [w for w in important if w in cv_words]
    missing = [w for w in important if w not in cv_words]
    score = round(len(covered) / max(len(important), 1) * 100)
    print("# Keyword Match Report\n")
    print(f"Keyword coverage: {score}%\n")
    print("## Covered")
    for w in covered[:60]: print(f"- {w}")
    print("\n## Missing")
    for w in missing[:60]: print(f"- {w}")

if __name__ == "__main__":
    main()
