#this is the main orchestrator which brings all the pieces together to create a complete automated pipeline.
import os 
from src.loaders.pdf_loader import load_pdf
from src.chunking.chunker import create_chunks
from src.embeddings.embedder import Embedder
from src.vectorstore.store import VectorStore

def run_raw_ingestion(data_folder):
    all_chunks=[]
    all_metadata=[]
    for file_name in os.listdir(data_folder): #this looks inside data/raw folder and lists every file it sees.
        if not file_name.endswith(".pdf"): #this is a safety filter.. if there is an image or a hidden system file in that folder the code will skip it and only look for pdfs.
            continue
        file_path=os.path.join(data_folder,file_name)
        pages=load_pdf(file_path)

        for text, page_number in pages: #it loops through every page for text, page_number 
            chunks = create_chunks(text) #breaks each page into smaller pieces

            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadata.append({ 
                    "source": file_name, #which pdf did chunk came from
                    "page":page_number, #which page was it on
                    "chunk_id":i, #which piece of that page is this
                    "text": chunk #the actual text data 
                    #by saving the text inside metadata, the vectorstoreloop will be able to show exactly what the ai found
                })
    print (f"total chunks created: {len(all_chunks)}")
    embedder=Embedder()
    # embeddings=embedder.embed(all_chunks)  #takes massive list of thousands of text chunks and send them to the AI model. this outputs a large matrix where every row is a 384 dimension vector.
    formatted_chunks = [f"passage: {chunk}" for chunk in all_chunks]  #to improve model accuracy we prefix passage. we are now basically giving hint to the model by saying trear this text as piece of knowlefge that might be used to ans a question later.
    #previously it was just storing text as a string it did not know if it is passage, query or a document. 
    #this improves the accuracy by 5-10%. the direction of the vector in 384D space will shift slightly towards the knowledge/ans cluster of model's brain.
    embeddings = embedder.embed(formatted_chunks) 

    dimension= embeddings.shape[1] #instead of hardcoding the dimension 384 the code looks at the result of the embedding to determine how many columns do these numbers have. in a 2d table matrix 
    store= VectorStore(dimension)
    store.add(embeddings,all_metadata)
    store.save(
        "src/indexes/index.faiss", #this is the math map which stores the coordinates of the text in 384 dimensional space. it does not store words or file names.
        "src/indexes/metadata.pkl" #this is the next dictionary which stores the serialized versionof python all_metadata list. it acts as the lookup table that links vector id back to actual text.
    )
    print("ingestion complete")

if __name__=="__main__":
    run_raw_ingestion("src/data/raw")