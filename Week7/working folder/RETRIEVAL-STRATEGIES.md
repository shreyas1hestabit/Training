# RETRIEVAL-STRATEGIES.md

## Overview

This project implements an advanced retrieval pipeline for a Retrieval-Augmented Generation (RAG) system.

The goal is to move from basic semantic search to a production-grade retrieval system that is:

- High recall (finds all relevant information)
- High precision (returns only the best chunks)
- Diverse (avoids repetition)
- Traceable (sources are auditable)
- Robust (handles edge cases like filtering failures)

---

## Retrieval Pipeline Architecture

User Query
   ↓
Query Embedding (BGE)
   ↓
Dense Retrieval (FAISS)
   ↓
Keyword Retrieval (BM25)
   ↓
Fusion (RRF)
   ↓
Metadata Filtering
   ↓
MMR (Diversity)
   ↓
Cross-Encoder Reranking
   ↓
Context Builder
   ↓
Final Context (LLM Input)

---

## Strategy 1: Semantic Retrieval (Dense Search)

### What it does
Uses embeddings to find semantically similar chunks.

### Implementation
- Model: BAAI/bge-small-en-v1.5
- Vector DB: FAISS (IndexFlatIP)
- Similarity: Inner Product (equivalent to cosine due to normalization)

### Pros
- Captures meaning (even if wording differs)
- Works well for conceptual queries

### Cons
- May miss exact keyword matches
- Sensitive to embedding quality

---

## Strategy 2: Keyword Retrieval (BM25)

### What it does
Ranks documents based on exact keyword matching.

### Implementation
- Library: rank_bm25
- Tokenization: simple split()

### Pros
- Strong for exact matches
- Works well for factual queries

### Cons
- No semantic understanding
- Fails on paraphrased queries

---

## Strategy 3: Hybrid Retrieval (Dense + BM25)

### Why needed
Neither dense nor keyword search alone is sufficient.

### Solution
Combine both for better recall and coverage.

---

## Strategy 4: Reciprocal Rank Fusion (RRF)

### What it does
Combines rankings from dense search and BM25.

### Formula
Score = Σ (1 / (k + rank))

### Pros
- Simple and effective
- No need for score normalization

### Cons
- Ignores actual score magnitudes

---

## Strategy 5: Metadata Filtering

### What it does
Filters documents based on metadata fields.

### Pros
- Reduces search space
- Enables structured retrieval

### Cons
- Strict matching may remove all results
- Depends on metadata quality

---

## Strategy 6: MMR (Max Marginal Relevance)

### Problem
Top results are often redundant.

### Solution
Balances relevance and diversity.

### Formula
MMR = λ * relevance - (1 - λ) * similarity_to_selected

### Pros
- Reduces repetition
- Improves context diversity

### Cons
- Additional computation required

---

## Strategy 7: Cross-Encoder Reranking

### What it does
Re-evaluates relevance using full query-document interaction.

### Implementation
- Model: BAAI/bge-reranker-base

### Pros
- Highest accuracy
- Captures deep relationships

### Cons
- Slower than embedding-based methods
- Expensive for large candidate sets

---

## Strategy 8: Deduplication

### What it does
Removes repeated or similar chunks.

### Pros
- Cleaner context
- Reduces noise

---

## Strategy 9: Context Engineering

### What it does
Builds final input for the LLM.

### Features
- Combines top chunks
- Maintains order
- Adds source traceability

### Pros
- Reduces hallucination
- Enables auditability

---

## Trade-offs Summary

Component | Benefit | Cost
----------|--------|------
Dense Search | Semantic understanding | Misses keywords
BM25 | Exact matching | No semantics
RRF | Robust fusion | Ignores scores
MMR | Diversity | Extra computation
Reranker | High precision | Slow
Filtering | Control | Can over-filter

---

## Final Outcome

This pipeline achieves:

- Higher Recall (Hybrid Retrieval)
- Higher Precision (Reranking)
- Better Diversity (MMR)
- Reduced Hallucination (Context Engineering)
- Traceable Answers (Metadata + Sources)

---

## Future Improvements

- Replace BM25 with ElasticSearch
- Use ANN index (IVF, HNSW)
- Add query expansion
- Use LLM-based reranking
- Introduce feedback loop

---

## Key Takeaway

Retrieval quality directly determines LLM answer quality.

A strong retriever:
- Finds the right information
- Filters noise
- Structures context
