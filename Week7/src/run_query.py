# run_query.py

import faiss
import pickle

from src.embeddings.embedder import Embedder
from src.retriever.hybrid_retriever import HybridRetriever
from src.retriever.bm25 import BM25store
from src.pipelines.context_builder import ContextBuilder


INDEX_PATH = "src/indexes/index.faiss"
METADATA_PATH = "src/indexes/metadata.pkl"
BM25_PATH = "src/indexes/bm25.pkl"


def main():

    query = "Explain how credit underwriting works"
    top_k = 5
    filters = {"year": "2022", "type": "Document"}

    print("Loading FAISS index...")
    index = faiss.read_index(INDEX_PATH)

    print("Loading metadata...")
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)

    print("Loading BM25 store...")
    bm25_store = BM25store.load(BM25_PATH)

    print("Loading embedding model...")
    embedder = Embedder()   

    # IMPORTANT:
    # HybridRetriever expects an embedding_model with .encode()
    # So we pass embedder.model (SentenceTransformer inside)
    retriever = HybridRetriever(
        dense_index=index,
        embedding_model=embedder.model,
        metadata_store=metadata,
        bm25_store=bm25_store
    )

    print("Running retrieval...")
    results = retriever.retrieve(
        query=query,
        top_k=top_k,
        filters=filters
    )

    print("Building context...")
    builder = ContextBuilder()
    final_context = builder.build(results)

    print("\n===== FINAL CONTEXT =====\n")
    print(final_context["context"])

    print("\n===== SOURCES =====\n")
    print(final_context["sources"])


if __name__ == "__main__":
    main()