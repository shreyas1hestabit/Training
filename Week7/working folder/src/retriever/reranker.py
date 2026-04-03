from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self,model_name="BAAI/bge-reranker-base"):
        self.model=CrossEncoder(model_name)
    
    def rerank(self,query,documents,top_k=5):
        pairs=[[query,doc] for doc in documents] #reranker chunks ka pair bnata hai like [[question, chunk#1]]
        scores= self.model.predict(pairs) #model looks at both the texts and read them side by side and gives a score usually between 0 to1. if score is 0.99 means chunk is perfect to answer this specifc question.

        ranked=sorted(
            list(zip(documents,scores)),
            key=lambda x: x[1],
            reverse=True
        )

        return [doc for doc, _ in ranked[:top_k]]