import faiss
import pickle
import numpy as np
import time
from src.embeddings.embedder import Embedder


class QueryEngine:

    def __init__(self, index_path, metadata_path):
        # Load FAISS index
        self.index = faiss.read_index(index_path)

        # Load metadata
        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

        # Initialize embedder
        self.embedder = Embedder()

    def search(self, query: str, top_k: int = 5):
        query = f"query: {query}"
        # Embed query
        query_vector = self.embedder.embed([query])

        # Convert to numpy float32
        query_vector = np.array(query_vector).astype("float32")

        #  Search FAISS
        distances, indices = self.index.search(query_vector, top_k)

        # Fetch matching chunks
        results = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])

        return results

if __name__ == "__main__":

    engine = QueryEngine(
        index_path="src/indexes/index.faiss",
        metadata_path="src/indexes/metadata.pkl"
    )

    #query = "What is equity compensation plan? "
    query= "What is equity compensation plan of ZIFF DAVIS, INC? "

    st = time.perf_counter()
    results = engine.search(query, top_k=3)
    et = time.perf_counter()
    print(f"Printed results in {et-st:.4f} seconds \n") 
    
    for i, res in enumerate(results):
        print(f"\nResult {i+1}:\n{res}\n")