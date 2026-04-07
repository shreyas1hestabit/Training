# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# from sentence_transformers import SentenceTransformer


# class RAGEvaluator:
#     def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
#         self.embedder = SentenceTransformer(model_name)

#     def embed(self, text: str):
#         return self.embedder.encode([text])[0]

#     def faithfulness_score(self, answer: str, context: str) -> float:
#         ans_vec = self.embed(answer)
#         ctx_vec = self.embed(context)
#         score = cosine_similarity([ans_vec], [ctx_vec])[0][0]
#         return float(score)

#     def context_match_score(self, query: str, context: str) -> float:
#         q_vec = self.embed(query)
#         ctx_vec = self.embed(context)
#         score = cosine_similarity([q_vec], [ctx_vec])[0][0]
#         return float(score)

#     def hallucination_detected(self, answer: str, context: str, threshold=0.4) -> bool:
#         score = self.faithfulness_score(answer, context)
#         return score < threshold

#     def confidence_score(
#         self,
#         faithfulness: float,
#         context_match: float,
#         hallucination: bool
#     ) -> float:
#         base = (faithfulness * 0.6) + (context_match * 0.4)
#         if hallucination:
#             base *= 0.5
#         return round(base, 3)

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class RAGEvaluator:
    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        # Model loading for embedding generation [cite: 50, 91]
        self.embedder = SentenceTransformer(model_name)

    def embed(self, text: str):
        # Generate local embeddings [cite: 124]
        return self.embedder.encode([text])

    def faithfulness_score(self, answer: str, context: str) -> float:
        # Measures how faithful the answer is to the retrieved context [cite: 247, 290]
        if not answer or not context: return 0.0
        ans_vec = self.embed(answer)
        ctx_vec = self.embed(context)
        score = cosine_similarity(ans_vec, ctx_vec)[0][0]
        return float(score) # Ensuring Python float conversion 

    def context_match_score(self, query: str, context: str) -> float:
        # Checks if retrieved context matches the user query [cite: 252, 290]
        if not query or not context: return 0.0
        q_vec = self.embed(query)
        ctx_vec = self.embed(context)
        score = cosine_similarity(q_vec, ctx_vec)[0][0]
        return float(score)

    def hallucination_detected(self, answer: str, context: str, threshold=0.4) -> bool:
        # Hallucination detection logic [cite: 246, 265]
        score = self.faithfulness_score(answer, context)
        return bool(score < threshold) # Explicit boolean for JSON safety

    def confidence_score(
        self,
        faithfulness: float,
        context_match: float,
        hallucination: bool
    ) -> float:
        # Final scoring logic for production-ready monitoring [cite: 266, 285]
        base = (float(faithfulness) * 0.6) + (float(context_match) * 0.4)
        if hallucination:
            base *= 0.5
        return float(round(base, 3))