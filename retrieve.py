"""
retrieve.py - Retrieve the top-k most relevant chunks for a query.
"""

import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "mines_rag"
EMBED_MODEL     = "all-MiniLM-L6-v2"
TOP_K           = 5

_model      = None
_collection = None


def _load():
    global _model, _collection
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    if _collection is None:
        client = chromadb.PersistentClient(path="chroma_db")
        _collection = client.get_collection(COLLECTION_NAME)


def retrieve(query: str, k: int = TOP_K) -> list:
    """
    Return the top-k most relevant chunks for a query.

    Each result is a dict with:
      - chunk:    the text
      - source:   the originating document path
      - score:    cosine distance (lower = more relevant)
    """
    _load()

    embedding = _model.encode([query]).tolist()
    results   = _collection.query(query_embeddings=embedding, n_results=k)

    return [
        {
            "chunk":  doc,
            "source": meta["source"],
            "score":  round(score, 4),
        }
        for doc, meta, score in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


if __name__ == "__main__":
    test_queries = [
        "What happens if a student receives an incomplete grade?",
        "What are the CS degree options?",
        "How do I apply for graduation?",
        "What is the tuition refund policy?",
        "What is the academic integrity policy?",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        for r in retrieve(query):
            print(f"  [{r['score']}] {r['source']}")
            print(f"  {r['chunk'][:200]}\n")
