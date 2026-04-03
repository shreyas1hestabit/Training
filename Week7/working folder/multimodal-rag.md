# Multimodal RAG (Image-RAG) --- Day 3

## Overview

This project implements a Multimodal Retrieval-Augmented Generation
(RAG) system capable of handling images and PDFs. It supports ingestion,
embedding, indexing, and retrieval across both visual and textual
modalities.

## Objectives

-   Handle image and PDF inputs
-   Extract text using OCR
-   Generate captions using BLIP
-   Create embeddings using CLIP and BGE
-   Build a multimodal vector database
-   Support multiple query modes

## Architecture

### Ingestion Pipeline

1.  Load images or PDFs
2.  Convert PDFs to images
3.  Extract text using OCR
4.  Generate captions using BLIP
5.  Generate:
    -   Image embeddings (CLIP)
    -   Text embeddings (BGE)
6.  Store embeddings in FAISS indexes
7.  Save metadata

### Retrieval Pipeline

1.  Load FAISS indexes and metadata
2.  Accept query:
    -   Text
    -   Image
    -   PDF
3.  Convert query into embeddings
4.  Perform similarity search
5.  Return results

## Components

### 1. CLIP Embedder

-   Generates image embeddings
-   Used for image-to-image similarity

### 2. BGE Text Embedder

-   Generates text embeddings
-   Used for text-to-image retrieval

### 3. OCR Engine

-   Extracts text from images using Tesseract

### 4. BLIP Captioner

-   Generates captions for images

### 5. FAISS Vector Store

-   Stores image and text embeddings
-   Enables fast similarity search

## Supported Query Modes

### Text to Image

-   Input: Text query
-   Output: Relevant images

### Image to Image

-   Input: Image
-   Output: Visually similar images

### Image to Text

-   Input: Image or PDF
-   Output: Combined captions and OCR text

## File Structure

    src/
     ├── pipelines/
     │    └── image_ingest.py
     ├── embeddings/
     │    ├── clip_embedder.py
     │    └── text_embedder.py
     ├── retriever/
     │    └── image_search.py
     ├── utils/
     │    ├── ocr_engine.py
     │    ├── blip_captioner.py
     │    └── pdf_utils.py
     ├── vectorstore/
     │    └── multimodel_index.py
     ├── indexes/
     └── data/

## How to Run

### Step 1: Ingestion

    python -m src.pipelines.image_ingest

### Step 2: Retrieval

    python -m src.retriever.image_search

## Key Design Decisions

-   Dual FAISS index for image and text
-   Use of normalized embeddings for cosine similarity
-   Separation of ingestion and retrieval pipelines
-   CPU-friendly models

## Limitations

-   Slow ingestion on CPU
-   Large PDFs may increase processing time
-   No LLM-based answer generation yet


