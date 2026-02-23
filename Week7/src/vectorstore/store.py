# this acts as a search engine. stores the numbers(embeddings) and quickly finds the most relevant ones.
import faiss
import pickle
import numpy as np
import os

class VectorStore:
    def __init__(self,dimension):
        self.index = faiss.IndexFlatIP(dimension) #using faiss for similarity search
        # flat index ip stands for inner product. we are using this because we have already normalized embeddings earlier so this is mathematically same as cosine similarity.
        #cosine similarity ka perfect score is 1.0 whereas ip mein if we have not normalized then it could be any number 50,100,75 etc. but as we have normalized so it's output will also range between 0 and 1.
        # dimension is the width of the vector. the db needs to know the size to align the numbers correctly.
        # our model captures 384 dimensions.
        # we tells faiss the dimension because it needs to know the datasize it can expect to allocate memory and prepare high-speed math equations.
        # faiss basically reserves a block of ram each time we call add(), it grabs the next 384 numbers and treats them as one single record. 
        self.metadata=[] #initializes empty list to store metadata.
    def add(self,embeddings,metadata_list):
        self.index.add(embeddings) # this wires the numbers into faiss index so that they can be searched.
        self.metadata.extend(metadata_list) # faiss stores numbers and not text. we maintain a seperate list(metadata) to store actual text chunks and page numbers. extend() is used to add multiple items to our list at once.
    def save (self, index_path, metadata_path):
        folder=os.path.dirname(index_path)
        os.makedirs(folder,exist_ok=True)
        faiss.write_index(self.index,index_path) #stores the complex mathematical index to a file so you dont have to re-process the pdf every time we run the script
        with open(metadata_path,"wb") as f: #wb-> write binary
            pickle.dump(self.metadata,f) #pickle is a python tool that takes complex object and freezes it into a file. dump actually writes the data to the file.
    def search(self,query_embedding, top_k=3): #main part where we type a question and it finds the best matches.
        # query_embeddings is the vector version of my query and top_k=3 tells the faiss to return top 3 best matches
        scores, indices= self.index.search(query_embedding,top_k) # scores tell how similar the match is and indices are the address or id of the matching chunk.
        results=[] #initializes an empty list of results.

        #this loop goes through the top3 matches. it grabs the score and the metadata and puts them into a clean python dictionary.
        for i, idx in enumerate(indices[0]): #i is the integer id given to vectors based on the order they arrived in faiss.
            #idx basically is the current id we are working on
            #indices[0] is the list of top id found.
            # faiss is designed to handle batch searches. even if we ask one question it puts ans inside another list so we grab the inner list at position 0. 
            results.append({
                "score": scores[0][i],
                "metadata": self.metadata[idx]
            })
        return results