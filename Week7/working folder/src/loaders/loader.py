import faiss
import pickle

from src.embeddings.embedder import Embedder
from src.retriever.bm25 import BM25store

INDEX_PATH = "src/indexes/index.faiss"
METADATA_PATH = "src/indexes/metadata.pkl"
BM25_PATH = "src/indexes/bm25.pkl"


def load_dense_index():
    return faiss.read_index(INDEX_PATH)


def load_metadata():
    with open(METADATA_PATH, "rb") as f:
        return pickle.load(f)


def load_bm25():
    return BM25store.load(BM25_PATH)


def load_embedding_model():
    embedder = Embedder()
    return embedder.model  