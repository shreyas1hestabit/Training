#now we are working on the retrieval part of the project

from rank_bm25 import BM25Okapi
import pickle
import os

class BM25store:
    def __init__(self,documents=None):
        self.documents= documents or [] #self.documents mein meri list aa rhi hai chunks ki 
        self.tokenized_docs=[doc.split() for doc in self.documents] #bm25 does not work on full strings. because it counts the frequency of words toh it needs one single word at a time to process. 
        self.bm25= BM25Okapi(self.tokenized_docs) #bm25 takes the list of all the words and builds a mathematical table. it counts how ofetn a word appears accross all my chunks.
    
    def search(self,query,top_k=5):
        tokenized_query=query.split() #this splits the query like it did to the document
        scores=self.bm25.get_scores(tokenized_query) #this generates the score. it returns a list of numbers (score) for every chunk. score we are refering here is the similarity score.
        #eg: query -> the lion is the king.
        # now it starts matching the appears in almost all the documents so its score is 0, lion appears 3 times suppose so it gives score accordingly , king appears rarely so it gives it a massive score.

        #this is the sorting logic 
        ranked = sorted(
            list(enumerate(scores)), #enumerate attaches an id to every score basically attaches an index to the scores.
            key= lambda x:x[1], #this tells python to sort based on the score and not the index. as it is stored in the format [[index,score]] where index is at 0 position and score at 1, therefore we are using x[1].
            reverse=True #put the highest scores at the top.
        )
        return ranked[:top_k] #only give me the top_k results (5 in our case.)
      
    def save(self,path):
        os.makedirs(os.path.dirname(path),exist_ok=True)
        with open(path,"wb") as f:
            pickle.dump(self.documents,f)

    @classmethod
    def load(cls,path):
        with open(path,"rb") as f:
            documents=pickle.load(f)
        return cls(documents)