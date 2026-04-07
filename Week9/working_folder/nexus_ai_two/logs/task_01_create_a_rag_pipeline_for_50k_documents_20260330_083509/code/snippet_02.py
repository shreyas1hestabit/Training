# Usage example
query = "What is the capital of Germany?"
documents = [
    "The capital of Germany is Berlin.",
    "Berlin is the capital and largest city of Germany.",
    "The Brandenburg Gate is located in Berlin, Germany.",
    "Germany is a country located in Central Europe.",
    "The official language of Germany is German."
]

# Initialize the RAG pipeline
retrieval_model = AutoModelForSeq2SeqLM.from_pretrained('distilbert-base-uncased')
generation_model = AutoModelForSeq2SeqLM.from_pretrained('t5-small')
tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
rag_pipeline = RAGPipeline(retrieval_model, generation_model, tokenizer)

# Perform retrieval and generation
retrieved_documents = rag_pipeline.retrieve(query, documents)
generated_text = rag_pipeline.generate(query, retrieved_documents)

# Print the generated text
print(generated_text)