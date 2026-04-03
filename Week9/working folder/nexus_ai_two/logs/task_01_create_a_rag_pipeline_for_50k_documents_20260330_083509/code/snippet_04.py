# Create a RAG pipeline instance
pipeline = RAGPipeline(
    retrieval_model='sentence-transformers/all-MiniLM-L6-v2',
    generation_model='t5-base',
    tokenizer='t5-base'
)

# Define a sample corpus of documents
corpus = [
    'This is a sample document about machine learning.',
    'Another document about natural language processing.',
    'A document about deep learning techniques.',
    # ... 50k documents ...
]

# Preprocess the corpus
tfidf_vectors, vectorizer = pipeline.preprocess_corpus(corpus)

# Define a sample query
query = 'What is machine learning?'

# Perform retrieval
retrieved_indices, similarities = pipeline.retrieve(query, tfidf_vectors, vectorizer)

# Perform generation
generated_text = pipeline.generate(query, retrieved_indices)

# Print the generated text
print(generated_text)