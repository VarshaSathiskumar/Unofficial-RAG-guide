"""
chunk.py - Split cleaned documents into chunks by heading, then by size.

Strategy:
  1. Split on headings/sections (lines that look like a title).
  2. If a section exceeds MAX_SECTION_SIZE, further split with overlap.
"""

import os
import re

CLEANED_DIR      = "cleaned_text"
MAX_SECTION_SIZE = 1500
OVERLAP          = 150

# A heading: short line (under 80 chars), title-cased or ALL CAPS, no sentence-ending punctuation
HEADING_RE = re.compile(r"^(?=[A-Z0-9])(?!.{80,})(?!.*[.?!]$).+$", re.MULTILINE)


def parse_source(text: str) -> tuple:
    """Return (source_label, body) by splitting off the SOURCE header."""
    lines = text.split("\n")
    source, body_start = "", 0
    for i, line in enumerate(lines):
        if line.startswith("SOURCE:"):
            source = line[len("SOURCE:"):].strip()
        if line.startswith("=" * 10):
            body_start = i + 1
    return source, "\n".join(lines[body_start:]).strip()


def split_by_headings(text: str) -> list:
    """Split text into sections at heading boundaries."""
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        return [text]

    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end   = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section = text[start:end].strip()
        if section:
            sections.append(section)

    # Include any text before the first heading
    preamble = text[:matches[0].start()].strip()
    if preamble:
        sections.insert(0, preamble)

    return sections


def split_with_overlap(text: str, max_size: int, overlap: int) -> list:
    """Further split a long section into overlapping character chunks."""
    chunks, start = [], 0
    while start < len(text):
        end = start + max_size
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def build_chunks() -> list:
    """Read all cleaned files and return a flat list of chunk dicts."""
    all_chunks = []
    files = sorted(f for f in os.listdir(CLEANED_DIR) if f.endswith(".txt"))

    for fname in files:
        with open(os.path.join(CLEANED_DIR, fname), encoding="utf-8") as f:
            source, body = parse_source(f.read())

        sections = split_by_headings(body)
        file_chunks = []
        for section in sections:
            if len(section) > MAX_SECTION_SIZE:
                file_chunks.extend(split_with_overlap(section, MAX_SECTION_SIZE, OVERLAP))
            else:
                file_chunks.append(section)

        slug = fname[:-4]
        for i, chunk in enumerate(file_chunks):
            if chunk:
                all_chunks.append({
                    "id":     f"{slug}_{i}",
                    "source": source,
                    "chunk":  chunk,
                })

        print(f"  {fname:<55} {len(sections):>4} sections -> {len(file_chunks):>4} chunks")

    print(f"\nTotal chunks: {len(all_chunks)}")
    print("\n--- 5 representative chunks ---")
    step = len(all_chunks) // 5
    for chunk in [all_chunks[i * step] for i in range(5)]:
        print(f"\n[{chunk['id']}] source: {chunk['source']}")
        print(chunk['chunk'][:300])

    return all_chunks


def main():
    print("=" * 60)
    print(f"CHUNKING  |  heading-based, max={MAX_SECTION_SIZE}, overlap={OVERLAP}")
    print("=" * 60)
    build_chunks()


if __name__ == "__main__":
    main()
