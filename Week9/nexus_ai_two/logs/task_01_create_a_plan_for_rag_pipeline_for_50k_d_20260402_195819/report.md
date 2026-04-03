# NEXUS AI Report

**Task:** create a plan for rag pipeline for 50k documents

**Generated:** 2026-04-02 19:58:19

---

## RAG Pipeline Design for 50 k Documents  

**Goal** – Build a production‑ready Retrieval‑Augmented Generation system that can ingest, index, and serve 50 k documents (PDFs, HTML, text) with low latency, high accuracy, and cost‑efficiency on Google Cloud Platform (GCP).  

---

### 1. High‑Level Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│  Data Ingestion  │ →   │  Vector Store    │ →   │  Retrieval Service   │
│ (Cloud Storage,  │     │ (FAISS or Pinecone│     │ (Cloud Functions /   │
│  Pub/Sub)        │     │  on GKE)          │     │  Cloud Run)          │
└──────────────────┘     └──────────────────┘     └──────────────────────┘
          ▲                       ▲                        │
          │                       │                        ▼
          │                       │              ┌──────────────────────┐
          │                       │              │  Generation Service  │
          │                       │              │ (Gemini/LLama‑2 on   │
          │                       │              │  Vertex AI / Cloud   │
          │                       │              │  Run)                │
          │                       │              └──────────────────────┘
          │                       │
          ▼                       ▼
