import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.retriever.bm25 import BM25store
from src.retriever.rrf import reciprocal_rank_fusion
from src.retriever.reranker import Reranker


class HybridRetriever:
    def __init__(self, dense_index, embedding_model, metadata_store, bm25_store):
        self.dense_index = dense_index
        self.embedding_model = embedding_model
        self.metadata = metadata_store
        self.bm25 = bm25_store
        self.reranker = Reranker()

    # Metadata Filtering
    def _apply_filters(self, filters):
        if not filters:
            return list(range(len(self.metadata)))

        valid = []
        for idx, meta in enumerate(self.metadata):

            match = True
            for k,v in filters.items():
                meta_val=meta.get(k)

                if meta_val is None:
                    match=False
                    break

                if isinstance(meta_val,str) and isinstance(v,str):
                    if meta_val.lower()!=v.lower():
                        match=False
                        break
                    else:
                        if meta_val!=v:
                            match=False
                            break
                if match:
                    valid.append(idx)
        return valid
    # Dense Retrieval
    def _dense_search(self, query, top_k):
        query_vec = self.embedding_model.encode([query])
        distances, indices = self.dense_index.search(query_vec, top_k)

        return [(idx, float(score)) for score, idx in zip(distances[0], indices[0])]


    # MMR (Diversity)
    def _mmr(self, query, candidate_indices, top_k, lambda_param=0.7): #lambda tells what to priortize diversity or relevance. higher the lambda the more relevance would be priortized.
        if not candidate_indices:
            return[]
        selected = []

        query_vec = self.embedding_model.encode([query])
        doc_vecs = self.embedding_model.encode(
            [self.metadata[idx]["text"] for idx in candidate_indices]
        )

        similarity_to_query = cosine_similarity(query_vec, doc_vecs)[0]

        while len(selected) < min(top_k, len(candidate_indices)):

            if not selected:
                selected_idx = np.argmax(similarity_to_query)
            else:
                selected_vecs = doc_vecs[selected]
                sim_to_selected = cosine_similarity(
                    doc_vecs, selected_vecs
                ).max(axis=1)

                mmr_score = (
                    lambda_param * similarity_to_query
                    - (1 - lambda_param) * sim_to_selected
                )

                for s in selected:
                    mmr_score[s] = -np.inf

                selected_idx = np.argmax(mmr_score)

            selected.append(selected_idx)

        return [candidate_indices[i] for i in selected]

    # Main Retrieval Pipeline
    def retrieve(self, query, top_k=5, filters=None):
        # fused_indices = reciprocal_rank_fusion(dense_results, bm25_results)

        #  Metadata filtering
        valid_indices = self._apply_filters(filters)
        if not valid_indices:
            print("warning: filters removed all documents. ignoring filters")
            valid_indices=list(range(len(self.metadata)))

        # Dense retrieval
        dense_results = self._dense_search(query, top_k * 4)
        dense_results = [(i, s) for i, s in dense_results if i in valid_indices]

        #  BM25 retrieval
        bm25_results = self.bm25.search(query, top_k * 4)
        bm25_results = [(i, s) for i, s in bm25_results if i in valid_indices]

        #  RRF Fusion
        fused_indices = reciprocal_rank_fusion(dense_results, bm25_results)

        #  Dedup (RRF already unique but safe)
        fused_indices = list(dict.fromkeys(fused_indices))
        if not fused_indices:
            return []

        #  MMR Diversification
        diversified_indices = self._mmr(query, fused_indices, top_k)
        if not fused_indices:
            return []
        
        print("Dense results:", len(dense_results))
        print("BM25 results:", len(bm25_results))
        print("Fused results:", len(fused_indices))
        print("diversified:", len(diversified_indices))

        # Prepare texts for reranker
        documents = [self.metadata[idx]["text"] for idx in diversified_indices]

        #  Cross-Encoder Reranking
        reranked_docs = self.reranker.rerank(query, documents, top_k)

        # Structured traceable output
        structured_output = []

        for doc in reranked_docs:
            idx = next(
                i for i in diversified_indices
                if self.metadata[i]["text"] == doc
            )

            meta = self.metadata[idx]

            structured_output.append({
                "chunk_id": idx,
                "text": doc,
                "source": meta.get("source"),
                "year": meta.get("year"),
                "type": meta.get("type")
            })

        return structured_output