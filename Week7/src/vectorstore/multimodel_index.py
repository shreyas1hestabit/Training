import faiss
import pickle
import numpy as np


class MultiModalIndex:
    def __init__(self):
        self.image_index = faiss.IndexFlatIP(512)
        self.text_index = faiss.IndexFlatIP(384)
        self.metadata = []

    def add(self, image_vector, text_vector, meta):
        self.image_index.add(image_vector.astype(np.float32))
        self.text_index.add(text_vector.astype(np.float32))
        self.metadata.append(meta)

    def save(self):
        faiss.write_index(self.image_index, "src/indexes/faiss_image.index")
        faiss.write_index(self.text_index, "src/indexes/faiss_text.index")
        with open("src/indexes/faiss_metadata.pkl", "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self):
        self.image_index = faiss.read_index("src/indexes/faiss_image.index")
        self.text_index = faiss.read_index("src/indexes/faiss_text.index")
        with open("src/indexes/faiss_metadata.pkl", "rb") as f:
            self.metadata = pickle.load(f)