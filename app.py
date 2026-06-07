"""
app.py - Run the full ingestion pipeline: ingest -> chunk -> embed -> retrieve.
"""

import ingest
from chunk import build_chunks
from embed import store
from retrieve import retrieve


def main():
    print("\n>>> STEP 1: Ingest and clean documents")
    ingest.main()

    print("\n>>> STEP 2: Chunk cleaned text")
    chunks = build_chunks()
    print(f"Total chunks: {len(chunks)}")

    print("\n>>> STEP 3: Embed and store in ChromaDB")
    store(chunks)

    print("\n>>> STEP 4: Test retrieval")
    query = "What happens if a student receives an incomplete grade?"
    print(f"Query: {query}\n")
    for r in retrieve(query):
        print(f"  [{r['score']}] {r['source']}")
        print(f"  {r['chunk'][:200]}\n")

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
