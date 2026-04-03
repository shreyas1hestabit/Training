# Import necessary libraries
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Define the retrieval and generation models
retrieval_model = "facebook/dpr-ctx_encoder-multiset"
generation_model = "t5-small"

# Initialize the tokenizer
tokenizer = AutoTokenizer.from_pretrained(generation_model)

# Initialize the RAG pipeline with the selected models
rag_pipeline = RAGPipeline(retrieval_model, generation_model, tokenizer)