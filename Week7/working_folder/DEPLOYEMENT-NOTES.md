# Advanced RAG Capstone Deployment Notes

## Features Implemented

- Conversational memory (last 5 interactions)
- Hybrid retrieval (FAISS + BM25)
- Self-refinement loop
- Hallucination detection
- Faithfulness scoring
- Confidence scoring
- Logging to CHAT-LOGS.json
- FastAPI endpoints:
  - /ask
  - /ask-image
  - /ask-sql

## How to Run

uvicorn src.deployment.app:app --reload

## Architecture

User → Memory → Retrieval → LLM → Refinement → Evaluation → Logging → Response
