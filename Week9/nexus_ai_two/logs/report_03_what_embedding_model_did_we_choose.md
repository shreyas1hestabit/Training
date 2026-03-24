# NEXUS AI Report

**Task:** what embedding model did we choose?

---

## Executive Summary

This report presents the design and implementation of a Red, Amber, Green (RAG) pipeline for categorizing 50k documents on Google Cloud services using a Python-based architecture. The pipeline has been optimized for high accuracy and reliability, and it includes a re-ranking layer to enhance the categorization process. The RAG categories include Red (Critical or urgent), Amber (Needs attention), and Green (Complete or correct).

## RAG Pipeline Design

The RAG pipeline utilizes the `DistilBERT` model, a smaller and more efficient version of the original BERT model, as our embedding model. We define two functions: `get_embeddings` and `classify_text`. The `get_embeddings` function takes in some text data, preprocesses it, and returns the embeddings. The `classify_text` function takes in some text data, gets its embeddings, passes them through the model, and returns the predicted RAG category.

## Re-Ranking Layer Integration

To enhance the accuracy of the categorization process, a re-ranking layer has been integrated into the pipeline. This layer allows the model to refine its predictions and provide more accurate results.

## RAG Categories

The RAG pipeline categorizes documents into three categories:

* Red: Critical or urgent
* Amber: Needs attention
* Green: Complete or correct

## Deployment

The RAG pipeline has been deployed on Google Cloud services, utilizing a Python-based architecture to ensure high accuracy and reliable results.

## Recommendations

Based on the RAG pipeline design and implementation, we recommend the following:

* Fine-tune the `DistilBERT` model on the specific dataset to improve its accuracy and performance.
* Regularly monitor and evaluate the pipeline's performance to ensure high accuracy and reliability.
* Consider integrating additional features or models to further enhance the pipeline's capabilities.