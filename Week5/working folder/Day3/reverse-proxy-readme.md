## What is a Reverse Proxy?

A reverse proxy is a server that:

- Acts as a **single entry point** for clients
- Receives all incoming requests
- Forwards requests to internal backend services
- Returns responses back to the client

Clients never directly communicate with backend servers.

---

## Why Reverse Proxy is Used

Reverse proxies are used to:

- Hide internal services from direct exposure
- Distribute traffic across multiple backend instances
- Improve scalability and reliability
- Centralize routing and access control

---

## High-Level Architecture

Client requests are routed as follows:

Client --> NGINX (Reverse Proxy) --> Backend Containers

NGINX decides which backend instance should handle each request.

---

## Load Balancing Concept

Multiple backend containers run the same service.

NGINX distributes incoming requests across these containers using **round-robin load balancing**, where each request is forwarded to the next available backend instance in sequence.

This allows the system to handle higher traffic and improves fault tolerance.

---

## Docker Networking Concept

All services run on the same Docker network.

- Each Docker service name acts as a **DNS hostname**
- Containers communicate using **service names and internal ports**
- Host machine ports are irrelevant for container-to-container communication

---

## Container Identity vs Process ID

Each container runs in its own isolated environment.

- Process IDs are container-scoped
- The main process inside a container often has PID = 1

Therefore, process ID cannot be used to verify load balancing.

Instead, container identity (hostname) is used to confirm traffic distribution across replicas.

---

## Project Structure

```bash
|--- docker-compose.yml        # Defines multi-container application
|--- nginx
│   |--- nginx.conf            # Reverse proxy configuration
|--- server
    |--- Dockerfile            # Backend service image definition
    |--- index.js              # Backend application entry point
```

---

## Request Flow Explanation

1. Client sends a request to the exposed NGINX port
2. NGINX receives the request as the single entry point
3. NGINX forwards the request to one backend container
4. Docker networking resolves the backend service name
5. Backend processes the request and sends response back
6. NGINX returns the response to the client

This entire flow is transparent to the client.

---

## Architectural Learnings

- Reverse proxies abstract backend complexity
- NGINX handles routing and traffic distribution
- Docker provides service discovery through internal DNS
- Load balancing is independent of application logic

---

## Real-World Usecase

This architecture is commonly used in:

- Microservices-based systems
- API gateways
- Cloud-native applications
- High-traffic backend platforms

---

## OUTPUT

![ot](./screenshots/working.png)
