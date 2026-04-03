import json
import numpy as np
from pathlib import Path
from typing import Optional

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False


INDEX_PATH    = Path(__file__).parent / "faiss.index"
METADATA_PATH = Path(__file__).parent / "vector_metadata.json"

# Embedding model — small, fast, good quality for semantic search
EMBED_MODEL = "all-MiniLM-L6-v2"   # 384-dim, ~22 MB download on first use
EMBED_DIM   = 384

class VectorStore:
    """
    FAISS-backed semantic memory.

    Each entry stored has:
        text   : the raw text that was embedded
        source : where it came from ("fact", "episode", "conversation", etc.)
        meta   : optional arbitrary dict for extra fields

    Usage
    -----
        store = VectorStore()
        store.add("Alice is a software engineer", source="fact")
        results = store.search("what does Alice do?", top_k=3)
        for r in results:
            print(r["score"], r["text"])
    """

    def __init__(
        self,
        index_path: Path = INDEX_PATH,
        metadata_path: Path = METADATA_PATH,
        model_name: str = EMBED_MODEL,
    ):
        if not FAISS_AVAILABLE:
            raise ImportError("faiss-cpu is required: pip install faiss-cpu")
        if not ST_AVAILABLE:
            raise ImportError("sentence-transformers is required: pip install sentence-transformers")

        self.index_path    = index_path
        self.metadata_path = metadata_path
        self._model        = SentenceTransformer(model_name)
        self._metadata: list[dict] = []
        self._index: Optional[faiss.IndexFlatL2] = None

        self._load()

    def _load(self) -> None:
        """Load existing index + metadata from disk, or create fresh ones."""
        if self.index_path.exists() and self.metadata_path.exists():
            self._index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self._metadata = json.load(f)
        else:
            self._index = faiss.IndexFlatL2(EMBED_DIM)
            self._metadata = []

    def save(self) -> None:
        """Persist index and metadata to disk."""
        faiss.write_index(self._index, str(self.index_path))
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self._metadata, f, indent=2, ensure_ascii=False)

    def add(self, text: str, source: str = "unknown", meta: dict | None = None) -> int:
        """
        Embed `text` and add it to the index.

        Parameters
        ----------
        text   : The text to store and embed.
        source : Label for where this came from (e.g. "fact", "episode").
        meta   : Optional extra metadata dict.

        Returns
        -------
        int : The index position of the new entry.
        """
        if not text.strip():
            return -1

        embedding = self._embed(text)
        self._index.add(embedding)

        entry = {
            "id":     len(self._metadata),
            "text":   text,
            "source": source,
            "meta":   meta or {},
        }
        self._metadata.append(entry)
        self.save()
        return entry["id"]

    def add_batch(self, texts: list[str], source: str = "batch") -> list[int]:
        """Embed and add multiple texts at once (faster than individual adds)."""
        texts = [t for t in texts if t.strip()]
        if not texts:
            return []

        embeddings = self._model.encode(texts, convert_to_numpy=True).astype("float32")
        self._index.add(embeddings)

        ids = []
        for text in texts:
            entry = {
                "id":     len(self._metadata),
                "text":   text,
                "source": source,
                "meta":   {},
            }
            self._metadata.append(entry)
            ids.append(entry["id"])

        self.save()
        return ids

    def search(self, query: str, top_k: int = 3, score_threshold: float = 2.0) -> list[dict]:
        """
        Find the top_k most semantically similar stored texts.

        Parameters
        ----------
        query          : The search query (embedded on the fly).
        top_k          : Number of results to return.
        score_threshold: L2 distance cutoff — higher = more permissive.
                         L2 distance of 0 = identical, ~2.0 = loosely related.

        Returns
        -------
        list of dicts with keys: id, text, source, meta, score
        """
        if self._index.ntotal == 0:
            return []

        k = min(top_k, self._index.ntotal)
        query_vec = self._embed(query)
        distances, indices = self._index.search(query_vec, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1 or dist > score_threshold:
                continue
            entry = self._metadata[idx].copy()
            entry["score"] = float(dist)
            results.append(entry)

        return results

    def get_all(self) -> list[dict]:
        """Return all stored entries (without embeddings)."""
        return list(self._metadata)

    def count(self) -> int:
        return self._index.ntotal if self._index else 0

    def delete_by_source(self, source: str) -> int:
        """
        Remove all entries from a given source.
        FAISS flat indices don't support in-place deletion, so we rebuild.
        Returns number of entries removed.
        """
        keep = [m for m in self._metadata if m["source"] != source]
        removed = len(self._metadata) - len(keep)
        if removed == 0:
            return 0

        self._rebuild(keep)
        return removed

    def reset(self) -> None:
        """Wipe the entire index."""
        self._index    = faiss.IndexFlatL2(EMBED_DIM)
        self._metadata = []
        self.save()

    def _rebuild(self, entries: list[dict]) -> None:
        """Rebuild the FAISS index from a filtered metadata list."""
        texts = [e["text"] for e in entries]
        self._index    = faiss.IndexFlatL2(EMBED_DIM)
        self._metadata = []

        if texts:
            embeddings = self._model.encode(texts, convert_to_numpy=True).astype("float32")
            self._index.add(embeddings)
            for i, entry in enumerate(entries):
                entry["id"] = i
                self._metadata.append(entry)

        self.save()

    def _embed(self, text: str) -> np.ndarray:
        """Return a (1, EMBED_DIM) float32 numpy array."""
        vec = self._model.encode([text], convert_to_numpy=True)
        return vec.astype("float32")

    def format_context(self, results: list[dict]) -> str:
        """
        Format search results into a string ready to inject into an LLM prompt.

        Example output:
            [Memory 1 | source: fact] Alice is a software engineer.
            [Memory 2 | source: episode] Alice mentioned she prefers Python.
        """
        if not results:
            return ""
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"[Memory {i} | source: {r['source']}] {r['text']}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"VectorStore(entries={self.count()}, index='{self.index_path.name}')"