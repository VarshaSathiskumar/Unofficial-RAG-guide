"""
embed.py - Embed chunks and store them in ChromaDB.

Embedding model: all-MiniLM-L6-v2 (sentence-transformers)
Collection:      mines_rag
"""

import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "mines_rag"
EMBED_MODEL     = "all-MiniLM-L6-v2"
BATCH_SIZE      = 64


def store(chunks: list) -> None:
    print(f"Loading embedding model: {EMBED_MODEL} ...")
    model = SentenceTransformer(EMBED_MODEL)

    print("Connecting to ChromaDB ...")
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_or_create_collection(COLLECTION_NAME)
    if collection.count() > 0:
        print(f"  Collection '{COLLECTION_NAME}' already has {collection.count()} entries — skipping embed.")
        return

    print(f"Embedding and storing {len(chunks)} chunks ...")
    for start in range(0, len(chunks), BATCH_SIZE):
        batch     = chunks[start : start + BATCH_SIZE]
        texts     = [c["chunk"]  for c in batch]
        ids       = [c["id"]     for c in batch]
        metadatas = [{"source": c["source"]} for c in batch]

        collection.add(
            ids        = ids,
            documents  = texts,
            embeddings = model.encode(texts, show_progress_bar=False).tolist(),
            metadatas  = metadatas,
        )
        print(f"  stored {start + 1}-{start + len(batch)}")

    print(f"\nDone. Collection '{COLLECTION_NAME}' has {collection.count()} entries.")


def main():
    from chunk import build_chunks
    store(build_chunks())


if __name__ == "__main__":
    main()
