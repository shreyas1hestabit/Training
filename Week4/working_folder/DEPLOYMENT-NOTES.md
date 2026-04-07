# DEPLOYMENT-NOTES.md

This document explains the deployment-related decisions, architecture choices, and production readiness measures implemented in the backend project.

---

## 1. Environment Configuration Strategy

The project uses environment-based configuration to separate **code from configuration**.

### Why this was done

- To avoid hardcoding secrets (DB URLs, ports, Redis config)
- To support different environments (local, staging, production)
- To make the project deployable on any system without code changes

### How it works

- `.env.example` acts as **documentation**
- `.env.local` / `.env.production` contains **real values**
- The application reads configuration at startup

This ensures:

- Secure handling of credentials
- Production-safe deployments

---

## 2. Redis & Background Job Architecture

The application implements **asynchronous background processing** using a job queue.

### Why background jobs were needed

Some tasks should not block the API response, such as:

- Sending emails
- Generating reports
- Long-running operations

Blocking APIs reduce performance and user experience.

---

### Job Queue Design

The architecture is split into:

- **Producer**: Adds jobs to a queue
- **Worker**: Processes jobs independently

This separation ensures:

- Faster API responses
- Better scalability

Redis is used as a message broker to coordinate jobs between producers and workers.

---

## 3. Worker Process Design

The worker runs as a **separate process** from the main server.

### Why this design is important

- Failure in job processing does not crash the API
- Jobs can retry automatically on failure
- Heavy tasks do not consume API resources

This reflects real-world production systems where background processing is isolated from request handling.

---

## 4. Process Management with PM2

PM2 is used as a **process manager** for production readiness.

### Why PM2 was introduced

- To keep the server running even if it crashes
- To manage restarts automatically
- To provide centralized logging
- To simulate real production environments

---

### PM2 Logs Location

PM2 stores logs **outside the project directory**.

### Why this is correct behavior

- Prevents accidental deletion during deployments
- Keeps logs independent of codebase

---

## 5. Structured Logging & Observability

The project implements structured logging using Winston.

### Benefits

- Centralized logging across the application
- Logs written to both console and files
- Clear separation between application logic and logging

---

### Request Tracing

Each request is assigned a unique **Request ID**.

### Why request tracing matters

- Helps debug issues across multiple layers
- Allows grouping logs belonging to the same request

---

## 6. API Documentation Strategy

Instead of hardcoded documentation, the project uses **Postman collections**.

### Why this approach was chosen

- Easier collaboration with frontend teams
- Environment-based variable handling
- Real request/response examples
- Can be shared and imported easily

This ensures APIs are:

- Testable
- Reusable
- Self-documented

---

## 7. Production Folder (`prod/`) Purpose

The `prod/` folder represents **deployment-specific artifacts**.

### Why it exists

- Keeps deployment configs separate from application logic
- Contains PM2 configuration and environment references
- Prepares the project for server or cloud deployment

This separation improves maintainability and clarity.

---

## 8. Security & Stability Considerations

The deployment setup assumes:

- Secure environment variable handling
- Isolated worker processes
- Controlled request flow via background jobs
- Observability through logs and tracing

these ensure:

- Stability under load
- Easier debugging
- Production-safe behavior
