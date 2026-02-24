from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self,model_name="BAAI/bge-reranker-base"):
        self.model=CrossEncoder(model_name)
    
    def rerank(self,query,documents,top_k=5):
        pairs=[[query,doc] for doc in documents]
        scores= self.model.predict(pairs)

        ranked=sorted(
            list(zip(documents,scores)),
            key=lambda x: x[1],
            reverse=True
        )

        return [doc for doc, _ in ranked[:top_k]]