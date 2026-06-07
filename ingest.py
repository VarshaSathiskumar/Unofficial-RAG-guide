"""
ingest.py - Extract text from PDFs and save raw + cleaned versions.
"""

import html
import os
import re
import unicodedata

import pdfplumber

DOCUMENTS_DIR = "documents"
CLEANED_DIR   = "cleaned_text"

DOCUMENTS = [
    ("mines_mission_vision",               "Mines Mission, Vision and Strategic Planning - President's Office.pdf"),
    ("catalog",                            "catalog.pdf"),
    ("cs_graduate_programs",              "cs.pdf"),
    ("academic_regulations",              "generalregulations.pdf"),
    ("graduate_grading_system",           "graduategradingsystem.pdf"),
    ("graduation",                         "graduation.pdf"),
    ("graduation_requirements",           "graduationrequirements.pdf"),
    ("policies_and_procedures",           "policiesandprocedures.pdf"),
    ("registration_tuition",              "registrationandtuitionclassification.pdf"),
    ("robotics_graduate_programs",        "robotics.pdf"),
    ("the_graduate_school",               "thegraduateschool.pdf"),
    ("tuition_fees_financial_assistance", "tuitionfeesfinancialassistance.pdf"),
]


def ingest(filepath: str) -> str:
    """Extract raw text from a PDF file."""
    pages = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    raw = "\n\n".join(pages)
    raw = unicodedata.normalize("NFKC", raw)
    raw = re.sub(r"[ \t]+", " ", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


def clean(slug: str, text: str) -> str:
    """Remove boilerplate: page headers, nav, URLs, HTML entities, bad bullets."""
    # HTML entities and tags
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)

    # Private-use Unicode icon glyphs (from browser-printed PDFs)
    text = re.sub(r"[-]+", "", text)

    # Repeated PDF page-title lines e.g. "Computer Science 1"
    text = re.sub(r"^[A-Z][A-Za-z ,&/]+\s+\d{1,3}\s*$", "", text, flags=re.MULTILINE)

    # Noise specific to mines_mission_vision (printed-to-PDF from browser)
    if slug == "mines_mission_vision":
        text = re.sub(r"^\d{2}/\d{2}/\d{4},\s+\d{2}:\d{2}[^\n]*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"^[^\n]*MINES\.EDU[^\n]*$",                  "", text, flags=re.MULTILINE)
        text = re.sub(r"^[^\n]*Home\s+Meet the President[^\n]*$",   "", text, flags=re.MULTILINE)
        text = re.sub(r"^https?://\S+(\s+\d+/\d+)?\s*$",           "", text, flags=re.MULTILINE)
        text = re.sub(r"\s+Download\s+(Campus Town|the Mines@150)[^\n]*", "", text)
        text = re.sub(r"\s+Hall Fall \d{4}",                        "", text)
        text = re.sub(r"\s+Playbook Presentation",                  "", text)
        text = re.sub(r"RESOURCES\s+VISIT MINES\b.*",               "", text, flags=re.DOTALL)
        text = re.sub(r"©\d{4}\s+Colorado School of Mines[^\n]*",  "", text)
        text = re.sub(r"^Contact\s+Accessibility\s+Emergency[^\n]*$", "", text, flags=re.MULTILINE)

    # Normalize bullets and whitespace
    text = re.sub(r"[·•]", "-", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def save(directory: str, slug: str, source: str, text: str) -> None:
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{slug}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"SOURCE: {source}\n{'=' * 60}\n\n{text}")


def main():
    print(f"{'=' * 60}\nINGESTION — extracting and cleaning PDFs\n{'=' * 60}\n")

    for slug, filename in DOCUMENTS:
        filepath = os.path.join(DOCUMENTS_DIR, filename)
        if not os.path.isfile(filepath):
            print(f"  [SKIP] {filename}")
            continue

        raw  = ingest(filepath)
        cleaned = clean(slug, raw)

        save(CLEANED_DIR, slug, filepath, cleaned)

        print(f"  {filename}  ->  {len(cleaned):,} chars")

    print("\nDone.")


if __name__ == "__main__":
    main()
