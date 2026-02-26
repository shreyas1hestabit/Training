from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import pytesseract
from PIL import Image
import io

from src.memory.memory_store import MemoryStore
from src.evaluation.rag_eval import RAGEvaluator
from src.retriever.hybrid_retriever import HybridRetriever
from src.generator.sql_generator import SQLGenerator
from src.utils.blip_captioner import BLIPCaptioner
from src.embeddings.clip_embedder import CLIPEmbedder

from src.loaders.loader import load_dense_index, load_embedding_model, load_metadata, load_bm25

app = FastAPI(title="RAG System")

memory = MemoryStore()
evaluator = RAGEvaluator()
sql_generator = SQLGenerator()
captioner=BLIPCaptioner()
clip_model=CLIPEmbedder()



dense_index = load_dense_index()
embedding_model = load_embedding_model()
metadata_store = load_metadata()
bm25_store = load_bm25()

retriever = HybridRetriever(
    dense_index,
    embedding_model,
    metadata_store,
    bm25_store
)



class QueryRequest(BaseModel):
    question: str


def refinement_loop(question: str, context: str, initial_answer: str) -> str:
    critique_prompt = f"""
    Question: {question}
    Context: {context}
    Initial Answer: {initial_answer}

    Improve the answer strictly using context.
    """

    return sql_generator.generate(critique_prompt, context,mode="rag")



@app.post("/ask")
def ask(request: QueryRequest):

    memory_context = memory.format_memory_for_prompt()

    docs = retriever.retrieve(request.question)
    context = "\n".join([d["text"] for d in docs])

    full_context = memory_context + "\n" + context

    answer = sql_generator.generate(request.question, full_context,mode="rag")

    refined_answer = refinement_loop(request.question, context, answer)

    faithfulness = evaluator.faithfulness_score(refined_answer, context)
    context_match = evaluator.context_match_score(request.question, context)
    hallucination = evaluator.hallucination_detected(refined_answer, context)
    confidence = evaluator.confidence_score(
        faithfulness, context_match, hallucination
    )

    interaction = {
        "question": request.question,
        "retrieved_docs": docs,
        "answer": refined_answer,
        "faithfulness": faithfulness,
        "context_match": context_match,
        "hallucination": hallucination,
        "confidence": confidence,
        "timestamp": datetime.now().isoformat(),
    }

    memory.add_interaction(interaction)

    return {
        "answer": refined_answer,
        "confidence": confidence,
        "hallucination": hallucination,
    }



# @app.post("/ask-image")
# async def ask_image(file: UploadFile = File(...)):

#     contents = await file.read()
#     image = Image.open(io.BytesIO(contents))
#     extracted_text = pytesseract.image_to_string(image).strip()

#     print(f"[OCR OUTPUT]: '{extracted_text}'")
#     if not extracted_text:
#         return {"answer":"could not extract any text from image"}

#     docs = retriever.retrieve(extracted_text)
#     context = "\n".join([d["text"] for d in docs])

#     answer = sql_generator.generate(extracted_text, context,mode="rag")

#     interaction={
#         "question":f"[IMAGE QUERY]: {extracted_text[:50]}...",
#         "answer":answer,
#         "type":"image",
#         "timestamp":datetime.now().isoformat()
#     }
#     memory.add_interaction(interaction)
#     return {"answer": answer}
# Create a new Pydantic model for image requests
class ImageQueryRequest(BaseModel):
    question: str

# @app.post("/ask-image")
# async def ask_image(question: str = Form(...), file: UploadFile = File(...)):
#     # 1. Image processing
#     contents = await file.read()
#     image = Image.open(io.BytesIO(contents))
    
#     # 2. OCR Extraction [cite: 181, 189]
#     extracted_text = pytesseract.image_to_string(image)

#     # 3. Retrieve relevant docs based on OCR + User Question [cite: 175, 178]
#     search_query = f"{question} {extracted_text[:200]}"
#     docs = retriever.retrieve(search_query)
#     retrieved_context = "\n".join([d["text"] for d in docs])

#     # 4. Multimodal Reasoning Prompt [cite: 173, 204]
#     # Note: Hum yahan SQL generator nahi, General LLM prompt use karenge
#     prompt = f"""
#     You are an expert technical assistant.
    
#     USER QUESTION: {question}
    
#     TEXT EXTRACTED FROM IMAGE (OCR):
#     {extracted_text}
    
#     SUPPORTING CONTEXT FROM KNOWLEDGE BASE:
#     {retrieved_context}
    
#     INSTRUCTION: Answer the user question based on the image text and provided context.
#     """

#     # Model call (Make sure to use a non-SQL specific method if possible)
#     answer = sql_generator.generate(prompt, "") 

#     # 5. Logging for Day 5 Requirements [cite: 254, 267]
#     memory.add_interaction({
#         "question": f"[IMAGE] {question}",
#         "answer": answer,
#         "timestamp": datetime.now().isoformat()
#     })

#     return {"answer": answer}

@app.post("/ask-image")
async def ask_image(question: str = Form(...), file: UploadFile = File(...)):
    # 1. Image loading
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    
    # 2. Visual Understanding (Day 3 logic integration)
    # Yeh part 'Apple' ko identify karega jab OCR fail ho jaye
    visual_caption = captioner.generate_caption(image) # Example: "a photo of a red apple"
    extracted_text = pytesseract.image_to_string(image).strip()

    # 3. Multimodal Context Building
    # Hum context ko combine karenge taaki LLM ko puri picture mile
    combined_visual_context = f"Image Description: {visual_caption}\nOCR Text: {extracted_text}"
    
    # Optional: Retrieve similar images/docs using CLIP if needed
    # docs = retriever.retrieve(visual_caption) 

    # 4. Generate Answer using your SQLGenerator in 'rag' mode
    prompt_context = f"Visual Analysis: {combined_visual_context}"
    answer = sql_generator.generate(question, prompt_context, mode="rag")

    # 5. Logging (Day 5 Capstone Requirement)
    memory.add_interaction({
        "question": f"[IMAGE] {question}",
        "answer": answer,
        "visual_caption": visual_caption,
        "timestamp": datetime.now().isoformat()
    })

    return {"answer": answer, "caption": visual_caption}


@app.post("/ask-sql")
def ask_sql(request: QueryRequest):

    conn = sqlite3.connect("src/data/cleaned/database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    schema = "\n".join([row[0] for row in cursor.fetchall() if row[0]])

    sql_query = sql_generator.generate(request.question, schema, mode="sql")

    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
    except Exception as e:
        result = str(e)

    conn.close()
    interaction = {
        "question": request.question,
        "answer": f"SQL Result: {str(result)[:100]}",
        "sql": sql_query,
        "type": "sql",
        "timestamp": datetime.now().isoformat()
    }
    memory.add_interaction(interaction)
    return {
        "sql_query": sql_query,
        "result": result
    }