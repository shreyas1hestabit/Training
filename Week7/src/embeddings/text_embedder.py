from sentence_transformers import SentenceTransformer
import numpy as np


class TextEmbedder:
    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-small-en")

    def encode(self, text: str):
        embedding = self.model.encode(text, normalize_embeddings=True)
        return np.array([embedding])