┌──────────────────┐     ┌──────────────────┐
│  Monitoring &    │     │  Logging &       │
│  Alerting (Stack│     │  Tracing (Cloud │
│  Driver)         │     │  Logging)        │
└──────────────────┘     └──────────────────┘
```

| Layer | Responsibility | Key Services |
|-------|----------------|--------------|
| **Ingestion** | Ingest raw files, normalize, chunk | Cloud Storage, Cloud Pub/Sub, Cloud Functions |
| **Indexing** | Generate embeddings, store vectors | Vertex AI Feature Store, FAISS on GKE, or managed Pinecone |
| **Retrieval** | Similarity search, dynamic re‑ranking | Cloud Functions, Cloud Run, Redis for caching |
| **Generation** | Prompt‑engineering, LLM inference | Vertex AI Gemini or Llama‑2 on GPU‑enabled Cloud Run |
| **Orchestration** | Workflow management, retries | Cloud Workflows or Airflow on GKE |
| **Observability** | Metrics, logs, alerts | Cloud Monitoring, Cloud Logging, Cloud Trace |
| **Security** | IAM, VPC, KMS | Cloud IAM, Cloud KMS, Private Service Connect |

---

### 2. Vector Store Choice

| Option | Pros | Cons | Recommended |
|--------|------|------|-------------|
| **FAISS (self‑hosted on GKE)** | Full control, no vendor lock‑in, cost‑efficient for 50 k vectors | Requires GPU nodes for large index, maintenance overhead | ✅ For tight cost control |
| **Pinecone** | Managed, autoscaling, high throughput | Per‑node pricing, vendor lock‑in | ⚙️ For quick start / hybrid workloads |
| **Vertex AI Feature Store** | Native to GCP, integrates with Vertex AI pipelines | Limited to dense vectors, scaling limits | ⚙️ If you already use Vertex AI heavily |

**Recommendation** – Use **FAISS on GKE**: 2‑node GPU cluster (A2‑8G or equivalent) gives > 99 % recall for 50 k vectors, with ~$200/month.

---

### 3. Retrieval Strategy

1. **Chunking** – Split each document into 500‑token chunks with 50‑token overlap.  
2. **Embeddings** – Generate dense embeddings using **OpenAI Embeddings v3** (or Cohere/Vertex AI embeddings). 1536‑dim.  
3. **Indexing** – Build FAISS `IVF32 + Flat` index; rebuild nightly or after ingestion.  
4. **Similarity Search** – K‑NN (k=10) + optional **rerank** with BM25 on raw text for hybrid retrieval.  
5. **Caching** – Cache frequent queries in Cloud Memorystore (Redis) to reduce latency.

---

### 4. Generation Model & Deployment

| Model | Hosting Option | Cost (per 1k tokens) | GPU Requirement | Recommendation |
|-------|----------------|----------------------|-----------------|----------------|
| **Gemini Pro** | Vertex AI | ~$0.06 | 8‑bit | ✅ If you have a Vertex AI subscription |
| **Llama‑2 70B** | Cloud Run on GPU (A100) | ~$0.12 | 16‑GB GPU | ⚙️ If you need open‑source or fine‑tuning |
| **Claude 3** | Anthropic API | ~$0.15 | None | ⚙️ For minimal infra overhead |

**Deployment** – Cloud Run with 1‑2 GPU instances, autoscaled by request count. Use **Google Cloud Function** for lightweight prompt generation.

---

### 5. Orchestration & Workflow

| Tool | Use Case | Notes |
|------|----------|-------|
| **Cloud Workflows** | End‑to‑end pipeline (ingestion → indexing → monitoring) | Serverless, event‑driven |
| **Airflow on GKE** | Complex multi‑step pipelines, retries | Requires manual scaling |
| **Kubeflow Pipelines** | ML‑centric pipelines | Good for experimentation |

**Chosen** – **Cloud Workflows** for production simplicity.

---

### 6. Scaling & Concurrency

- **Document ingestion**: Cloud Pub/Sub + Cloud Functions, max 1k messages/s.  
- **Index updates**: Run nightly or incremental. 10 k vectors added per hour → ~50 s indexing on FAISS node.  
- **Retrieval**: Cloud Run with 8 vCPU + 4 GB RAM per instance; autoscale to 5–10 instances under peak load.  
- **Generation**: GPU instances with 8 GB memory, autoscale up to 3 for peak concurrency.  

Use **Cloud Load Balancer** to distribute traffic across Cloud Run services.

---

### 7. Monitoring, Logging & Error Handling

1. **Metrics** – Latency (ingestion, retrieval, generation), error rates, GPU utilization.  
   - Cloud Monitoring dashboards.  
2. **Logging** – Structured logs in Cloud Logging; include request IDs, user IDs, vector IDs.  
3. **Tracing** – Cloud Trace for end‑to‑end request path.  
4. **Alerting** – Thresholds:  
   - Retrieval latency > 200 ms → alert.  
   - Generation error rate > 5 % → alert.  
5. **Retries** – Use Cloud Workflows retry policies; exponential backoff for Pub/Sub messages.

---

### 8. Cost Estimation (Monthly)

| Component | Approx. Cost | Notes |
|-----------|--------------|-------|
| **Storage** – 50 k docs (~100 MB each) | $200 (Coldline) | 5 TB |
| **FAISS GPU nodes** | $250 | 2 nodes, 730 h |
| **Vertex AI Gemini** | $500 | 2 M tokens generated |
| **Cloud Run** | $100 | 10 k requests/day |
| **Pub/Sub & Cloud Functions** | $50 | |
| **Monitoring, Logging** | $30 | |
| **Total** | **≈$1,130** | + 30 % buffer |

---

### 9. Security & Compliance

- **IAM** – Least privilege for service accounts.  
- **VPC** – Private Service Connect to avoid public endpoints.  
- **KMS** – Encrypt embeddings and raw docs.  
- **Data Residency** – Ensure bucket and compute zones comply with regulations (GDPR, HIPAA).  
- **Audit Logs** – Enable Cloud Audit Logging for all services.

---

### 10. Optional Enhancements

| Feature | Benefit | Implementation |
|---------|---------|----------------|
| **Dynamic Re‑ranking** | Improves answer quality | Post‑process retrieval results with a lightweight model |
| **Feedback Loop** | Continual learning | Store user feedback, retrain embeddings quarterly |
| **Versioning** | Track changes to embeddings | Keep snapshot of vector store, use timestamped indices |
| **Multi‑lang Support** | Serve diverse users | Use language‑specific embeddings, add language detection |

---

**Next Steps**

1. Prototype ingestion + chunking pipeline with a