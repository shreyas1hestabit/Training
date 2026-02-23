from sentence_transformers import SentenceTransformer #sentence-transformer is a pre-trained ai model specifically desgined to turn sentences to mathematical vectors.
import torch #to check if we have gpu or not and if not then work on c
import numpy as np #use it at the end to format numbers properly.


class Embedder:
    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu" #sets hardware target for the ai model. if we have gpu then use gpu else fallback to the cpu.
        self.model = SentenceTransformer(model_name, device=self.device) #loads the ai model to the computer's memory on the chosen device.

    def embed(self, texts, batch_size=32): # texts is a list of string and batch tells the ai to process 32 sentences at a time. saves time.
        #32 is the safest batch size not too small not to large for systems to crash.
        embeddings = self.model.encode( # here actual thinking happens. model looks at the text and calculates its vectors.
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True #this makes every vector have a length of 1 which makes comparison between two text pieces easy.
            #we need this because length of the embedding is often influenced by things that dont matter like how many words are in the sentence or how common certain words are. by making them same length i.e. 1 we can compare them based only on the direction they are pointing.
        )
        return np.array(embeddings, dtype="float32") #converts the output to a numpy array and ensures that numbers are stored in 32 bit decimals(standard format)
        #earlier it was being returned in list format but we converted it into numpy array because of three main reasons
         #1. memory compression - standard python is 64bit but we cut them into half 32bit
         #2. universal compatibiltiy- almost every search tool (faiss, chromedb) requires data to be in a numpy array format.
         #3. speed - numpy uses vectorized math to calculated similarity which is faster than standard python for loop.