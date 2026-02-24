from rank_bm25 import BM25Okapi
import pickle
import os

class BM25store:
    def __init__(self,documents=None):
        self.documents= documents or []
        self.tokenized_docs=[doc.split() for doc in self.documents]
        self.bm25= BM25Okapi(self.tokenized_docs)
    
    def search(self,query,top_k=5):
        tokenized_query=query.split()
        scores=self.bm25.get_scores(tokenized_query)
        ranked = sorted(
            list(enumerate(scores)),
            key= lambda x:x[1],
            reverse=True
        )
        return ranked[:top_k]
      
    def save(self,path):
        os.makedirs(os.path.dirname(path),exist_ok=True)
        with open(path,"wb") as f:
            pickle.dump(self.documents,f)

    @classmethod
    def load(cls,path):
        with open(path,"rb") as f:
            documents=pickle.load(f)
        return cls(documents)